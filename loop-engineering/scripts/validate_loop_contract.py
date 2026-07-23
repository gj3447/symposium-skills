#!/usr/bin/env python3
"""Validate a production control contract for a bounded agent loop."""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


TIERS = {"L_IDE", "L_RT", "L_MC"}
REQUIRED_TERMINAL_CATEGORIES = {
    "success", "permanent_failure", "retry_exhausted", "budget_exhausted", "timeout", "canceled"
}
ALLOWED_TERMINAL_CATEGORIES = REQUIRED_TERMINAL_CATEGORIES | {
    "pathology", "saturated", "external_blocked", "human_declined", "unknown_effect"
}
REQUIRED_BUDGETS = {
    "max_steps", "max_tool_calls", "max_retries_per_transition", "max_wall_seconds",
    "max_suspended_seconds", "max_tokens", "max_cost", "max_recursion_depth", "max_parallelism"
}
TRACE_FIELDS = {
    "run_id", "cycle_id", "workflow_version", "state_schema_version", "transition_id",
    "source_state", "target_state", "trigger", "actor", "evidence_hashes", "budget_delta",
    "timestamp", "trace_id", "span_id", "checkpoint_id"
}
APPROVAL_FIELDS = {
    "run_id", "workflow_version", "action_hash", "artifact_hash", "destination_hash",
    "visibility", "scope", "actor", "expiry", "nonce", "rationale"
}
COMMANDERS = {"Prometheus", "Longinus", "Eureka", "Occam", "Naesengmoon", "JaebaeMan", "Harness=Hades"}
ACTION_EFFECT_CLASSES = {"read_only", "reversible", "idempotent_external", "high_risk_external"}
HIGH_RISK_EFFECT_CLASSES = {"high_risk_external"}
INTERRUPT_TERMINAL_CATEGORIES = {
    "CANCEL": "canceled",
    "TIMEOUT": "timeout",
    "BUDGET_EXHAUSTED": "budget_exhausted",
}


def is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_text_list(value: Any, *, allow_empty: bool = False) -> bool:
    return isinstance(value, list) and (allow_empty or bool(value)) and all(is_text(item) for item in value)


def positive_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and value > 0
    )


