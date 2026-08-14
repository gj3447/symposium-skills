---
name: prom
kg_ref: ATOM_Skill_prom_alias
version: "3.1.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY  # SKILL.md = AI engineering; underlying methodology = user-primary mythology (12 apostles + 5 weapons). Per PseudepigraphaValidationGate-v1-2026-04-30.
description: >-
  Alias the bounded Prometheus evidence-first workflow while treating N as an optional maximum coverage budget rather than a vote or required agent count. Invoke when: the user enters `/prom`, `prom N`, or otherwise requests the short Prometheus command. Do not use when: the request is a stable one-step lookup or direct action needing no research cycle; use direct handling instead.
---

## Root policy boundary

`N` is an optional maximum coverage budget, not a required axis/agent count, vote, or confidence score.
The delegated run returns local evidence by default and follows `../AGENTS.md`.

# /prom — `/prometheus` alias

> `/prom`은 `/prometheus`의 짧은 별칭이다. 로직 중복 없음.

## 사용법

```
/prom 3 "간단한 문제"      → 최대 3개 독립 축
/prom 8 "중간 문제"        → 최대 8개 독립 축
/prom "문제만"             → 질문에 필요한 최소 축만 선택
```

## 실행 지침

`$ARGUMENTS`를 그대로 `../prometheus/SKILL.md`에 넘긴다.

**본문 정본**: [`../prometheus/SKILL.md`](../prometheus/SKILL.md)

`/prom`은 라우팅 단축어일 뿐 별도 저장·재귀·KG 쓰기 로직이 없다.

## 왜 별칭만 분리했나

- **DRY**: SKILL.md 본문 복제 시 drift 발생 → 단일 정본 유지
- **Claude Code 규약**: 슬래시 커맨드 = skill 디렉토리명 1:1 → `/prom`을 위해 최소 디렉토리 필요
- **얇은 래퍼**: 40줄 이내 유지

# KG: ATOM_Skill_prometheus
