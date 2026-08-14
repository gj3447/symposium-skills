# APT error handling

| Condition | Response |
|---|---|
| missing phase input | `RETURN` with exact missing artifact |
| ambiguous contract | `INCONCLUSIVE` or request the material choice |
| relevant check fails | `BLOCK` or return to owning phase with evidence |
| tool unavailable | run one valid alternative or report blocker |
| reviewer unavailable | continue only if independence was not required |
| partial parallel work | preserve partial results; cancel dependent tasks |
| external outcome unknown | reconcile with exact readback before retry |
| write collision or foreign drift | stop and preserve ownership boundary |

Retries, waits, parallelism, and follow-ups are bounded. Do not auto-spawn research, reviewers, Lessons,
ActionPlans, or status changes because an error occurred.
