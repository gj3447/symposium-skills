---
name: naesengmoon-lens-registry
kg_ref: naesengmoon-canonical-2026-05-19
version: "1.0.0"
channel: stable
provenance: ENGINE_GENERATED_M9_2  # bhgman MCP `naesengmoon_lens_check` 정적 페이로드 이주 (2026-08-03, M9.2 of LakatosTree_BhgmanToolModernization_20260729)
description: >
  나생문 LensSet 레지스트리 (정적) — 4렌즈 멤버십·축 목록 + HR12 계층 분리 규칙 + 하네스 4축 매핑.
  구 MCP `naesengmoon_lens_check` 도구의 스킬 강등본 (C-class: 정적 지식, M9.2).
  재생성: bhgman `engine.mcp_server.tools.naesengmoon.naesengmoon_lens_check_impl("all")` — engine_sha256 불일치 시 stale.
  Use when: looking up static LensSet membership, axes, critic minima, HR12 separation, or harness mapping. Do not use when: running a live multi-lens validation or xlock verdict; use `$taliban` instead.
engine_sha256: 5244437b559eb189be30622616090e88883ce9bcd36fee03b097cc61a57038f4
---

# 나생문 Lens Registry (M9.2 스킬 강등)

> 이주원: MCP `naesengmoon_lens_check` (deprecated surface, 2026-08-03 제거). 동치 증거: 이 문서 테이블은 impl 응답에서 기계 생성됨 (sha256 `5244437b559eb189…`, sort_keys 정규화).
> HR12: **HR12: never mix tiers. constitutional = artifact validation. mathematical = methodology meta-verification only. cross-tier application is BLOCKED at the naesengmoon gate.**

## 4 Lens

| lens | 축 수 | min_critics | 설명 | axes |
|---|---|---|---|---|
| `constitutional` | 9 | 3 | Default constitutional lens — 9 axes (6 executable xlock + 3 judgment tier; M2 2026-07-29). | correctness, completeness, consistency, efficiency, maintainability, safety, evidence, compositional, fail_modes |
| `longinus` | 7 | 2 | Longinus 7-Layer Reference Model lens. | L1_Symbol, L2_Source, L3_Path, L4_Crate, L5_ReferenceSite, L6_Sha256Baseline, L7_AestheticIntentional |
| `mathematical` | 113 | 7 | Meta-verification 113-axis lens (use for methodology meta-checks only). | (KG 참조 — 113축 미전개) |
| `solid` | 5 | 2 | SOLID class-level lens (SRP/OCP/LSP/ISP/DIP). | SRP, OCP, LSP, ISP, DIP |

## UNION 모드 (lens=all)

- union_axis_count_partial: **21** (전개된 축만 집계 — mathematical 113축은 KG 참조)
- union 축 목록: DIP, ISP, L1_Symbol, L2_Source, L3_Path, L4_Crate, L5_ReferenceSite, L6_Sha256Baseline, L7_AestheticIntentional, LSP, OCP, SRP, completeness, compositional, consistency, correctness, efficiency, evidence, fail_modes, maintainability, safety

## 하네스 4축 매핑

| 축 | naesengmoon 대응 |
|---|---|
| verify | naesengmoon xlock predicates — executable verification loops |
| constrain | fail-closed gates + vacuity refusal (guardrails) |
| inform | KG provenance + receipts (observability) |
| correct | executor != critic — generator/evaluator split (adversarial evaluation) |

## 정직 한계

- 정적 스냅샷 — KG에 렌즈 추가 시 이 문서는 drift한다. 재생성 절차: 위 frontmatter의 재생성 명령 실행 → 표 갱신 + engine_sha256 재계산.
- coverage_score는 의도적으로 없음 (축 수를 단일 숫자로 평탄화하지 않는다 — Goodhart 방지).
- 실행 판정(xlock)은 이 스킬 범위 밖 — `naesengmoon_xlock_check` (M9.3 CLI 이주 예정).
