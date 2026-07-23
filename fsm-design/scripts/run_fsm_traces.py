#!/usr/bin/env python3
"""Execute abstract fsm-spec/v1 traces using explicit guard outcomes."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_case(
    machine: dict[str, Any], case: dict[str, Any]
) -> tuple[list[str], set[str], set[str], bool]:
    failures: list[str] = []
    selected_ids: set[str] = set()
    false_guards: set[str] = set()
    exercised_invalid_event = False
    state = machine["initial"]
    policy = machine["invalid_event_policy"]
    for index, step in enumerate(case.get("steps", [])):
        event = step.get("event")
        guard_results = step.get("guard_results", {})
        choices = [
            transition for transition in machine["transitions"]
            if transition["from"] == state and transition["event"] == event
        ]
        choices.sort(key=lambda transition: transition.get("priority", 0))
        for transition in choices:
            guard = transition.get("guard")
            if guard is not None and guard_results.get(guard) is False:
                false_guards.add(guard)
        enabled = [
            transition for transition in choices
            if transition.get("guard") is None or guard_results.get(transition["guard"]) is True
        ]
        if enabled:
            selected = enabled[0]
            selected_ids.add(selected["id"])
            state = selected["to"]
            effects = selected.get("effects", [])
        else:
            exercised_invalid_event = exercised_invalid_event or not choices
            rejection_mode = policy.get("guard_false") if choices else policy.get("mode")
            effects = [policy["effect"]] if rejection_mode == "reject-and-audit" else []
        if state != step.get("expected_state"):
            failures.append(f"{case.get('id')} step {index}: state={state!r}, expected={step.get('expected_state')!r}")
        if effects != step.get("expected_effects"):
            failures.append(f"{case.get('id')} step {index}: effects={effects!r}, expected={step.get('expected_effects')!r}")
    return failures, selected_ids, false_guards, exercised_invalid_event


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {Path(sys.argv[0]).name} FSM_SPEC.json FSM_TRACES.json", file=sys.stderr)
        return 2
    try:
        spec = load(Path(sys.argv[1]))
        traces = load(Path(sys.argv[2]))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 2
    machine_by_id = {machine["id"]: machine for machine in spec.get("machines", [])}
    failures: list[str] = []
    selected_by_machine: dict[str, set[str]] = {machine_id: set() for machine_id in machine_by_id}
    false_guards_by_machine: dict[str, set[str]] = {machine_id: set() for machine_id in machine_by_id}
    invalid_by_machine: dict[str, bool] = {machine_id: False for machine_id in machine_by_id}
    for case in traces.get("cases", []):
        machine = machine_by_id.get(case.get("machine"))
        if machine is None:
            failures.append(f"{case.get('id')}: unknown machine {case.get('machine')!r}")
            continue
        case_failures, selected_ids, false_guards, exercised_invalid = run_case(machine, case)
        failures.extend(case_failures)
        machine_id = machine["id"]
        selected_by_machine[machine_id].update(selected_ids)
        false_guards_by_machine[machine_id].update(false_guards)
        invalid_by_machine[machine_id] = invalid_by_machine[machine_id] or exercised_invalid
    for machine_id, machine in machine_by_id.items():
        expected_transitions = {transition["id"] for transition in machine.get("transitions", [])}
        missing_transitions = expected_transitions - selected_by_machine[machine_id]
        if missing_transitions:
            failures.append(f"{machine_id}: traces do not select transitions {sorted(missing_transitions)}")
        expected_false_guards = {
            transition["guard"] for transition in machine.get("transitions", []) if transition.get("guard")
        }
        missing_false_guards = expected_false_guards - false_guards_by_machine[machine_id]
        if missing_false_guards:
            failures.append(f"{machine_id}: traces do not exercise guard-false outcomes {sorted(missing_false_guards)}")
        if not invalid_by_machine[machine_id]:
            failures.append(f"{machine_id}: traces do not exercise invalid-event policy")
    for failure in failures:
        print(f"FAIL  {failure}")
    if failures:
        return 1
    print(f"OK    {len(traces.get('cases', []))} abstract trace case(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
