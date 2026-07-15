#!/usr/bin/env python3
"""Static validation for the repository-native fsm-spec/v1 semantic contract."""

from __future__ import annotations

import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


INVALID_MODES = {"ignore", "reject", "reject-and-audit", "error", "defer"}
STATE_KINDS = {"atomic", "final"}


def is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_text_list(value: Any, *, allow_empty: bool = False) -> bool:
    return isinstance(value, list) and (allow_empty or bool(value)) and all(is_text(item) for item in value)


def binding_source_type(
    value: Any, event_types: dict[str, str], context_types: dict[str, str]
) -> str | None:
    """Resolve the declared type of a binding expression."""
    if not is_text(value):
        return None
    if value.startswith("literal:"):
        return "string" if value.removeprefix("literal:") else None
    if value.startswith("event."):
        field = value.removeprefix("event.")
        return "string" if field == "type" else event_types.get(field)
    if value.startswith("context."):
        return context_types.get(value.removeprefix("context."))
    if value in {"configuration.state", "rejection.reason"}:
        return "string"
    return None


def payload_field_types(contract: Any) -> dict[str, str]:
    if not isinstance(contract, dict):
        return {}
    properties = contract.get("payload_schema", {}).get("properties", {})
    if not isinstance(properties, dict):
        return {}
    return {
        field: schema["type"]
        for field, schema in properties.items()
        if isinstance(field, str) and isinstance(schema, dict) and is_text(schema.get("type"))
    }


def eventless_cycles(nodes: set[str], edges: dict[str, set[str]]) -> list[list[str]]:
    """Return strongly connected eventless components, including self-loops."""
    index = 0
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    cycles: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in edges.get(node, set()):
            if target not in indices:
                visit(target)
                low[node] = min(low[node], low[target])
            elif target in on_stack:
                low[node] = min(low[node], indices[target])
        if low[node] == indices[node]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1 or node in edges.get(node, set()):
                cycles.append(sorted(component))

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return cycles


