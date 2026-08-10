#!/usr/bin/env python3
"""Audit canonical skill descriptions for unambiguous routing boundaries.

The parser intentionally uses only the Python standard library.  It supports the
frontmatter forms used in this repository: inline scalars and folded/literal
block scalars.  Description text is whitespace-normalized before measuring it,
matching the Codex plugin porter's metadata normalization.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


SKILLS_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = SKILLS_ROOT / "MANIFEST.json"
MAX_DESCRIPTION_CHARS = 1024

POSITIVE_MARKER_RE = re.compile(r"\b(?:Use|Invoke) when:")
NEGATIVE_MARKER = "Do not use when:"
ALTERNATE_ROUTE_RE = re.compile(
    r"Do not use when:\s*(?P<near_miss>[^;]+);\s*"
    r"use\s+(?P<route>[^.;]+?)\s+instead(?:[.!]|$)",
    re.DOTALL,
)
BLOCK_SCALAR_RE = re.compile(r"[>|](?:[+-]|[1-9]|[+-][1-9]|[1-9][+-])?")
GENERIC_ROUTES = {
    "it",
    "this",
    "something else",
    "another skill",
    "another workflow",
    "a different skill",
    "a different workflow",
    "the other skill",
}


class FrontmatterError(ValueError):
    """Raised when a SKILL.md frontmatter description cannot be read."""


@dataclass(frozen=True)
class AuditResult:
    path: str
    skill: str
    description_chars: int
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def _frontmatter_lines(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].lstrip("\ufeff") != "---":
        raise FrontmatterError("frontmatter must start with an exact '---' line")

    for index in range(1, len(lines)):
        if lines[index] == "---":
            return lines[1:index]
    raise FrontmatterError("frontmatter has no closing '---' line")


def _without_trailing_yaml_comment(value: str) -> str:
    """Remove a YAML comment without treating # inside quotes as a comment."""
    in_single_quote = False
    in_double_quote = False
    escaped = False
    for index, character in enumerate(value):
        if in_double_quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_double_quote = False
            continue
        if in_single_quote:
            if character == "'":
                in_single_quote = False
            continue
        if character == '"':
            in_double_quote = True
        elif character == "'":
            in_single_quote = True
        elif character == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def _decode_inline_scalar(value: str) -> str:
    value = _without_trailing_yaml_comment(value).strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as exc:
            raise FrontmatterError(f"invalid double-quoted description: {exc}") from exc
        if not isinstance(decoded, str):
            raise FrontmatterError("description must be a string")
        return decoded
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def _extract_description(frontmatter: Sequence[str]) -> str:
    matches: list[tuple[int, int, str]] = []
    for index, line in enumerate(frontmatter):
        match = re.match(r"^(?P<indent>[ \t]*)description:\s*(?P<value>.*)$", line)
        if match:
            matches.append((index, len(match.group("indent")), match.group("value")))

    if not matches:
        raise FrontmatterError("missing 'description:' field")
    if len(matches) != 1:
        raise FrontmatterError("frontmatter contains multiple 'description:' fields")

    index, key_indent, value = matches[0]
    value = value.strip()
    scalar_header = _without_trailing_yaml_comment(value)
    if not BLOCK_SCALAR_RE.fullmatch(scalar_header):
        description = _decode_inline_scalar(value)
        if not description:
            raise FrontmatterError("description is empty")
        return description

    block_lines: list[str] = []
    for line in frontmatter[index + 1 :]:
        if not line.strip():
            block_lines.append("")
            continue
        indent = len(line) - len(line.lstrip(" \t"))
        if indent <= key_indent:
            break
        block_lines.append(line)

    content_indents = [
        len(line) - len(line.lstrip(" \t")) for line in block_lines if line.strip()
    ]
    if not content_indents:
        raise FrontmatterError("description block scalar is empty")
    content_indent = min(content_indents)
    return "\n".join(
        line[content_indent:] if line.strip() else "" for line in block_lines
    )


