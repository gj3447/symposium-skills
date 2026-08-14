# Naesengmoon error handling

| Condition | Verdict effect | Response |
|---|---|---|
| target revision missing | `INCONCLUSIVE` | request or locate exact target |
| oracle unavailable | usually `INCONCLUSIVE` | record gap; use a valid substitute only if declared |
| reviewer timeout | coverage gap | cancel or one bounded predeclared retry |
| invalid finding schema | no evidential weight | reject and optionally request one correction |
| executor equals required independent reviewer | independence gap | obtain external review or return conditional/inconclusive |
| conflicting evidence | unresolved | preserve both lineages and run one direct discriminator if in scope |
| external outcome unknown | unresolved | exact readback before retry |

Do not auto-approve empty output, but also do not auto-reject merely because a reviewer produced zero
findings. Evaluate the declared checks and evidence. Failures never auto-create a Lesson or recursive run.
