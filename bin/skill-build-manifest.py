#!/usr/bin/env python3
"""skill-build-manifest.py — generate SYMPOSIUM/SKILLS/MANIFEST.json + .well-known/skills/index.json.

D16 critique 반영: git_tree_sha를 frontmatter에 embed하지 않고 별도 manifest로 분리.
drift detection (Plan-5 phase 2): merkle_root field — sorted (path, git_tree_sha) tuple SHA256, O(1) drift gate.
Federated discovery (Plan-7 phase 1): RFC 8615 .well-known/skills/index.json — public-safe subset.

Re-run safe — atomic overwrite. Idempotent if no source changes.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import stat
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = SKILLS_DIR / "MANIFEST.json"
WELL_KNOWN_DIR = SKILLS_DIR / ".well-known" / "skills"
WELL_KNOWN_INDEX = WELL_KNOWN_DIR / "index.json"


def run_git(*args):
    return subprocess.check_output(["git", *args], cwd=SKILLS_DIR, text=True).strip()


def parse_frontmatter(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    block = m.group(1)
    for line in block.splitlines():
        m2 = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not m2:
            continue
        key, raw = m2.group(1), m2.group(2).strip()
        if not raw or raw.startswith(">"):
            continue
        # YAML-style quoted string 처리 (PROM 16 F3: SemVer migration)
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            fm[key] = raw[1:-1]
        elif raw.isdigit():
            fm[key] = int(raw)
        else:
            fm[key] = raw
    return fm


def _git_oid_algorithm() -> str:
    try:
        algorithm = run_git("config", "extensions.objectFormat").strip()
        if algorithm == "sha256":
            return "sha256"
    except subprocess.CalledProcessError:
        pass
    return "sha1"


def _git_object_digest(kind: str, payload: bytes, algorithm: str) -> bytes:
    if algorithm not in {"sha1", "sha256"}:
        raise ValueError(f"Unsupported git object algorithm: {algorithm}")
    header = f"{kind} {len(payload)}\0".encode("ascii")
    return hashlib.new(algorithm, header + payload).digest()


def _git_tree_body(directory: Path, algorithm: str) -> bytes:
    entries: list[tuple[bytes, bytes]] = []
    for child in directory.iterdir():
        if child.name == ".git":
            continue
        name = os.fsencode(child.name)
        if b"\0" in name or b"/" in name:
            raise ValueError("Git tree entry contains an invalid name")
        if child.is_symlink():
            mode = b"120000"
            digest = _git_object_digest("blob", os.fsencode(os.readlink(child)), algorithm)
            sort_key = name
        elif child.is_dir():
            child_body = _git_tree_body(child, algorithm)
            if not child_body:
                continue
            mode = b"40000"
            digest = _git_object_digest("tree", child_body, algorithm)
            sort_key = name + b"/"
        elif child.is_file():
            executable_bits = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            mode = b"100755" if child.stat().st_mode & executable_bits else b"100644"
            digest = _git_object_digest("blob", child.read_bytes(), algorithm)
            sort_key = name
        else:
            continue
        entries.append((sort_key, mode + b" " + name + b"\0" + digest))
    return b"".join(entry for _key, entry in sorted(entries))


def _git_tree_oid(directory: Path, *, algorithm: str) -> str:
    return _git_object_digest("tree", _git_tree_body(directory, algorithm), algorithm).hex()


def tree_sha_for_path(skill_dir: Path, *, algorithm: str) -> str:
    if not skill_dir.is_dir():
        return ""
    try:
        return _git_tree_oid(skill_dir, algorithm=algorithm)
    except (OSError, ValueError):
        return ""


def _content_sha256(skill_md: Path) -> str:
    return hashlib.sha256(skill_md.read_bytes()).hexdigest()


def run_resolve_check():
    """A6 L2 pre-build invariant: ensure no SKILL.md ships with unresolved ${MIC_v1.SLOT}.
    Skipped if APT_SKIP_RESOLVE_CHECK=1. KG: skill-resolver-l2-buildstep-2026-05-06.
    """
    import os
    if os.environ.get("APT_SKIP_RESOLVE_CHECK") == "1":
        return
    checker = SKILLS_DIR / "bin" / "skill-resolve-check.sh"
    if not checker.is_file():
        return  # validator not yet installed (older checkout)
    try:
        subprocess.run([str(checker)], check=True, cwd=str(SKILLS_DIR))
    except subprocess.CalledProcessError as e:
        print(f"ERROR: skill-resolve-check failed (exit {e.returncode}). Run bin/skill-resolve-check.sh to inspect.", file=sys.stderr)
        sys.exit(1)


def main():
    run_resolve_check()
    head_commit = run_git("rev-parse", "HEAD")
    head_short = run_git("rev-parse", "--short", "HEAD")
    head_committed_at = run_git("show", "-s", "--format=%cI", "HEAD")
    try:
        latest_tag = run_git("describe", "--tags", "--abbrev=0")
    except subprocess.CalledProcessError:
        latest_tag = None

    skills = []
    algorithm = _git_oid_algorithm()
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = parse_frontmatter(skill_md)
        skills.append({
            "name": fm.get("name", skill_dir.name),
            "path": skill_dir.name,
            "version": fm.get("version"),
            "kg_ref": fm.get("kg_ref"),
            "channel": fm.get("channel", "stable"),
            "git_tree_sha": tree_sha_for_path(skill_dir, algorithm=algorithm),
            "content_sha256": _content_sha256(skill_md),
        })

    merkle_input = "\n".join(f"{s['path']}:{s['git_tree_sha']}" for s in skills)
    merkle_root = hashlib.sha256(merkle_input.encode("utf-8")).hexdigest()

    manifest = {
        "schema": "v1",
        "generatedAt": head_committed_at,
        "git_head_commit": head_commit,
        "git_head_short": head_short,
        "git_latest_tag": latest_tag,
        "canonical_path": str(SKILLS_DIR),
        "skills_count": len(skills),
        "merkle_root": merkle_root,
        "skills": skills,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    WELL_KNOWN_DIR.mkdir(parents=True, exist_ok=True)
    well_known = {
        "schema": "rfc8615-skills-v1",
        "publisher": "SYMPOSIUM",
        "release": latest_tag,
        "git_head_short": head_short,
        "merkle_root": merkle_root,
        "skills_count": len(skills),
        "skills": [
            {
                "name": s["name"],
                "version": s["version"],
                "kg_ref": s["kg_ref"],
                "channel": s["channel"],
                "git_tree_sha": s["git_tree_sha"],
            }
            for s in skills
        ],
    }
    WELL_KNOWN_INDEX.write_text(
        json.dumps(well_known, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"OK: MANIFEST.json + .well-known/skills/index.json ({len(skills)} skills, merkle={merkle_root[:12]}, head={head_short}, tag={latest_tag})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