def require_object(spec: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = spec.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return {}
    return value


def validate(spec: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(spec, dict):
        return ["root must be a JSON object"], warnings
    if spec.get("schema_version") != "loop-contract/v1":
        errors.append("schema_version must be 'loop-contract/v1'")
    for key in ("name", "workflow_version", "state_schema_version"):
        if not is_text(spec.get(key)):
            errors.append(f"{key} must be a non-empty string")
    if spec.get("tier") not in TIERS:
        errors.append(f"tier must be one of {sorted(TIERS)}")

    owner = require_object(spec, "control_owner", errors)
    for key in ("continuation", "budgets", "authorization", "success_verdict", "checkpoint", "effects"):
        if not is_text(owner.get(key)):
            errors.append(f"control_owner.{key} must be a non-empty string")

    states = spec.get("states")
    if not is_text_list(states):
        errors.append("states must be a non-empty list of strings")
        state_set: set[str] = set()
    else:
        state_set = set(states)
        if len(state_set) != len(states):
            errors.append("states contains duplicates")
    initial = spec.get("initial")
    if initial not in state_set:
        errors.append(f"initial references unknown state {initial!r}")

    terminal = spec.get("terminal_states")
    if not isinstance(terminal, dict):
        errors.append("terminal_states must map state names to typed categories")
        terminal = {}
    else:
        for state in sorted(set(terminal) - state_set):
            errors.append(f"terminal state {state!r} is not declared in states")
        categories = set(terminal.values())
        missing = REQUIRED_TERMINAL_CATEGORIES - categories
        if missing:
            errors.append(f"terminal_states missing required categories: {sorted(missing)}")
        invalid = categories - ALLOWED_TERMINAL_CATEGORIES
        if invalid:
            errors.append(f"terminal_states has invalid categories: {sorted(invalid)}")
        if terminal.get("WAIT_HUMAN"):
            errors.append("WAIT_HUMAN is suspended and must not be terminal")

    actions = spec.get("action_types")
    if not isinstance(actions, dict) or not actions:
        errors.append("action_types must be a non-empty object")
        actions = {}
    required_critical_states: set[str] = set()
    for name, action in actions.items():
        if not isinstance(action, dict):
            errors.append(f"action_types.{name} must be an object")
            continue
        effect_class = action.get("effect_class")
        if not is_text(action.get("risk")) or not isinstance(action.get("approval_required"), bool):
            errors.append(f"action_types.{name} must define risk and approval_required")
        if effect_class not in ACTION_EFFECT_CLASSES:
            errors.append(f"action_types.{name}.effect_class must be one of {sorted(ACTION_EFFECT_CLASSES)}")
        if effect_class in HIGH_RISK_EFFECT_CLASSES and action.get("approval_required") is not True:
            errors.append(f"action_types.{name}: high-risk external effects require approval_required=true")
        if effect_class in HIGH_RISK_EFFECT_CLASSES:
            for key in ("approval_state", "authorization_state", "reconciliation_state", "unknown_outcome_state", "post_reconciliation_state"):
                if action.get(key) not in state_set:
                    errors.append(f"action_types.{name}.{key} must reference a declared state")

    transitions = spec.get("transitions")
    graph: dict[str, set[str]] = defaultdict(set)
    transition_ids: set[str] = set()
    transition_pairs: set[tuple[str, str]] = set()
    action_uses: dict[str, list[dict[str, Any]]] = defaultdict(list)
    transition_items: list[Any] = transitions if isinstance(transitions, list) else []
    if not isinstance(transitions, list) or not transitions:
        errors.append("transitions must be a non-empty list")
    else:
        for index, transition in enumerate(transition_items):
            where = f"transitions[{index}]"
            if not isinstance(transition, dict):
                errors.append(f"{where} must be an object")
                continue
            transition_id = transition.get("id")
            source = transition.get("from")
            target = transition.get("to")
            event = transition.get("event")
            if not is_text(transition_id):
                errors.append(f"{where}.id must be non-empty")
            elif transition_id in transition_ids:
                errors.append(f"duplicate transition id {transition_id!r}")
            else:
                transition_ids.add(transition_id)
            if source not in state_set:
                errors.append(f"{where}.from references unknown state {source!r}")
            if target not in state_set:
                errors.append(f"{where}.to references unknown state {target!r}")
            if source in terminal:
                errors.append(f"{where}: terminal state {source!r} must have no outgoing transition")
            for key in ("event", "actor", "evidence"):
                if not is_text(transition.get(key)):
                    errors.append(f"{where}.{key} must be a non-empty string")
            if isinstance(source, str) and isinstance(event, str):
                pair = (source, event)
                if pair in transition_pairs:
                    errors.append(f"ambiguous duplicate transition for {source!r}/{event!r}")
                transition_pairs.add(pair)
            action_name = transition.get("action")
            if action_name is not None:
                if action_name not in actions:
                    errors.append(f"{where}.action references unknown action {action_name!r}")
                else:
                    action_uses[action_name].append(transition)
            if source in state_set and target in state_set:
                graph[source].add(target)

    for name, action in actions.items():
        if not isinstance(action, dict) or action.get("effect_class") not in HIGH_RISK_EFFECT_CLASSES:
            continue
        approval_state = action.get("approval_state")
        authorization_state = action.get("authorization_state")
        reconciliation_state = action.get("reconciliation_state")
        unknown_outcome_state = action.get("unknown_outcome_state")
        post_reconciliation_state = action.get("post_reconciliation_state")
        incoming_authorization = [
            t for t in transition_items
            if isinstance(t, dict) and t.get("to") == authorization_state
        ]
        if not incoming_authorization or any(
            t.get("from") != approval_state or t.get("event") != "APPROVED"
            for t in incoming_authorization
        ):
            errors.append(f"high-risk action {name!r} lacks APPROVED path from approval_state to authorization_state")
        for use in action_uses.get(name, []):
            if use.get("from") != authorization_state:
                errors.append(f"high-risk action {name!r} is used outside its authorization_state")
        if not action_uses.get(name):
            errors.append(f"high-risk action {name!r} is never used by a transition")
        execution_states = {
            use.get("to") for use in action_uses.get(name, []) if isinstance(use.get("to"), str)
        }
        role_states = {
            approval_state,
            authorization_state,
            reconciliation_state,
            unknown_outcome_state,
            post_reconciliation_state,
        }
        if len(role_states) != 5:
            errors.append(f"high-risk action {name!r} must use five distinct control states")
        invalid_execution_states = execution_states & (role_states | set(terminal))
        if invalid_execution_states:
            errors.append(
                f"high-risk action {name!r} execution states overlap control/terminal states: "
                f"{sorted(invalid_execution_states)}"
            )
        action_critical_states = {
            state for state in (
                authorization_state,
                reconciliation_state,
                unknown_outcome_state,
                post_reconciliation_state,
                *execution_states,
            )
            if isinstance(state, str)
        }
        required_critical_states.update(action_critical_states)
        if not any(
            t.get("from") == reconciliation_state
            and t.get("event") == "OUTCOME_UNKNOWN"
            and t.get("to") == unknown_outcome_state
            for t in transition_items
            if isinstance(t, dict)
        ):
            errors.append(f"high-risk action {name!r} lacks bound OUTCOME_UNKNOWN reconciliation path")
        for source in (reconciliation_state, unknown_outcome_state):
            if not any(
                t.get("from") == source
                and t.get("event") == "RECEIPT_CONFIRMED"
                and t.get("to") == post_reconciliation_state
                for t in transition_items
                if isinstance(t, dict)
            ):
                errors.append(f"high-risk action {name!r} lacks receipt path through post_reconciliation_state")
        pending_outcomes = {
            "NO_PENDING_INTERRUPT_SUCCESS": "success",
            "NO_PENDING_INTERRUPT_FAILURE": "permanent_failure",
            "PENDING_CANCEL": "canceled",
            "PENDING_TIMEOUT": "timeout",
            "PENDING_BUDGET_EXHAUSTED": "budget_exhausted",
        }
        for event, category in pending_outcomes.items():
            if not any(
                t.get("from") == post_reconciliation_state
                and t.get("event") == event
                and terminal.get(t.get("to")) == category
                for t in transition_items
                if isinstance(t, dict)
            ):
                errors.append(f"high-risk action {name!r} lacks post-reconciliation {event} path")
        for transition in transition_items:
            if not isinstance(transition, dict):
                continue
            source = transition.get("from")
            target = transition.get("to")
            event = transition.get("event")
            if source in (action_critical_states - {post_reconciliation_state}) and target not in action_critical_states:
                errors.append(
                    f"high-risk action {name!r} exits effect-critical path before post_reconciliation_state "
                    f"via transition {transition.get('id')!r}"
                )
            if source == authorization_state and (
                transition.get("action") != name or target not in execution_states
            ):
                errors.append(
                    f"high-risk action {name!r} must move from authorization to an execution state "
                    f"through its action transition; invalid {transition.get('id')!r}"
                )
            if source in execution_states and target not in (execution_states | {reconciliation_state}):
                errors.append(
                    f"high-risk action {name!r} execution must proceed to reconciliation; "
                    f"invalid {transition.get('id')!r}"
                )
            if source == reconciliation_state and (event, target) not in {
                ("RECEIPT_CONFIRMED", post_reconciliation_state),
                ("OUTCOME_UNKNOWN", unknown_outcome_state),
            }:
                errors.append(
                    f"high-risk action {name!r} has invalid reconciliation transition "
                    f"{transition.get('id')!r}"
                )
            if source == unknown_outcome_state and (event, target) not in {
                ("RECEIPT_CONFIRMED", post_reconciliation_state),
                ("ABANDON", post_reconciliation_state),
            }:
                errors.append(
                    f"high-risk action {name!r} has invalid unknown-outcome transition "
                    f"{transition.get('id')!r}"
                )
            if target == post_reconciliation_state and source not in {
                reconciliation_state, unknown_outcome_state
            }:
                errors.append(
                    f"high-risk action {name!r} post_reconciliation_state has invalid incoming "
                    f"transition {transition.get('id')!r}"
                )
            if source == post_reconciliation_state and (
                event not in pending_outcomes or terminal.get(target) != pending_outcomes.get(event)
            ):
                errors.append(
                    f"high-risk action {name!r} has invalid post-reconciliation exit "
                    f"via transition {transition.get('id')!r}"
                )

    global_interrupts = spec.get("global_interrupts")
    interrupt_targets: dict[str, str] = {}
    seen_interrupts: set[str] = set()
    critical_states_raw = spec.get("effects", {}).get("effect_critical_states", []) if isinstance(spec.get("effects"), dict) else []
    critical_states = set(critical_states_raw) if is_text_list(critical_states_raw) else set()
    if not isinstance(global_interrupts, list):
        errors.append("global_interrupts must be a list")
    else:
        for index, interrupt in enumerate(global_interrupts):
            where = f"global_interrupts[{index}]"
            if not isinstance(interrupt, dict):
                errors.append(f"{where} must be an object")
                continue
            event = interrupt.get("event")
            target = interrupt.get("to")
            if event not in {"CANCEL", "TIMEOUT", "BUDGET_EXHAUSTED"}:
                errors.append(f"{where}.event must be CANCEL, TIMEOUT, or BUDGET_EXHAUSTED")
            elif event in seen_interrupts:
                errors.append(f"duplicate global interrupt {event!r}")
            else:
                seen_interrupts.add(event)
            if target not in terminal:
                errors.append(f"{where}.to must reference a terminal state")
            elif terminal.get(target) != INTERRUPT_TERMINAL_CATEGORIES.get(event):
                errors.append(
                    f"{where}.to must have terminal category "
                    f"{INTERRUPT_TERMINAL_CATEGORIES.get(event)!r} for {event!r}"
                )
            if interrupt.get("applies_to") != "all-safe-nonterminal":
                errors.append(f"{where}.applies_to must be 'all-safe-nonterminal'")
            deferred = interrupt.get("deferred_in_states")
            if not is_text_list(deferred, allow_empty=True) or set(deferred) != critical_states:
                errors.append(f"{where}.deferred_in_states must equal effects.effect_critical_states")
            if not is_text(interrupt.get("deferred_behavior")):
                errors.append(f"{where}.deferred_behavior must be non-empty")
            if not is_text(interrupt.get("owner")):
                errors.append(f"{where}.owner must be non-empty")
            if isinstance(event, str) and isinstance(target, str):
                interrupt_targets[event] = target
        if set(interrupt_targets) != {"CANCEL", "TIMEOUT", "BUDGET_EXHAUSTED"}:
            errors.append("global_interrupts must define CANCEL, TIMEOUT, and BUDGET_EXHAUSTED exactly once")

    for source in (state_set - set(terminal)) - critical_states:
        for target in interrupt_targets.values():
            graph[source].add(target)
    if initial in state_set:
        reachable = {initial}
        queue = deque([initial])
        while queue:
            source = queue.popleft()
            for target in graph.get(source, set()):
                if target not in reachable:
                    reachable.add(target)
                    queue.append(target)
        for state in sorted(state_set - reachable):
            errors.append(f"state {state!r} is unreachable from {initial!r}")
        reverse: dict[str, set[str]] = defaultdict(set)
        for source, targets in graph.items():
            for target in targets:
                reverse[target].add(source)
        can_terminate = set(terminal)
        queue = deque(terminal)
        while queue:
            target = queue.popleft()
            for source in reverse.get(target, set()):
                if source not in can_terminate:
                    can_terminate.add(source)
                    queue.append(source)
        for state in sorted((state_set - set(terminal)) - can_terminate):
            errors.append(f"nonterminal state {state!r} has no path to a terminal state")

    budgets = require_object(spec, "budgets", errors)
    for key in sorted(REQUIRED_BUDGETS):
        if not positive_number(budgets.get(key)):
            errors.append(f"budgets.{key} must be a positive numeric hard limit")
    if not is_text(budgets.get("soft_boundary")):
        errors.append("budgets.soft_boundary must define graceful handoff behavior")
    if budgets.get("hard_boundary_owner") in (None, "model", "producer"):
        errors.append("budgets.hard_boundary_owner must be external to the model/producer")
    if budgets.get("aggregate_descendants") is not True:
        errors.append("budgets.aggregate_descendants must be true")

    no_progress = require_object(spec, "no_progress", errors)
    for key in ("fingerprint", "gain_metric", "calibration", "scope"):
        if not is_text(no_progress.get(key)):
            errors.append(f"no_progress.{key} must be a non-empty string")
    if no_progress.get("outcome_state") not in state_set:
        errors.append("no_progress.outcome_state must reference a declared state")
    if not isinstance(no_progress.get("threshold"), int) or no_progress.get("threshold", 0) <= 0:
        errors.append("no_progress.threshold must be a positive integer")
    gain_components = no_progress.get("gain_components")
    if not isinstance(gain_components, dict) or not gain_components or any(
        not positive_number(value) for value in gain_components.values()
    ):
        errors.append("no_progress.gain_components must map names to positive finite weights")
    if no_progress.get("aggregation") not in {"weighted-sum", "mean", "minimum"}:
        errors.append("no_progress.aggregation must be weighted-sum, mean, or minimum")
    epsilon = no_progress.get("epsilon")
    if not isinstance(epsilon, (int, float)) or isinstance(epsilon, bool) or not math.isfinite(float(epsilon)) or epsilon < 0:
        errors.append("no_progress.epsilon must be a finite non-negative number")
    if not isinstance(no_progress.get("window_rounds"), int) or no_progress.get("window_rounds", 0) <= 0:
        errors.append("no_progress.window_rounds must be a positive integer")
    if not is_text(no_progress.get("plateau_comparator")):
        errors.append("no_progress.plateau_comparator must be a non-empty string")

    retry = require_object(spec, "retry", errors)
    if retry.get("retryable_class") != "transient":
        errors.append("retry.retryable_class must be 'transient'")
    for key in ("backoff", "exhausted_outcome"):
        if not is_text(retry.get(key)):
            errors.append(f"retry.{key} must be a non-empty string")

    effects = require_object(spec, "effects", errors)
    for flag in ("persist_intent_before_execution", "atomic_with_checkpoint_and_outbox"):
        if effects.get(flag) is not True:
            errors.append(f"effects.{flag} must be true")
    for key in ("delivery_semantics", "idempotency_key", "durable_ledger", "high_risk_gate", "unknown_outcome"):
        if not is_text(effects.get(key)):
            errors.append(f"effects.{key} must be a non-empty string")
    if effects.get("delivery_semantics") == "exactly-once":
        warnings.append("exactly-once is claimed; attach a proof or use at-least-once plus reconciliation")
    if not is_text_list(effects.get("effect_critical_states")):
        errors.append("effects.effect_critical_states must be a non-empty list")
    else:
        declared_critical = set(effects["effect_critical_states"])
        for state in sorted(declared_critical - state_set):
            errors.append(f"effects.effect_critical_states references unknown state {state!r}")
        missing_critical = required_critical_states - declared_critical
        if missing_critical:
            errors.append(f"effects.effect_critical_states missing high-risk path states: {sorted(missing_critical)}")
        extra_critical = declared_critical - required_critical_states
        if extra_critical:
            errors.append(f"effects.effect_critical_states has states not derived from high-risk paths: {sorted(extra_critical)}")

    checkpoint = require_object(spec, "checkpoint", errors)
    for key in ("boundaries", "persisted_fields"):
        if not is_text_list(checkpoint.get(key)):
            errors.append(f"checkpoint.{key} must be a non-empty list")
    persisted_fields = checkpoint.get("persisted_fields", [])
    normalized_persisted = {
        field.strip().lower().replace("_", " ") for field in persisted_fields if isinstance(field, str)
    }
    if "pending interrupts" not in normalized_persisted:
        errors.append("checkpoint.persisted_fields must include pending interrupts")
    for key in ("compatibility", "migration", "fencing", "monotonic_sequence", "integrity", "corruption_outcome"):
        if not is_text(checkpoint.get(key)):
            errors.append(f"checkpoint.{key} must be a non-empty string")

    approval = require_object(spec, "approval", errors)
    binding = approval.get("binding_fields")
    if not isinstance(binding, list) or not APPROVAL_FIELDS.issubset(set(binding)):
        errors.append(f"approval.binding_fields must include {sorted(APPROVAL_FIELDS)}")
    if approval.get("one_time") is not True:
        errors.append("approval.one_time must be true")
    for key in ("revocation", "stale_outcome"):
        if not is_text(approval.get(key)):
            errors.append(f"approval.{key} must be a non-empty string")

    verification = require_object(spec, "verification", errors)
    for key in ("success_predicate", "environment_evidence", "evaluator_independence", "human_gray_band", "calibration"):
        if not is_text(verification.get(key)):
            errors.append(f"verification.{key} must be a non-empty string")
    for key in ("invariant_checks", "fault_tests"):
        if not is_text_list(verification.get(key)):
            errors.append(f"verification.{key} must be a non-empty list")

    replay = require_object(spec, "replay", errors)
    for key in ("resume", "trajectory_replay"):
        if not is_text(replay.get(key)):
            errors.append(f"replay.{key} must be a non-empty string")
    if not is_text_list(replay.get("deterministic_replay_requirements")):
        errors.append("replay.deterministic_replay_requirements must be a non-empty list")

    security = require_object(spec, "security", errors)
    for key in ("untrusted_content", "tool_least_privilege", "provenance_snapshots", "secret_isolation"):
        if not is_text(security.get(key)):
            errors.append(f"security.{key} must be a non-empty string")

    trace = require_object(spec, "trace", errors)
    fields = trace.get("transition_fields")
    if not isinstance(fields, list) or not TRACE_FIELDS.issubset(set(fields)):
        errors.append(f"trace.transition_fields must include {sorted(TRACE_FIELDS)}")
    if not is_text(trace.get("redaction")):
        errors.append("trace.redaction must be non-empty")

    dispatch = require_object(spec, "commander_dispatch", errors)
    if dispatch.get("mode") != "measured-need":
        errors.append("commander_dispatch.mode must be 'measured-need'")
    if dispatch.get("fixed_uses_edges") is not False:
        errors.append("commander_dispatch.fixed_uses_edges must be false")
    if set(dispatch.get("commanders", [])) != COMMANDERS:
        errors.append(f"commander_dispatch.commanders must equal the seven-command canon: {sorted(COMMANDERS)}")
    if dispatch.get("canon_verdict") != "verdict-bihaenggiman-7commander-unify-2026-06-07":
        errors.append("commander_dispatch.canon_verdict must bind the current user-source verdict")

    icvc = require_object(spec, "icvc", errors)
    for axis in ("inform", "constrain", "verify", "correct"):
        if not is_text(icvc.get(axis)):
            errors.append(f"icvc.{axis} must contain non-empty evidence")
    return errors, warnings


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} LOOP_CONTRACT.json", file=sys.stderr)
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
