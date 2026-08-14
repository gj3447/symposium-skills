# Prometheus error handling

| Condition | Record | Bounded response |
|---|---|---|
| source unavailable | missing source and impact | try one declared alternative or return `INCONCLUSIVE` |
| subtask timeout | task ID and partial output | cancel or one predeclared retry |
| invalid output schema | validation errors | reject result; request one corrected response if blocking |
| contradictory evidence | both lineages | preserve conflict and seek a direct discriminator if in scope |
| duplicate evidence | dependence group | deduplicate; do not count as corroboration |
| tool or KG unavailable | exact failure | continue locally when safe; never bootstrap writes |
| external outcome unknown | attempted action | reconcile by exact readback before retrying |

Do not react to failure by automatically creating a Lesson, sibling agent, ActionPlan, KG record, or new
research cycle. RootCause/Lesson proposals require demonstrated cause and reusable prevention.
