---
name: tlb
kg_ref: ATOM_Skill_tlb_alias
version: "2.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY  # SKILL.md = AI engineering; underlying methodology = user-primary mythology (12 apostles + 5 weapons). Per PseudepigraphaValidationGate-v1-2026-04-30.
description: >-
  Alias `/taliban` for the same Naesengmoon adversarial validation workflow and LensSet selection. Invoke when: the user enters `/tlb <target>` or explicitly requests the short Naesengmoon command. Do not use when: the target specifically requires the mathematical preset or needs no adversarial validation; use `$88-taliban` or direct review instead.
---

# /tlb — `/taliban` alias

> `/tlb`는 `/taliban`의 짧은 별칭이다. 로직 중복 없음.

## 사용법

```
/tlb <target>                    → 기본 constitutional 9-lens 검증
/tlb <target> --lens mathematical → 113-lens 수학적 메타 검증
/tlb <target> --lens solid        → SOLID 5-lens 검증
/tlb <target> --lens <any>        → KG에 등록된 임의 렌즈셋
```

## 실행 지침

`$ARGUMENTS`를 그대로 `/taliban` SKILL.md로 넘겨 검증 사이클 실행.

**본문**: `/Users/lagyeongjun/CD/SERVER/.claude/skills/taliban/SKILL.md`

Claude는 본 skill 진입 시 **즉시 `/taliban` SKILL.md를 Read**하고, `--lens` 파라미터에 맞는 LensSet의 재배맨 SubagentTaskSpec 씨앗을 KG에서 조회하여 병렬 출격.

# KG: ATOM_Skill_taliban, alias-of-taliban