def normalized_description(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise FrontmatterError(f"cannot read file: {exc}") from exc
    raw = _extract_description(_frontmatter_lines(text))
    return re.sub(r"\s+", " ", raw).strip()


def audit_path(path: Path) -> AuditResult:
    errors: list[str] = []
    description = ""
    try:
        description = normalized_description(path)
    except FrontmatterError as exc:
        errors.append(str(exc))
    else:
        if len(description) > MAX_DESCRIPTION_CHARS:
            errors.append(
                f"description is {len(description)} characters; maximum is "
                f"{MAX_DESCRIPTION_CHARS}"
            )
        if not POSITIVE_MARKER_RE.search(description):
            errors.append("missing exact positive marker 'Use when:' or 'Invoke when:'")
        if NEGATIVE_MARKER not in description:
            errors.append(f"missing exact negative marker '{NEGATIVE_MARKER}'")
        route_match = ALTERNATE_ROUTE_RE.search(description)
        if not route_match:
            errors.append(
                "negative boundary must use "
                "'Do not use when: <near miss>; use <explicit route> instead.'"
            )
        else:
            near_miss = route_match.group("near_miss").strip()
            route = route_match.group("route").strip()
            if len(near_miss) < 8:
                errors.append("negative boundary near miss is too vague")
            if route.casefold() in GENERIC_ROUTES or len(route) < 3:
                errors.append("alternate route is not explicit")

    try:
        display_path = str(path.resolve().relative_to(SKILLS_ROOT.resolve()))
    except ValueError:
        display_path = str(path)
    return AuditResult(
        path=display_path,
        skill=path.parent.name,
        description_chars=len(description),
        errors=tuple(errors),
    )


def canonical_skill_paths() -> list[Path]:
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FrontmatterError(f"cannot read canonical manifest: {exc}") from exc

    skills = manifest.get("skills")
    declared_count = manifest.get("skills_count")
    if not isinstance(skills, list) or not isinstance(declared_count, int):
        raise FrontmatterError("manifest must contain integer skills_count and skills list")
    if declared_count != len(skills):
        raise FrontmatterError(
            f"manifest skills_count={declared_count} but contains {len(skills)} entries"
        )

    paths: list[Path] = []
    seen: set[str] = set()
    for entry in skills:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise FrontmatterError("each manifest skill must contain a string path")
        relative = entry["path"]
        if relative in seen:
            raise FrontmatterError(f"duplicate manifest skill path: {relative}")
        seen.add(relative)
        path = SKILLS_ROOT / relative / "SKILL.md"
        if not path.is_file():
            raise FrontmatterError(f"manifest skill is missing SKILL.md: {relative}")
        paths.append(path)
    return paths


def _print_human(results: Sequence[AuditResult]) -> None:
    for result in results:
        if result.ok:
            print(
                f"OK   {result.skill}: routing description "
                f"({result.description_chars}/{MAX_DESCRIPTION_CHARS} chars)"
            )
            continue
        for error in result.errors:
            print(f"FAIL {result.path}: {error}", file=sys.stderr)
    failed = sum(not result.ok for result in results)
    print(
        f"SUMMARY checked={len(results)} passed={len(results) - failed} failed={failed}",
        file=sys.stderr if failed else sys.stdout,
    )


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="SKILL.md files to audit")
    parser.add_argument("--all", action="store_true", help="audit all MANIFEST skills")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return exit status 1 when any routing description fails",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    if args.all and args.paths:
        parser.error("--all and explicit paths are mutually exclusive")
    if not args.all and not args.paths:
        parser.error("provide --all or at least one SKILL.md path")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        paths = canonical_skill_paths() if args.all else args.paths
    except FrontmatterError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"ERROR {exc}", file=sys.stderr)
        return 2

    results = [audit_path(path) for path in paths]
    failed = sum(not result.ok for result in results)
    if args.json:
        print(
            json.dumps(
                {
                    "ok": failed == 0,
                    "checked": len(results),
                    "passed": len(results) - failed,
                    "failed": failed,
                    "max_description_chars": MAX_DESCRIPTION_CHARS,
                    "results": [
                        {**asdict(result), "ok": result.ok} for result in results
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        _print_human(results)
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
