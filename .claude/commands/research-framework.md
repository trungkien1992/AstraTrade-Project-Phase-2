Lean Codebase Research Framework (≤2 days)

Phase 0: Setup and Snapshot
- Clone and baseline
  - git clone <repo>; git fetch --all --tags
  - git status; git log --oneline -n 50; git tag -l
- Fast health probes
  - README, CONTRIBUTING, docs/adr/, LICENSE
  - Try build/test: make help; make test; ./scripts/dev
- Produce snapshot artifacts
  - tree -L 2 > .research/tree.txt
  - git shortlog -sn > .research/authors.txt
  - git ls-files > .research/files.txt
  - du -sh . > .research/size.txt
Deliverable: .research/README.md with repo metadata and how to build/test.

Phase 1: Architecture Recon
- High-level structure
  - Identify entrypoints: main functions, Dockerfile, Procfile, k8s manifests.
  - Map services/packages: module boundaries, directories, ownership docs.
- Runtime topology
  - Search for network calls, queues, storage: grep -R "http|grpc|kafka|sns|sqs|redis|mongo|postgres" -n .
  - Extract env config and secrets usage.
- Generate diagrams
  - dependency-cruiser (JS/TS), pydeps (Python), go list -deps (Go), jdeps (JVM).
  - Output to .research/diagrams/ with a short legend.
Deliverable: docs/arch/overview.md + a context/container diagram and module graph.

Phase 2: Domain and Data Understanding
- Domain glossary
  - Extract ubiquitous language from code: entity names, aggregate roots, core flows.
  - Build a mini-glossary in .research/domain.md.
- Data contracts
  - Collect schemas: OpenAPI, GraphQL SDL, DB migrations, Avro/Proto files.
  - Snapshot representative payloads and migrations to .research/samples/.
- Critical paths
  - Trace the top 3 user journeys end-to-end.
Deliverable: docs/flows/top-flows.md with sequence steps and involved modules.

Phase 3: Quality Signals and Risks
- Tests and coverage
  - coverage/nyc/jacoco reports; mutation test if feasible on a module.
  - Map untested hotspots: high complexity + low coverage.
- Security and compliance
  - Run gitleaks, osv-scanner/npm audit/pip-audit, SAST (semgrep, bandit, spotbugs).
  - Note data handling for PII/PHI and encryption at rest/in transit.
- Ops and performance
  - Check logging, metrics, tracing setup (OpenTelemetry, Prometheus).
  - Build/perf baseline: hyperfine build; note p95 targets if present.
Deliverable: .research/risk-register.md with risks, severity, mitigations.

Phase 4: Dependency and Build Graph
- Dependency inventory
  - SBOM: syft . -o table > .research/sbom.txt
  - Outdated libs: npm outdated / pip list --outdated / mvn versions:display-dependency-updates
- Build and CI
  - Read .github/workflows/, Jenkinsfile, gitlab-ci.yml
  - Note gates, caches, flaky tests, long poles, secrets usage.
Deliverable: .research/ci-build.md with pipeline map and improvement candidates.

Phase 5: Contribution Map and Ownership
- Ownership
  - CODEOWNERS; infer with git blame, git shortlog, git fame.
- Change hotspots
  - git log --name-only --since="12 months ago" | sort | uniq -c | sort -nr | head -100 > .research/hotspots.txt
  - Pair with complexity (radon, sonarqube, eslint complexity rule)
Deliverable: .research/ownership.md + hotspots.txt annotated with context.

Phase 6: Interactive Exploration (Optional)
- Start app locally with realistic data
  - Use seed scripts or anonymized dumps.
- Trace-driven discovery
  - Enable tracing; perform key flows; export traces.
  - Build a trace-to-code map for the top flows.
Deliverable: .research/trace-notes.md with spans ↔ files/functions.

Phase 7: Synthesis and Next Steps
- 1-page brief
  - What it does, architecture, key dependencies, main risks, and low-effort/high-value improvements.
- Backlog seeds
  - 5–10 tickets: e.g., add OpenAPI diff gate; replace deprecated libs; refactor hotspots; add missing observability.
- Knowledge handoff
  - 10–15 min walkthrough recording.
Deliverable: docs/adr/000-research-findings.md and link to walkthrough.

Toolbox
- JS/TS: depcruise, ts-prune, depcheck, eslint --print-config, npm audit, stryker, nyc, autocannon
- Python: pipdeptree, pydeps, bandit, ruff, mypy, pytest --cov, hypothesis, radon
- JVM: jdeps, spotbugs, jacoco, archunit, mvn versions:..., gradle deps, gatling
- Go: go list -deps, staticcheck, go test -cover, benchstat, hey
- Infra: terraform graph, tflint, checkov, kube-score, kubectl tree

Starter .research/README.md template
Repo purpose
How to build and run
Architecture summary
Key flows
Quality and risk snapshot
CI/build overview
Ownership and hotspots
Next steps
