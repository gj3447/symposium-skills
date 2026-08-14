# Jaebaeman error handling

| Failure | Status | Response |
|---|---|---|
| invalid TaskSpec | not dispatched | correct locally; do not guess missing authority |
| timeout | `FAILED` or `PARTIAL` | cancel; use at most the declared retry |
| invalid output | `FAILED` | reject result or request one bounded correction if blocking |
| dependency failure | `BLOCKED` | cancel dependent work |
| write collision risk | `BLOCKED` | serialize or assign one owner |
| external outcome unknown | `PARTIAL` | reconcile by exact readback before retry |
| parent no longer needs result | `CANCELLED` | interrupt and record cancellation |

Partial failure never spawns a sibling automatically. Compensation must be an explicit safe in-scope
action; do not execute stored arbitrary code or Cypher. Preserve all known partial effects in the manifest.
