# TPA error handling

| Condition | Response |
|---|---|
| parser unavailable/fails | record exact gap; use a valid alternate or return partial |
| target revision changes | stop and restart from a frozen revision |
| manifest mismatch | reconcile denominator before continuing |
| contract evidence conflicts | preserve conflict; do not promote convention |
| pattern uncertain | classify `ALTERNATIVE` or `INCONCLUSIVE` |
| binding target absent | return unresolved proposal |
| external mutation outcome unknown | exact readback before retry |

Retries, research, reviewers, and follow-ups are bounded and explicit. Errors do not auto-create status,
Lessons, ActionPlans, seeds, siblings, or recursive cycles.
