Codebase Clean-up Routine (Fast, Safe, Auditable)

1) Prep and Scope
- Create short-lived branch: git checkout -b chore/cleanup-<date>
- Tag baseline: git tag cleanup-base-<date>
- Inventory:
  - git ls-files > .artifacts/files-before.txt
  - du -sh . | tee .artifacts/repo-size-before.txt
Exit: Branch created, baseline artifacts exist.

2) Dead Code and Asset Pruning
- Static reachability:
  - JS/TS: ts-prune, depcheck
  - Python: vulture, ruff --select F401,F841
  - Java/Kotlin: gradle -q dependencies, jdeps
  - Go: go vet, staticcheck, gocov
- Runtime reachability: enable coverage in staging; collect unused endpoints/functions.
- Remove/quarantine to dead_code/ with justification.
- Large assets: git lfs migrate info; move to LFS or artifact storage.
Exit: No unused symbols/modules or documented quarantine.

3) Dependency Hygiene
- Remove unused deps:
  - JS/TS: npx depcheck
  - Python: pip-chill, pipdeptree
  - Java: mvn dependency:analyze
- Update pinned versions:
  - JS: npm outdated && npx npm-check-updates -u && npm i
  - Python: pip-compile --upgrade
- Security: npm audit --audit-level=high, pip-audit, osv-scanner
Exit: No unused deps; audits clean for CVSS <7; lockfiles updated.

4) Lint, Format, Types
- Lint zero warnings: eslint . --max-warnings=0; ruff check . --select ALL --ignore <agreed>
- Format: prettier . --write; black .; isort .
- Types: tsc --noEmit; mypy .
Exit: Lint clean; no diffs after second formatter run; typecheck clean.

5) Tests and Coverage Hardening
- Remove obsolete tests; seed randomness and freeze time.
- Coverage ≥90% line+branch; changed files ≥95%.
- Mutation testing on critical modules: mutmut/stryker.
- Quarantine flaky tests and ticket.
Exit: Tests green; thresholds met; no flakies in PR.

6) Build Outputs and CI Slim
- Clean build artifacts: dist/, build/, .pytest_cache/, node_modules/.cache/
- CI speedups: cache by hash; dedupe steps; split ci-fast.yml vs ci-full.yml; remove legacy jobs.
Exit: PR CI ≤10 min; nightly ≤60 min; no unused CI jobs.

7) Docs, Comments, Conventions
- Update OpenAPI/README/CHANGELOG; ADRs for cleanup.
- Resolve TODO/FIXME/XXX or ticket and link.
- Delete commented-out code; enforce naming and structure; merge duplicate utils.
Exit: No stale docs or unresolved TODOs; cohesive naming.

8) Configuration and Secrets
- Centralize config: .env.example; validate with schema.
- Secrets: gitleaks detect; rotate exposed keys; move to secret manager.
- Prune env-specific configs; keep per-env overlays.
Exit: No secrets in repo; config validated; least privilege intact.

9) Performance Footprint Cleanup
- Profile with hyperfine/autocannon/ab or language-specific tools.
- Fix N+1, allocations, redundant serialization.
- Asset optimization: tree-shake, code-split, compress images, purge unused CSS.
Exit: No regression vs baseline; ideally ≤3% improvement in p95 or bundle size.

10) Legal and Licensing
- SBOM: syft . -o json > sbom.json
- License scan: fossa analyze or scancode-toolkit
- Update NOTICE and third-party acknowledgments.
Exit: License compliance confirmed; SBOM attached.

11) Git History and Repository Maintenance
- Consolidate commits: git rebase -i to squash fixups.
- Remove large blobs only if needed: git filter-repo; force-push cautiously.
- Prune branches: delete merged stale; archive long-lived.
Exit: Clean history for PR; no orphaned branches.

12) Final Gate and Merge
- Full validation: SAST/SCA/DAST green; perf guardrails; typos + markdownlint; API contract diffs vetted.
- Human rule: reject "good enough for now".
Exit: All gates pass; merge; tag cleanup-<date>.

Starter (JS/TS)
- npx depcheck
- npx ts-prune
- npm audit --audit-level=high
- eslint . --max-warnings=0
- prettier . --write
- tsc --noEmit
- npm test -- --coverage
- npx stryker run
- gitleaks detect
- typos
- markdownlint '**/*.md'
- hyperfine 'npm run build' --warmup 2

PR Artifacts
- .artifacts/files-before.txt, repo-size-before.txt
- Coverage and mutation reports
- SBOM (sbom.json)
- License scan report
- Perf comparison output
- ADR for cleanup decisions in docs/adr/
