Stage 0: Initialize + Debug Hooks
Purpose: Baseline repo, enable verbose diagnostics early.
Actions:
- Verify Make targets and CI parity.
- Ensure directories: artifacts/, approvals/, logs/.
- Set DEBUG=1, TRACE=1 env toggles honored by tools.
- Add fast sanity script: make doctor (prints versions, paths, env toggles, network reachability, secrets redaction checks).

Stage 1: Express (No Gate) + Failure Hypothesis
Purpose: Capture 4W1H and initial failure modes.
Command:
- make express ARG="Short title or ticket ID"
Outputs:
- artifacts/express.md
- artifacts/assumptions.md
Add:
- artifacts/failure_hypothesis.md (suspected breakpoints, invariants, observability signals, known flakey areas).

Stage 2: Ask (Gate A) + Repro Criteria
Purpose: Validate scope and agree on minimal repro + exit criteria.
Command:
- make ask-gate APPROVE=1
Inputs:
- artifacts/assumptions.md, artifacts/failure_hypothesis.md
Outputs:
- approvals/assumptions.approved
Adds Gate criteria:
- Repro steps documented, dataset/fixtures defined, acceptance signals and failure signals listed.

Stage 3: Explore (Parallel) + Instrument
Purpose: Collect context and wire temporary debug instrumentation.
Commands:
- Full: make -j explore
- Sub: make context | make research | make risks
Outputs:
- artifacts/context.md, artifacts/research.md, artifacts/requirements.md, artifacts/risks.md
Add:
- artifacts/instrumentation_plan.md (where to log/trace, feature flags, sampling plan, PII handling).
- artifacts/observability_gaps.md (missing metrics/traces/logs; suggested additions).

Stage 4: Plan (Gate B) + Debug Plan
Purpose: Design plus debug strategy and rollback.
Command:
- make plan
Inputs:
- context.md, research.md, requirements.md, risks.md, instrumentation_plan.md
Outputs:
- artifacts/plan.md
- artifacts/test_plan.md
- artifacts/rollback_plan.md (feature flags, migration backout, data repair steps)
Adds Gate criteria:
- Debug plan reviewed; log keys, redaction, and sampling approved.

Stage 5: Code + Feature Flags + Guardrails
Purpose: Implement with toggles and diagnostics.
Guidance:
- Introduce feature flags for risky paths; default off.
- Add structured logs with correlation IDs and request IDs.
- Guardrails: input validation, rate limits, circuit breakers where relevant.
Notes:
- Keep debug knobs controllable via env/flags; document in instrumentation_plan.md.

Stage 6: Test (Gate C) + Repro/Flake Focus
Purpose: Quality gates plus reproducibility and flake detection.
Command:
- make qa
Behavior:
- Run tests with DEBUG=1 to surface hidden issues.
- Capture failing seeds for property/fuzz tests.
- Re-run flaky tests N=5 with jitter; emit artifacts/flake_report.md if flakiness > threshold.
Gate criteria:
- Lint/format pass, tests pass, coverage ≥ 80% or justified.
- Repro script present: scripts/repro.sh or make repro.

Stage 7: Trace & Perf Snapshot (Conditional)
Purpose: Capture traces/pprof/profile on hot paths.
Commands:
- make profile or make trace
Outputs:
- artifacts/profile.md, logs/profiles/*, logs/traces/*

Stage 8: Security & Data Handling (Conditional)
Purpose: Validate security-specific controls relevant to change.
Commands:
- make security or make sast
Outputs:
- artifacts/security.md (threat model deltas, authz/authn changes, secrets handling).

Stage 9: Write-up + Debug Appendix
Purpose: PR narrative with debug learnings and ops notes.
Command:
- make writeup
Outputs:
- artifacts/writeup.md
- artifacts/debug_appendix.md (repro, flags, logs to check, dashboards, runbooks touched).

CI Parallelization & Debug Artifacts
Local:
- DEBUG=1 make -j explore; iterate with make repro.
CI:
- Store logs/ and artifacts/ as build artifacts.
- Matrix: explore, qa (retries for flake), security (if enabled), profile (if enabled).

Governance
- Commit artifacts/, approvals/, logs/ where policy allows.
- No secrets; ensure redaction in logs.
- Sunset debug flags after stabilization; track in rollback_plan.md.
