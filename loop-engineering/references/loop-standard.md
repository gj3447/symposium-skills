# Production loop interoperability profile

There is no single ratified cross-vendor “loop engineering standard.” This profile conservatively synthesizes current official runtime contracts and SYMPOSIUM canon.

## Control and stopping

- OpenAI Agents SDK documents an explicit model/tool/handoff loop, resumption from `RunState`, and `max_turns` exhaustion: <https://openai.github.io/openai-agents-python/running_agents/>.
- Anthropic's agent guidance favors simple composable patterns, environmental feedback, stopping conditions, checkpoints, and distinct evaluator-optimizer roles: <https://www.anthropic.com/engineering/building-effective-agents>.
- Anthropic's 2026 long-running application harness reports planner/generator/evaluator contracts and testable sprint behaviors, while warning that a larger harness is costly and should be simplified by removing assumptions: <https://www.anthropic.com/engineering/harness-design-long-running-apps>.

These are product/runtime examples, not proof that one vendor loop is universal.

## Durability and effects

- Temporal distinguishes durable workflow execution, event history/replay, activities, retries, timeouts, and typed closed statuses: <https://docs.temporal.io/workflow-execution>.
- LangGraph persistence and interrupts document step checkpoints, resume behavior, and the requirement that pre-interrupt effects be idempotent because work may execute again: <https://docs.langchain.com/oss/python/langgraph/persistence> and <https://docs.langchain.com/oss/python/langgraph/interrupts>.
- Google ADK documents event-mediated execution and at-least-once tool semantics on resume: <https://adk.dev/runtime/event-loop/> and <https://adk.dev/runtime/resume/>.

Checkpoint availability does not imply deterministic replay or exactly-once effects.

## Human gates and traces

- OpenAI Agents SDK human-in-the-loop serializes run state around approvals: <https://openai.github.io/openai-agents-python/human_in_the_loop/>.
- Its tracing surface records agent, model, tool, handoff, and guardrail spans and exposes sensitive-data controls: <https://openai.github.io/openai-agents-python/tracing/>.

Bind approval to immutable action content and treat checkpoint/trace stores as security boundaries.

## Evaluation

Use deterministic ground truth where possible. Automated judges need labeled calibration, held-out cases, independent evidence, uncertainty/gray-band handling, and periodic human audit. Different models may still share correlated errors; cross-model voting is supplementary, not independence proof.

## Local research basis

`THEORY/harness_loop_engineering/PROM_16_REPORT.md` and its A–D sourcebooks cover the 3-tier Harness family, loop patterns, context/compaction, reliability guards, observability, and operations. They are industry research synthesis, not direct user-authored canon. This skill crystallizes a short operational protocol from that material while preserving the provenance boundary.
