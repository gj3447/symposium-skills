---
name: harness-diagnose
kg_ref: hub-harness-3tier
version: "1.0.0"
channel: stable
provenance: ENGINE_GENERATED_M9_2  # bhgman MCP `harness_diagnose` 정적 KB 이주 (2026-08-03, M9.2)
description: >
  Harness 3-tier 진단 정적 KB — KNOWN_FRAMEWORKS 40개 이름→tier(L_IDE/L_RT/L_MC) + 4축(Inform/Constrain/Verify/Correct) 매핑 + 분류 규칙.
  구 MCP `harness_diagnose` 도구의 스킬 강등본 (C-class: 정적 KB 이름매칭, M9.2. M6 capability-probe 방향은 별도 축).
  사용: 이름 매치(HIGH) → 아래 표 조회. 미등록 대상은 분류 규칙 수동 적용 또는 UNKNOWN 선언 (추측 금지).
  Use when: classifying a named framework with this frozen 3-tier/4-axis knowledge base. Do not use when: diagnosing a repository from live evidence or designing a harness; use `$harness` instead.
  재생성: bhgman `engine.harness.harness.diagnose()` 전수 — engine_sha256 불일치 시 stale.
engine_sha256: 34d95fa1462d40cd1a73f68cb996360d2feca99c7c28288de4db7ec8ece94459
---

# Harness Diagnose — 정적 KB (M9.2 스킬 강등)

> 이주원: MCP `harness_diagnose` (deprecated surface, 2026-08-03 제거). 동치 증거: 40개 전수 응답 sha256 `34d95fa1462d40cd…`.
> 정직 규칙: 축 부재 = **unknown** (부재 ≠ 능력 없음). 미등록 대상 추측 진단 금지.

## 분류 규칙 (결정론 코어와 동일)

1. **이름 매치** (아래 표, case-insensitive, 제어문자 제거) → 해당 tier, confidence HIGH.
2. **키워드 fallback** → MEDIUM/LOW (코어 엔진 규칙; 스킬에서는 UNKNOWN 선언이 정직).
3. **명시 signals** → 호출자가 축 신호를 직접 주면 override.

tier 라벨: `L_IDE` = IDE-host coding harness / `L_RT` = application agent runtime / `L_MC` = managed cloud control plane.
축 약어: I=Inform C=Constrain V=Verify R=Correct — `Y`=present(강신호) `i`=inferred(약신호) `?`=unknown.

## KNOWN_FRAMEWORKS (40)

| framework | tier | conf | I/C/V/R |
|---|---|---|---|
| agno | L_RT | HIGH | I:Y/C:?/V:?/C:? |
| aider | L_IDE | HIGH | I:Y/C:?/V:Y/C:Y |
| autogen | L_RT | HIGH | I:Y/C:?/V:?/C:Y |
| azure ai agent | L_MC | HIGH | I:?/C:?/V:?/C:? |
| bedrock agent | L_MC | HIGH | I:?/C:?/V:?/C:? |
| claude code | L_IDE | HIGH | I:?/C:Y/V:Y/C:? |
| claude-flow | L_RT | HIGH | I:?/C:?/V:?/C:? |
| cline | L_IDE | HIGH | I:Y/C:Y/V:?/C:Y |
| codex | L_IDE | HIGH | I:?/C:Y/V:?/C:Y |
| continue | L_IDE | HIGH | I:Y/C:?/V:?/C:? |
| copilot | L_IDE | HIGH | I:Y/C:?/V:?/C:? |
| crewai | L_RT | HIGH | I:Y/C:?/V:?/C:Y |
| crush | L_IDE | HIGH | I:?/C:Y/V:?/C:Y |
| cursor | L_IDE | HIGH | I:Y/C:?/V:?/C:? |
| dspy | L_RT | HIGH | I:?/C:?/V:Y/C:Y |
| gemini cli | L_IDE | HIGH | I:Y/C:?/V:?/C:Y |
| google adk | L_RT | HIGH | I:?/C:Y/V:?/C:? |
| goose | L_IDE | HIGH | I:?/C:Y/V:?/C:Y |
| langchain | L_RT | HIGH | I:Y/C:?/V:?/C:? |
| langgraph | L_RT | HIGH | I:?/C:Y/V:Y/C:? |
| letta | L_RT | HIGH | I:Y/C:?/V:?/C:? |
| llamaindex | L_RT | HIGH | I:Y/C:?/V:?/C:? |
| managed agent | L_MC | HIGH | I:?/C:Y/V:Y/C:? |
| mastra | L_RT | HIGH | I:?/C:Y/V:?/C:Y |
| microsoft agent framework | L_RT | HIGH | I:?/C:Y/V:Y/C:? |
| openai agents sdk | L_RT | HIGH | I:?/C:Y/V:?/C:? |
| openai assistant | L_MC | HIGH | I:Y/C:?/V:?/C:? |
| opencode | L_IDE | HIGH | I:?/C:Y/V:Y/C:Y |
| openhands | L_IDE | HIGH | I:Y/C:Y/V:Y/C:Y |
| pydantic ai | L_RT | HIGH | I:?/C:Y/V:Y/C:? |
| pydantic-ai | L_RT | HIGH | I:?/C:Y/V:Y/C:? |
| ruflo | L_RT | HIGH | I:?/C:?/V:?/C:? |
| semantic kernel | L_RT | HIGH | I:Y/C:?/V:?/C:? |
| smolagents | L_RT | HIGH | I:?/C:Y/V:?/C:? |
| strands | L_RT | HIGH | I:?/C:Y/V:?/C:? |
| swe-agent | L_IDE | HIGH | I:?/C:Y/V:Y/C:? |
| vercel ai | L_RT | HIGH | I:?/C:Y/V:?/C:Y |
| vertex ai agent | L_MC | HIGH | I:?/C:?/V:?/C:? |
| windsurf | L_IDE | HIGH | I:Y/C:?/V:?/C:? |
| zed | L_IDE | HIGH | I:Y/C:?/V:?/C:? |

## 정직 한계

- 이름 매치만 HIGH — 표에 없는 대상을 관련성으로 끼워 맞추지 말 것 (UNKNOWN이 정답).
- M6(capability probe 기반 동적 진단)는 별도 미착수 축 — 이 표는 2026-08-03 시점 정적 스냅샷.