def validate_machine(
    machine: Any,
    prefix: str,
    event_catalog: set[str],
    guard_contracts: dict[str, Any],
    effect_contracts: dict[str, Any],
    event_required: dict[str, set[str]],
    context_fields: set[str],
    context_types: dict[str, str],
    context_roles: dict[str, str],
    event_field_types: dict[str, dict[str, str]],
    event_field_roles: dict[str, dict[str, str]],
) -> tuple[list[str], list[str], set[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    used_events: set[str] = set()
    guard_catalog = set(guard_contracts)
    effect_catalog = set(effect_contracts)
    if not isinstance(machine, dict):
        return [f"{prefix} must be an object"], warnings, used_events

    if not is_text(machine.get("id")):
        errors.append(f"{prefix}.id must be a non-empty string")
    raw_states = machine.get("states")
    if not isinstance(raw_states, list) or not raw_states:
        return errors + [f"{prefix}.states must be a non-empty list"], warnings, used_events

    state_kinds: dict[str, str] = {}
    for index, state in enumerate(raw_states):
        where = f"{prefix}.states[{index}]"
        if not isinstance(state, dict):
            errors.append(f"{where} must be an object")
            continue
        state_id = state.get("id")
        kind = state.get("kind", "atomic")
        if not is_text(state_id):
            errors.append(f"{where}.id must be a non-empty string")
            continue
        if state_id in state_kinds:
            errors.append(f"{prefix}: duplicate state id {state_id!r}")
        if kind not in STATE_KINDS:
            errors.append(f"{where}.kind must be one of {sorted(STATE_KINDS)}")
        state_kinds[state_id] = kind

    initial = machine.get("initial")
    if initial not in state_kinds:
        errors.append(f"{prefix}.initial references unknown state {initial!r}")
    events = machine.get("events")
    if not is_text_list(events):
        errors.append(f"{prefix}.events must be a non-empty list of strings")
        event_set: set[str] = set()
    else:
        event_set = set(events)
        used_events |= event_set
        if len(event_set) != len(events):
            errors.append(f"{prefix}.events contains duplicates")
        for event in sorted(event_set - event_catalog):
            errors.append(f"{prefix}.events references event without payload schema: {event!r}")

    policy = machine.get("invalid_event_policy")
    if not isinstance(policy, dict):
        errors.append(f"{prefix}.invalid_event_policy must be an object")
    else:
        mode = policy.get("mode")
        guard_false = policy.get("guard_false")
        if mode not in INVALID_MODES:
            errors.append(f"{prefix}.invalid_event_policy.mode must be one of {sorted(INVALID_MODES)}")
        if guard_false not in INVALID_MODES:
            errors.append(f"{prefix}.invalid_event_policy.guard_false must be one of {sorted(INVALID_MODES)}")
        if policy.get("state_change") != "none":
            errors.append(f"{prefix}.invalid_event_policy.state_change must be 'none'")
        if mode == "reject-and-audit" or guard_false == "reject-and-audit":
            audit_effect = policy.get("effect")
            if audit_effect not in effect_catalog:
                errors.append(f"{prefix}.invalid_event_policy.effect must name a declared audit effect")
            elif not isinstance(effect_contracts[audit_effect], dict) or effect_contracts[audit_effect].get("kind") != "audit":
                errors.append(f"{prefix}.invalid_event_policy.effect must have kind 'audit'")
            else:
                required = set(effect_contracts[audit_effect].get("payload_schema", {}).get("required", []))
                binding = policy.get("effect_binding")
                if not isinstance(binding, dict) or not required.issubset(binding) or any(
                    not is_text(value) for value in binding.values()
                ):
                    errors.append(f"{prefix}.invalid_event_policy.effect_binding must bind every audit payload field")
                elif event_set:
                    common_event_fields = set.intersection(
                        *(event_required.get(event, set()) for event in event_set)
                    )
                    common_event_types = {
                        field: next(iter(field_types))
                        for field in common_event_fields
                        if len(field_types := {
                            event_field_types.get(event, {}).get(field) for event in event_set
                        }) == 1 and None not in field_types
                    }
                    target_types = payload_field_types(effect_contracts[audit_effect])
                    for field, source in binding.items():
                        source_type = binding_source_type(source, common_event_types, context_types)
                        if source_type is None:
                            errors.append(
                                f"{prefix}.invalid_event_policy.effect_binding.{field} "
                                f"references unavailable source {source!r}"
                            )
                        elif field in target_types and source_type != target_types[field]:
                            errors.append(
                                f"{prefix}.invalid_event_policy.effect_binding.{field} has type "
                                f"{source_type!r}, expected {target_types[field]!r}"
                            )

    transitions = machine.get("transitions")
    if not isinstance(transitions, list):
        errors.append(f"{prefix}.transitions must be a list")
        return errors, warnings, used_events

    graph: dict[str, set[str]] = defaultdict(set)
    always_graph: dict[str, set[str]] = defaultdict(set)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    transition_ids: set[str] = set()
    for index, transition in enumerate(transitions):
        where = f"{prefix}.transitions[{index}]"
        if not isinstance(transition, dict):
            errors.append(f"{where} must be an object")
            continue
        transition_id = transition.get("id")
        source = transition.get("from")
        target = transition.get("to")
        event = transition.get("event")
        if not is_text(transition_id):
            errors.append(f"{where}.id must be a non-empty string")
        elif transition_id in transition_ids:
            errors.append(f"{prefix}: duplicate transition id {transition_id!r}")
        else:
            transition_ids.add(transition_id)
        if source not in state_kinds:
            errors.append(f"{where}.from references unknown state {source!r}")
        if target not in state_kinds:
            errors.append(f"{where}.to references unknown state {target!r}")
        if event != "@always" and event not in event_set:
            errors.append(f"{where}.event references undeclared machine event {event!r}")
        if source in state_kinds and state_kinds[source] == "final":
            errors.append(f"{where}: final state {source!r} must have no outgoing transition")
        guard = transition.get("guard")
        if event == "TIMEOUT" and guard is None:
            errors.append(f"{where}: TIMEOUT transitions require a declared guard")
        if guard is not None and guard not in guard_catalog:
            errors.append(f"{where}.guard references undeclared guard {guard!r}")
        elif guard is not None:
            guard_contract = guard_contracts[guard]
            event_reads = guard_contract.get("event_reads", []) if isinstance(guard_contract, dict) else []
            if not is_text_list(event_reads, allow_empty=True):
                errors.append(f"guards.{guard}.event_reads must be a list of non-empty strings")
            else:
                missing = set(event_reads) - event_required.get(event, set())
                if missing:
                    errors.append(f"{where}.guard requires event fields absent from {event!r}: {sorted(missing)}")
            if event == "TIMEOUT" and isinstance(guard_contract, dict):
                deadline_field = guard_contract.get("deadline_context_field")
                observed_field = guard_contract.get("observed_event_field")
                reads = guard_contract.get("reads", [])
                if guard_contract.get("kind") != "deadline":
                    errors.append(f"{where}.guard must declare kind 'deadline' for TIMEOUT")
                if not is_text(deadline_field) or deadline_field not in reads:
                    errors.append(f"{where}.guard must bind deadline_context_field through reads")
                if not is_text(observed_field) or observed_field not in event_reads:
                    errors.append(f"{where}.guard must bind observed_event_field through event_reads")
                if is_text(deadline_field) and context_types.get(deadline_field) != "timestamp":
                    errors.append(f"{where}.guard deadline_context_field must reference timestamp context")
                if is_text(observed_field) and event_field_types.get(event, {}).get(observed_field) != "timestamp":
                    errors.append(f"{where}.guard observed_event_field must reference timestamp event payload")
                if is_text(deadline_field) and context_roles.get(deadline_field) != "deadline":
                    errors.append(f"{where}.guard deadline_context_field must have role 'deadline'")
                if is_text(observed_field) and event_field_roles.get(event, {}).get(observed_field) != "observation_time":
                    errors.append(f"{where}.guard observed_event_field must have role 'observation_time'")
        effects = transition.get("effects", [])
        if not is_text_list(effects, allow_empty=True):
            errors.append(f"{where}.effects must be a list of non-empty strings")
        else:
            for effect in sorted(set(effects) - effect_catalog):
                errors.append(f"{where}.effects references undeclared effect {effect!r}")
            bindings = transition.get("effect_bindings", {})
            if effects and not isinstance(bindings, dict):
                errors.append(f"{where}.effect_bindings must be an object")
            elif isinstance(bindings, dict):
                for effect in effects:
                    if effect not in effect_contracts:
                        continue
                    effect_contract = effect_contracts[effect]
                    required = set(effect_contract.get("payload_schema", {}).get("required", [])) if isinstance(effect_contract, dict) else set()
                    effect_binding = bindings.get(effect)
                    if not isinstance(effect_binding, dict) or not required.issubset(effect_binding) or any(
                        not is_text(value) for value in effect_binding.values()
                    ):
                        errors.append(f"{where}.effect_bindings.{effect} must bind every required payload field")
                    elif isinstance(event, str):
                        target_types = payload_field_types(effect_contract)
                        for field, binding_source in effect_binding.items():
                            source_type = binding_source_type(
                                binding_source, event_field_types.get(event, {}), context_types
                            )
                            if source_type is None:
                                errors.append(
                                    f"{where}.effect_bindings.{effect}.{field} "
                                    f"references unavailable source {binding_source!r}"
                                )
                            elif field in target_types and source_type != target_types[field]:
                                errors.append(
                                    f"{where}.effect_bindings.{effect}.{field} has type "
                                    f"{source_type!r}, expected {target_types[field]!r}"
                                )
        if source in state_kinds and target in state_kinds:
            graph[source].add(target)
            if event == "@always":
                always_graph[source].add(target)
        if isinstance(source, str) and isinstance(event, str):
            groups[(source, event)].append(transition)

    for (source, event), choices in sorted(groups.items()):
        if len(choices) < 2:
            continue
        priorities = [item.get("priority") for item in choices]
        if any(not isinstance(value, int) or isinstance(value, bool) for value in priorities):
            errors.append(f"{prefix}: competing {source!r}/{event!r} transitions require integer priorities")
        elif len(set(priorities)) != len(priorities):
            errors.append(f"{prefix}: competing {source!r}/{event!r} transitions have duplicate priorities")
        guards = [item.get("guard", "@default") for item in choices]
        if len(set(guards)) != len(guards):
            errors.append(f"{prefix}: competing {source!r}/{event!r} transitions duplicate a guard/default")
        if "@default" not in guards:
            warnings.append(f"{prefix}: competing {source!r}/{event!r} transitions have no explicit default")

    if initial in state_kinds:
        reachable = {initial}
        queue = deque([initial])
        while queue:
            source = queue.popleft()
            for target in graph.get(source, set()):
                if target not in reachable:
                    reachable.add(target)
                    queue.append(target)
        for state_id in sorted(set(state_kinds) - reachable):
            warnings.append(f"{prefix}: state {state_id!r} is unreachable from {initial!r}")
    for cycle in eventless_cycles(set(state_kinds), always_graph):
        errors.append(f"{prefix}: eventless cycle can prevent macrostep termination: {cycle}")
    if not any(kind == "final" for kind in state_kinds.values()):
        warnings.append(f"{prefix}: no final state is declared; document why the machine is intentionally perpetual")
    return errors, warnings, used_events


def validate(spec: Any) -> tuple[list[str], list[str]]:
    if not isinstance(spec, dict):
        return ["root must be a JSON object"], []
    errors: list[str] = []
    warnings: list[str] = []
    if spec.get("schema_version") != "fsm-spec/v1":
        errors.append("schema_version must be 'fsm-spec/v1'")

    execution = spec.get("execution")
    if not isinstance(execution, dict):
        errors.append("execution must be an object")
    else:
        for key in ("step_interface", "event_queue", "run_to_completion", "action_order"):
            if not is_text(execution.get(key)):
                errors.append(f"execution.{key} must be a non-empty string")

    context = spec.get("context_schema")
    if not isinstance(context, dict):
        errors.append("context_schema must be an object")
        context_fields: set[str] = set()
        context_types: dict[str, str] = {}
        context_roles: dict[str, str] = {}
    else:
        context_fields = set(context)
        context_types = {}
        context_roles = {}
        for key, value in context.items():
            if not is_text(key) or not isinstance(value, dict) or not is_text(value.get("type")):
                errors.append(f"context_schema.{key} must define an object with a non-empty type")
            else:
                context_types[key] = value["type"]
                if is_text(value.get("role")):
                    context_roles[key] = value["role"]

    event_schemas = spec.get("event_schemas")
    if not isinstance(event_schemas, dict) or not event_schemas:
        errors.append("event_schemas must be a non-empty object")
        event_catalog: set[str] = set()
    else:
        event_catalog = set(event_schemas)
        event_required: dict[str, set[str]] = {}
        event_field_types: dict[str, dict[str, str]] = {}
        event_field_roles: dict[str, dict[str, str]] = {}
        for name, schema in event_schemas.items():
            if not is_text(name) or not isinstance(schema, dict) or schema.get("type") != "object":
                errors.append(f"event_schemas.{name}.type must be 'object'")
                event_required[name] = set()
                event_field_types[name] = {}
                event_field_roles[name] = {}
                continue
            required = schema.get("required")
            if not is_text_list(required):
                errors.append(f"event_schemas.{name}.required must be a non-empty list")
                event_required[name] = set()
            else:
                event_required[name] = set(required)
            properties = schema.get("properties")
            if not isinstance(properties, dict):
                errors.append(f"event_schemas.{name}.properties must be an object")
                event_field_types[name] = {}
                event_field_roles[name] = {}
            else:
                event_field_types[name] = {}
                event_field_roles[name] = {}
                for field, field_schema in properties.items():
                    if not is_text(field) or not isinstance(field_schema, dict) or not is_text(field_schema.get("type")):
                        errors.append(f"event_schemas.{name}.properties.{field} must declare a non-empty type")
                    else:
                        event_field_types[name][field] = field_schema["type"]
                        if is_text(field_schema.get("role")):
                            event_field_roles[name][field] = field_schema["role"]
                missing_properties = event_required[name] - set(event_field_types[name])
                if missing_properties:
                    errors.append(
                        f"event_schemas.{name}.properties missing required fields: {sorted(missing_properties)}"
                    )
    if not isinstance(event_schemas, dict) or not event_schemas:
        event_required = {}
        event_field_types = {}
        event_field_roles = {}

    guards = spec.get("guards")
    if not isinstance(guards, dict):
        errors.append("guards must be an object")
        guard_catalog: set[str] = set()
    else:
        guard_catalog = set(guards)
        for name, contract in guards.items():
            if not isinstance(contract, dict):
                errors.append(f"guards.{name} must be an object")
                continue
            if contract.get("pure") is not True or contract.get("synchronous") is not True:
                errors.append(f"guards.{name} must set pure and synchronous to true")
            reads = contract.get("reads")
            if not is_text_list(reads, allow_empty=True):
                errors.append(f"guards.{name}.reads must be a list of non-empty strings")
            else:
                for field in sorted(set(reads) - context_fields):
                    errors.append(f"guards.{name}.reads references missing context field {field!r}")
            if not is_text_list(contract.get("event_reads", []), allow_empty=True):
                errors.append(f"guards.{name}.event_reads must be a list of non-empty strings")

    effects = spec.get("effects")
    if not isinstance(effects, dict) or not effects:
        errors.append("effects must be a non-empty object")
        effect_catalog: set[str] = set()
    else:
        effect_catalog = set(effects)
        for name, contract in effects.items():
            if not isinstance(contract, dict) or contract.get("kind") not in {"command", "audit"}:
                errors.append(f"effects.{name} must define kind command or audit")
                continue
            payload = contract.get("payload_schema")
            if not isinstance(payload, dict) or payload.get("type") != "object":
                errors.append(f"effects.{name}.payload_schema.type must be 'object'")
                continue
            required = payload.get("required")
            if not is_text_list(required):
                errors.append(f"effects.{name}.payload_schema.required must be a non-empty list")
                continue
            properties = payload.get("properties")
            if not isinstance(properties, dict):
                errors.append(f"effects.{name}.payload_schema.properties must be an object")
                continue
            typed_properties = {
                field for field, schema in properties.items()
                if is_text(field) and isinstance(schema, dict) and is_text(schema.get("type"))
            }
            missing_properties = set(required) - typed_properties
            if missing_properties:
                errors.append(
                    f"effects.{name}.payload_schema.properties missing required fields: "
                    f"{sorted(missing_properties)}"
                )

    for key in ("safety_properties", "liveness_properties"):
        properties = spec.get(key)
        if not isinstance(properties, list) or not properties:
            errors.append(f"{key} must be a non-empty list")
            continue
        for index, prop in enumerate(properties):
            if not isinstance(prop, dict):
                errors.append(f"{key}[{index}] must be an object")
                continue
            for field in ("id", "statement", "verification"):
                if not is_text(prop.get(field)):
                    errors.append(f"{key}[{index}].{field} must be a non-empty string")
            if key == "liveness_properties" and not is_text_list(prop.get("assumptions")):
                errors.append(f"{key}[{index}].assumptions must be a non-empty list")

    machines = spec.get("machines")
    if not isinstance(machines, list) or not machines:
        return errors + ["machines must be a non-empty list"], warnings
    machine_ids: set[str] = set()
    used_events: set[str] = set()
    for index, machine in enumerate(machines):
        sub_errors, sub_warnings, machine_events = validate_machine(
            machine, f"machines[{index}]", event_catalog, guards if isinstance(guards, dict) else {},
            effects if isinstance(effects, dict) else {}, event_required, context_fields,
            context_types, context_roles, event_field_types, event_field_roles
        )
        errors.extend(sub_errors)
        warnings.extend(sub_warnings)
        used_events |= machine_events
        if isinstance(machine, dict) and isinstance(machine.get("id"), str):
            if machine["id"] in machine_ids:
                errors.append(f"duplicate machine id {machine['id']!r}")
            machine_ids.add(machine["id"])
    for event in sorted(event_catalog - used_events):
        warnings.append(f"event schema {event!r} is not used by any machine")

    if len(machines) > 1:
        coordination = spec.get("coordination")
        if not isinstance(coordination, dict):
            errors.append("multiple machines require a coordination object")
        else:
            for key in ("event_protocol", "global_invariants"):
                if not coordination.get(key):
                    errors.append(f"coordination.{key} must be non-empty")

    if not is_text_list(spec.get("trace_fixtures")):
        errors.append("trace_fixtures must be a non-empty list")
    conformance = spec.get("conformance")
    if not isinstance(conformance, dict):
        errors.append("conformance must be an object")
    else:
        for key in ("implementation_step", "model_trace_runner", "contract_tests"):
            if not is_text(conformance.get(key)):
                errors.append(f"conformance.{key} must be a non-empty string")

    liveness_text = " ".join(
        [prop.get("statement", "") + " " + " ".join(prop.get("assumptions", []))
         for prop in spec.get("liveness_properties", []) if isinstance(prop, dict)]
    ).upper()
    transition_events = {
        transition.get("event")
        for machine in machines if isinstance(machine, dict)
        for transition in machine.get("transitions", []) if isinstance(transition, dict)
    }
    if "TIMEOUT" in liveness_text and "TIMEOUT" not in transition_events:
        errors.append("liveness mentions TIMEOUT but no TIMEOUT transition exists")
    return errors, warnings


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} FSM_SPEC.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR {path}: {error}", file=sys.stderr)
        return 2
    errors, warnings = validate(spec)
    for item in warnings:
        print(f"WARN  {item}")
    for item in errors:
        print(f"ERROR {item}")
    if errors:
        print(f"FAIL  {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK    {path}: {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
