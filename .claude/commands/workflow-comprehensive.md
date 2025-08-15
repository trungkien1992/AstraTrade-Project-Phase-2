

Stage 0: Initialize
Purpose: Ensure repo tooling, Make targets, CI, and artifact directories exist.
Actions:
- Verify `Makefile` targets exist locally and in CI.
- Ensure directories: `artifacts/`, `approvals/`.
- Ensure CI jobs: Ask Gate, Explore (matrix), Plan, QA, Write-up.

Stage 1: Express (No Gate)
Purpose: Capture 4W1H, initial assumptions, and scope hypothesis.
Command:
- make express ARG="Short title or ticket ID"
Outputs:
- artifacts/express.md (4W1H scaffold, scope hypothesis, constraints known)
- artifacts/assumptions.md (assumptions, open questions, unknowns, risks seen)
Notes:
- Keep concise. Link to ticket/ADR references and any related RFCs.

Stage 2: Ask (Gate A)
Purpose: Validate assumptions, scope, constraints, and NFRs with reviewers/stakeholders.
Command:
- make ask-gate APPROVE=1
Inputs:
- artifacts/assumptions.md
Outputs:
- approvals/assumptions.approved (reviewed and signed-off assumptions)
Gate criteria:
- approvals/assumptions.approved exists and is current.
Checklist (minimum):
- Scope boundaries confirmed (what’s in/out).
- Non-functional requirements captured (performance SLAs, latency, throughput, cost).
- Integration constraints and data ownership clarified.
- Acceptance criteria format agreed (for later test planning).

Stage 3: Explore (Parallel)
Purpose: Gather internal context, curated external research, requirements, and risks concurrently.
Commands:
- Full: make -j explore
- Subagents: make context | make research | make risks
Outputs:
- artifacts/context.md (internal code paths, modules, tickets, ADRs, architecture diagrams)
- artifacts/research.md (curated external sources; brief annotations; follow research policy)
- artifacts/requirements.md (functional + NFRs; acceptance criteria traceable to tests)
- artifacts/risks.md (risks, mitigations, edge cases, rollback/kill switches, observability plan)
Gate:
- All above files present and substantive; reviewers skim for completeness before Plan.
Notes:
- Include performance/load expectations, data migration implications, and operational runbook notes.
- For event systems: capture schema governance, retention, back-pressure, replay strategies.

Stage 4: Plan (Gate B: Design Review)
Purpose: Produce a concrete design and test strategy; get design approval before coding.
Command:
- make plan
Inputs:
- context.md, research.md, requirements.md, risks.md
Outputs:
- artifacts/plan.md (architecture, components, sequence diagrams, data schemas, decisions/trade-offs)
- artifacts/test_plan.md (test types, data sets, coverage targets, negative tests, perf/security scope)
- artifacts/ux_checklist.md (if UI present)
Gate criteria:
- Reviewer sign-off on plan and test approach (comment link or internal approval logged in plan.md).
- Conflicts resolved; any deviations from ADRs explicitly justified.

Stage 5: Code
Purpose: Implement per plan; keep artifacts current.
Guidance:
- Commit incrementally; update artifacts to reflect reality.
- Add or modify ADRs as needed; cross-link from plan.
- Maintain backward compatibility and feature toggles when applicable.
Notes:
- If scope shifts, update assumptions, requirements, plan, and risks with diffs.

Stage 6: Test (Gate C: Quality)
Purpose: Enforce code quality, coverage, and test success; optionally include performance/security tests.
Command:
- make qa
Behavior:
- Auto-detect format/lint/test tools (Node/nyc, Python/coverage.py+pytest, Go, Maven/Jacoco).
- Enforce ≥ 80% line coverage when measurable.
- If coverage not measurable, CI fails with guidance; temporary override via DISABLE_COVERAGE_GATE=true with justification.
Gate criteria:
- Format/lint pass (if tools present).
- Unit/integration tests pass.
- Coverage ≥ 80% when measurable, or approved override is set and documented in test_plan.md.
Optional sub-stages (triggered by requirements):
- Performance: baseline + target SLAs, regression thresholds, artifacts/perf.md summary.
- Security: basic SAST/DAST or dependency checks; artifacts/security.md summary.
Notes:
- Attach coverage reports and summarize gaps in test_plan.md.

Stage 7: Write-up
Purpose: Assemble PR description from artifacts; ensure traceability.
Command:
- make writeup
Output:
- artifacts/writeup.md
Include:
- Objective, summary of key choices, tests run, risks/mitigations, ops notes, and useful commands.
- Links to artifacts and approvals.

Parallelization: Local vs CI
Local:
- make -j explore for parallel collection.
- Work incrementally; keep artifacts updated.
CI (GitHub Actions):
- Ask Gate job validates approvals/assumptions.approved.
- Explore matrix runs [context, research, risks]; commits artifacts.
- Plan job synthesizes plan.md and test_plan.md; commits updates.
- QA enforces linters, tests, coverage gate.
- Write-up produces artifacts/writeup.md; uploads as artifact.

Artifacts and Governance Policy
- Commit artifacts/ and approvals/ on feature branches.
- Keep artifacts updated as understanding evolves; do not delete unless policy dictates archiving.
- No secrets or proprietary external content; link to sensitive docs instead.
- For schema or interface changes, include versioning, migration notes, and deprecation timelines.

Related Workflows and Guides
- Debug-inclined workflow: .claude/commands/workflow-comprehensive-debug.md
- Lean hypothesis workflow: .claude/commands/workflow-lean-hypothesis.md
- Testing strategies: .claude/commands/testing-strategies.md
- Cleanup routine: .claude/commands/cleanup-routine.md

Implementation Plan for Your Event Bus Initiative
- Phase 1 (Stages 1–3): Direct execution to maximize context capture across six domains, verify cross-domain schemas, performance constraints, and Redis Streams options. Produce acceptance criteria aligned with ADR-007.
- Reassess after Stage 3: If stable and well-scoped, consider sub-agent to accelerate Stages 4–7; otherwise continue direct execution to preserve domain continuity.

Decision
- Adopt the revised gates and artifacts.
- Start with direct execution for Stages 1–3, then reassess sub-agent usage for implementation.