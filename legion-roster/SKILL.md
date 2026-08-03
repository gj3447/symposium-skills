---
name: legion-roster
kg_ref: bihaenggiman-legioncommanders-2026-05-26
version: "1.0.0"
channel: stable
provenance: ENGINE_GENERATED_M9_2  # bhgman MCP `legion_roster` 정적 페이로드 이주 (2026-08-03, M9.2)
description: >
  비행기맨 #4 산하 7군단장 roster (정적) — 동사·Contract requires/provides·정전 순서.
  구 MCP `legion_roster` 도구의 스킬 강등본 (C-class: 정적 지식, M9.2).
  재생성: bhgman `engine.mcp_server.tools.legion.legion_roster_impl()` — engine_sha256 불일치 시 stale.
  참고: legion_run(폐루프 실행)은 MCP 잔류(A-class, KG 상태 의존).
engine_sha256: f2133a18b85e8ddd7333c2ebfa4445aaf9a65d97cdf45db6ef72a556254190bf
---

# Legion Roster — 7군단장 (M9.2 스킬 강등)

> 이주원: MCP `legion_roster` (deprecated surface, 2026-08-03 제거). 동치 증거: sha256 `f2133a18b85e8ddd…`.
> 획득→연결→창조→정리→검증→실현 (+출격=dispatch loop). naesengmoon requires all 4 prior provides; hades requires verdict (실현 종착, gate 후).

| 군단장 | 동사 | requires | provides | 역할 |
|---|---|---|---|---|
| prometheus | 획득 | run_cypher | acquired | active commander (CommanderStage) |
| longinus | 연결 | run_cypher | bindings | active commander (CommanderStage) |
| eureka | 창조 | run_cypher | abstractions | active commander (CommanderStage) |
| occam | 정리 | run_cypher | hygiene | active commander (CommanderStage) |
| naesengmoon | 검증 | acquired, bindings, abstractions, hygiene | verdict | active commander (CommanderStage) |
| hades | 실현 | verdict | realized | active commander (CommanderStage) |
| jaebaeman | 출격 | — | — | dispatch-loop (Legion.run itself, not a stage) |

- 정전 순서: **획득 → 연결 → 창조 → 정리 → 검증 → 실현** (+출격 = dispatch loop)
- count: 7 (6 CommanderStage + jaebaeman)
- 경계 정전: `bihaenggiman-7commander-boundaries-2026-05-26`, `adr-seven-commander-legion-architecture-2026-05-27`, `hades-canonical-2026-05-27`
- dispatch는 measurement-driven conditional (고정 USES 아님): `7cmd-measurement-driven-conditional-dispatch-2026-05-30`
