Testing Strategy Alternatives

1) Risk-Based Testing (RBT)
Philosophy: Test where failure hurts most; depth proportional to risk.

Scope and Shape
- Identify high-risk areas by impact x likelihood.
- Deep tests for critical paths; minimal for low-risk.
- Focus on business-critical workflows and data integrity.

Pyramid
- Heavy unit tests for core logic.
- Targeted integration for risky seams.
- Scenario-based end-to-end (E2E) on critical user journeys.

Tooling and Practices
- pytest/jest, contract tests (pact), property tests (hypothesis/fast-check).
- Test impact analysis to prioritize.
- Chaos or fault-injection for high-risk infra paths.

Gates
- Critical paths: 95%+ coverage, mutation score ≥70%.
- Contracts must pass for all consumer/provider pairs.
- Fail build if any high-risk scenario fails.

Cheat-sheet
1. Rank risks
2. Go deep where it hurts
3. Contracts + properties
4. E2E only for critical flows
5. Block on critical failures

2) Contract-First and Interface-Driven
Philosophy: Stability via explicit contracts; test at boundaries.

Scope and Shape
- Define schemas/APIs before code.
- Enforce producer/consumer compatibility.
- Mock at edges, not within modules.

Pyramid
- Unit tests ensure business rules.
- Contract tests dominate mid-layer.
- Few smoke E2E tests to verify wiring.

Tooling and Practices
- OpenAPI + spectral lint, pact for CDC, ajv/pydantic validators.
- API diff checks; schema versioning and backward compatibility tests.
- Generate server/client stubs from contracts.

Gates
- OpenAPI diff breaking → fail merge.
- CDC matrix must be green across supported versions.
- Validators enforce strict mode in CI.

Cheat-sheet
1. Write contract first
2. Generate stubs
3. Unit on rules, contracts on edges
4. Block on breaking diffs
5. Keep E2E as smoke

3) Property-Based and Invariant-Driven
Philosophy: Specify what must always hold, not just examples.

Scope and Shape
- Define invariants, algebraic laws, idempotence, monotonicity.
- Great for parsers, financial calcs, transformations.

Pyramid
- Unit: mix example + property tests.
- Integration: properties across modules (metamorphic tests).
- Minimal E2E; focus on correctness kernels.

Tooling and Practices
- hypothesis (Python), fast-check (JS), ScalaCheck, jqwik.
- Metamorphic testing for ML/heuristics.
- Differential testing against reference implementations.

Gates
- Properties must pass across randomized seeds.
- Mutation testing score ≥70% for critical modules.
- Differential test mismatch → fail immediately.

Cheat-sheet
1. List invariants
2. Encode as properties
3. Randomize inputs
4. Compare with oracle/differential
5. Enforce mutation scores

4) Observability-Backed Testing (Prod-Fidelity First)
Philosophy: Use production reality to drive and validate tests.

Scope and Shape
- Derive test cases from production traces, logs, and user journeys.
- Emulate prod data and traffic patterns in staging.

Pyramid
- Unit tests for logic.
- Integration tests built from real traces (trace-replay).
- E2E canary tests with synthetic monitors.

Tooling and Practices
- OpenTelemetry trace capture + replay harness.
- Snapshot tests with golden data sets anonymized.
- SLO-driven test suites; chaos + load in CI/CD nightly.

Gates
- Trace-replay pass rate ≥99% for top N journeys.
- SLO guardrails in perf tests (p95 latency, error rate).
- Synthetic canaries green before rollout.

Cheat-sheet
1. Capture traces
2. Build tests from reality
3. Replay in CI/staging
4. Enforce SLOs as gates
5. Canary before full traffic

5) Continuous Testing with Trunk-Based Dev (Flow-Optimized)
Philosophy: Keep the main branch always releasable with dense automation.

Scope and Shape
- Small PRs; test suites tiered for speed.
- Shift-left: run most checks locally and on pre-commit.

Pyramid
- Broad, fast unit tests as foundation.
- Focused integration with ephemeral environments.
- Minimal smoke E2E per PR; full E2E nightly.

Tooling and Practices
- Test impact analysis to select tests per change.
- Ephemeral envs via docker-compose/k8s preview; data seeds.
- Parallelized CI, flaky-test quarantine with auto-bisect.

Gates
- PR pipeline ≤10 min or fail for timeouts.
- Line + branch coverage ≥90%; changed files ≥95%.
- Flakiness detector: tests with instability >1% quarantined and ticketed.

Cheat-sheet
1. Tiny PRs, fast lanes
2. Run the right tests (impact-based)
3. Ephemeral envs for integration
4. Smoke E2E on PR, full nightly
5. Quarantine and fix flaky tests

Implementation Notes
- Mix strategies as appropriate: Contract-First + Observability for services; Property-Based for algorithms.
- Add a Test Strategy ADR in docs/adr/ with chosen philosophy, gates, exceptions.
- Bake CI presets: ci-fast.yml (PR), ci-full.yml (nightly), ci-release.yml (pre-release).
