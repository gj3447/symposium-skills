#!/usr/bin/env python3
"""Validate a PI completion envelope without executing its claimed tools."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{7,64}$")
ACTOR_ID = re.compile(r"^[a-z0-9][a-z0-9._:-]*$")


def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def sequence(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def require_text(obj: dict[str, Any], key: str, errors: list[str], prefix: str) -> None:
    if not text(obj.get(key)):
        errors.append(f"{prefix}.{key} must be a non-empty string")


def require_sha(obj: dict[str, Any], key: str, errors: list[str], prefix: str) -> None:
    value = obj.get(key)
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        errors.append(f"{prefix}.{key} must be a lowercase 64-hex SHA-256")


def require_actor(obj: dict[str, Any], key: str, errors: list[str], prefix: str) -> None:
    value = obj.get(key)
    if not isinstance(value, str) or ACTOR_ID.fullmatch(value) is None:
        errors.append(f"{prefix}.{key} must be a canonical lowercase actor id")


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not text(value):
        errors.append(f"{label} must be an ISO-8601 timestamp with timezone")
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp with timezone")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{label} must include a timezone")
        return None
    return parsed


def safe_repo_path(value: Any, repo_name: Any) -> bool:
    if not text(value) or not text(repo_name):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and len(path.parts) > 1 and path.parts[0] == repo_name


def verify_file(path_value: Any, sha_value: Any, root: Path, label: str) -> list[str]:
    if not text(path_value) or not isinstance(sha_value, str) or SHA256.fullmatch(sha_value) is None:
        return []
    path = Path(path_value)
    root = root.resolve()
    resolved = (path if path.is_absolute() else root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return [f"{label} escapes artifact root: {resolved}"]
    try:
        actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
    except OSError as error:
        return [f"{label} cannot be hash-verified at {resolved}: {error}"]
    return [] if actual == sha_value else [f"{label} SHA-256 mismatch at {resolved}"]


def verify_linked_files(document: Any, root: Path) -> list[str]:
    if not isinstance(document, dict):
        return []
    errors: list[str] = []
    measurement = mapping(document.get("measurement"))
    for path_key, sha_key in (("receipt_path", "receipt_sha256"), ("evidence_path", "evidence_sha256")):
        errors.extend(verify_file(measurement.get(path_key), measurement.get(sha_key), root, f"measurement.{path_key}"))
    judgment = mapping(document.get("judgment"))
    errors.extend(verify_file(judgment.get("packet_path"), judgment.get("packet_sha256"), root, "judgment.packet_path"))
    for index, raw in enumerate(sequence(document.get("verification"))):
        item = mapping(raw)
        if "output_path" in item:
            errors.extend(verify_file(item.get("output_path"), item.get("output_sha256"), root, f"verification[{index}].output_path"))
    return errors


def validate(document: Any, stage: str, allow_template: bool = False) -> list[str]:
    if not isinstance(document, dict):
        return ["document must be a JSON object"]
    errors: list[str] = []
    if allow_template:
        if document.get("template_only") is not True:
            errors.append("--template requires template_only=true")
    elif document.get("template_only") is not False:
        errors.append("completion packet must explicitly set template_only=false")
    if document.get("schema_version") != "pi-cycle/v1":
        errors.append("schema_version must be 'pi-cycle/v1'")
    require_text(document, "cycle_id", errors, "root")
    if document.get("mode") not in {"read_only", "write"}:
        errors.append("mode must be 'read_only' or 'write'")
    if document.get("kind") not in {"investigation", "behavior", "experiment", "progress_claim", "design"}:
        errors.append("kind must be investigation, behavior, experiment, progress_claim, or design")

    repo = mapping(document.get("repo"))
    for key in ("name", "logical_path", "resolved_root"):
        require_text(repo, key, errors, "repo")
    if not sequence(repo.get("instructions_read")) or not all(text(x) for x in sequence(repo.get("instructions_read"))):
        errors.append("repo.instructions_read must contain at least one path")
    git_head = repo.get("git_head")
    if git_head is not None and (not isinstance(git_head, str) or GIT_SHA.fullmatch(git_head) is None):
        errors.append("repo.git_head must be a lowercase 7-64 hex commit id when present")

    roles = mapping(document.get("roles"))
    for key in ("coordinator", "implementer", "judge"):
        require_actor(roles, key, errors, "roles")
    if roles.get("implementer") == roles.get("judge"):
        errors.append("roles.implementer and roles.judge must differ")

    coordination = mapping(document.get("coordination"))
    writes = sequence(coordination.get("writes"))
    if document.get("mode") == "read_only":
        if writes:
            errors.append("read_only cycles must not declare coordination.writes")
        if coordination.get("token_state") == "HELD":
            errors.append("read_only cycles must not hold the repository writer token")
    else:
        for key in ("owner_id", "policy", "token_state", "base_head"):
            require_text(coordination, key, errors, "coordination")
        if coordination.get("policy") != "canonical_main_single_writer":
            errors.append("coordination.policy must be canonical_main_single_writer")
        if not writes or len(set(writes)) != len(writes):
            errors.append("coordination.writes must be a non-empty list of unique paths")
        for index, write_path in enumerate(writes):
            if not safe_repo_path(write_path, repo.get("name")):
                errors.append(f"coordination.writes[{index}] must be a repo-qualified relative path without '..'")
        base_head = coordination.get("base_head")
        if not isinstance(base_head, str) or GIT_SHA.fullmatch(base_head) is None:
            errors.append("coordination.base_head must be a lowercase 7-64 hex commit id")
        if stage == "complete":
            if coordination.get("token_state") != "DONE":
                errors.append("complete write cycles require coordination.token_state == 'DONE'")
            commit_sha = coordination.get("commit_sha")
            if not isinstance(commit_sha, str) or GIT_SHA.fullmatch(commit_sha) is None:
                errors.append("coordination.commit_sha must be a lowercase 7-64 hex commit id")
            published_refs = mapping(coordination.get("published_refs"))
            if not published_refs:
                errors.append("complete write cycles require coordination.published_refs")
            for remote, remote_sha in published_refs.items():
                if not text(remote) or not isinstance(remote_sha, str) or GIT_SHA.fullmatch(remote_sha) is None:
                    errors.append(f"coordination.published_refs[{remote!r}] must be a lowercase 7-64 hex commit id")
                elif remote_sha != commit_sha:
                    errors.append(f"coordination.published_refs[{remote!r}] must equal coordination.commit_sha")
        elif coordination.get("token_state") != "HELD":
            errors.append("planned write cycles require coordination.token_state == 'HELD'")

    requires_receipt = stage == "complete" and (
        document.get("kind") == "behavior" or document.get("runtime_behavior") is True
    )
    requires_judgment = stage == "complete" and (
        document.get("kind") in {"experiment", "progress_claim"}
        or document.get("progress_claim") is True
    )
    measurement = mapping(document.get("measurement"))
    judgment = mapping(document.get("judgment"))
    if requires_receipt:
        for key in ("receipt_path", "test_command"):
            require_text(measurement, key, errors, "measurement")
        require_sha(measurement, "receipt_sha256", errors, "measurement")
        if measurement.get("positive_verdict") not in {"green", "present"}:
            errors.append("measurement.positive_verdict must be green or present")
        if measurement.get("negative_verdict") not in {"absent", "red", "failed", "rejected"}:
            errors.append("measurement.negative_verdict must prove the same gate failed")
    if requires_judgment:
        if measurement.get("measurement_type") not in {"ooptdd_receipt", "numeric_probe", "dataset_manifest", "replay"}:
            errors.append("judged experiments require a supported measurement.measurement_type")
        for key in ("evidence_path",):
            require_text(measurement, key, errors, "measurement")
        require_sha(measurement, "evidence_sha256", errors, "measurement")
    if requires_judgment or judgment:
        for key in ("packet_path", "judge_command"):
            require_text(judgment, key, errors, "judgment")
        require_sha(judgment, "packet_sha256", errors, "judgment")
        if judgment.get("source") != "scripted":
            errors.append("judgment.source must be 'scripted'")
        if judgment.get("verified_from_receipt") is not True:
            errors.append("judgment.verified_from_receipt must be true")

    verification = sequence(document.get("verification"))
    if stage == "complete":
        if not verification:
            errors.append("complete cycles require at least one verification record")
        for index, check in enumerate(verification):
            item = mapping(check)
            require_text(item, "command", errors, f"verification[{index}]")
            if item.get("exit_code") != 0:
                errors.append(f"verification[{index}].exit_code must be 0")
            require_sha(item, "output_sha256", errors, f"verification[{index}]")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--stage", choices=("plan", "complete"), default="complete")
    parser.add_argument("--template", action="store_true", help="validate the bundled placeholder template only")
    parser.add_argument("--verify-linked", action="store_true", help="hash-verify linked artifacts under --root")
    parser.add_argument("--root", type=Path, help="repository root used for relative linked artifact paths")
    args = parser.parse_args()
    if args.verify_linked and args.root is None:
        parser.error("--verify-linked requires --root")
    try:
        document = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 2
    errors = validate(document, args.stage, allow_template=args.template)
    if args.verify_linked:
        errors.extend(verify_linked_files(document, args.root.resolve()))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.template:
        print(f"valid pi-cycle/v1 template ({args.stage}); not completion evidence")
    elif args.verify_linked:
        print(f"valid pi-cycle/v1 ({args.stage}); linked artifact hashes verified")
    else:
        print(f"structurally valid pi-cycle/v1 ({args.stage}); claimed tools and artifacts were not executed or hash-verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
