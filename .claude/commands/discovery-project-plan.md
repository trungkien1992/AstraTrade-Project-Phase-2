Discovery Project Plan (1–2 weeks)

1) Task Brief
Goal: Validate problem-solution fit and feasibility; deliver evidence and a recommendation.
Success criteria:
- Problem statement and target user segment agreed by stakeholders.
- Top 3 user journeys mapped with pain points/opportunities.
- Tech feasibility proven via spike (runs locally, basic happy path).
- Risk register (top 10) with mitigations and costed options.
- Decision memo: proceed, pivot, or stop with next-step plan.
Constraints: Timebox 10 business days; prototype-only budget; use existing infra where possible.
Stakeholders: Product lead (D), Eng lead (A), Design (C), Data/Sec/Compliance (C/I), Sponsor (A).

2) Work Plan (3–5 tracks)
Track-1: Understand users and problem
- Outcome: problem definition doc
- Steps: 5 interviews, analyze existing data, synthesize JTBD
Track-2: Map current flow and architecture
- Outcome: context + system diagram
- Steps: inventory APIs/data, env constraints, integration points
Track-3: Prototype critical path
- Outcome: runnable spike
- Steps: pick slice, stub deps, implement happy path, measure latency
Track-4: Risk and compliance assessment
- Outcome: risk register
- Steps: security scan, data classifications, regulatory flags
Track-5: Decision package
- Outcome: memo + demo
- Steps: synthesize findings, cost/schedule, recommendation, record demo

3) Risks and Assumptions
Risks
- Access to users delayed → pre-schedule, prepare scripts
- Integration complexity → sandbox mocks; contract-first
- Security/compliance blockers → early data classification and DPIA
- Unknowns in legacy systems → allocate spike time and involve owners
- Time overrun → scope to one critical journey
Assumptions
- Stakeholders available for 2 checkpoints/week
- Access to dev environment and test data
- Prototype may be throwaway
- Scope limited to 1–2 personas and 1 core journey
- No production data in prototypes

4) Cadence and Checkpoints
- Kickoff (Day 0): align goals, criteria, risks, schedule
- Midpoint review (Day 5): early findings, spike status; cut scope if needed
- Final demo + decision (Day 10): memo, demo, roadmap options

5) Quality Plan
- Evidence: interview notes, analytics snapshots
- Prototype: tests on core logic, README with run steps, perf check
- Docs: ADRs for key decisions; traceability insights → requirements

6) Deliverables (docs/discovery/)
- problem-statement.md
- user-journeys.md
- arch-overview.md
- spike/ (runnable prototype + README)
- risk-register.md
- decision-memo.md
- Optional: recorded demo link

7) Example 10-day timeline
- Day 1–2: Interviews + data review; draft problem
- Day 3: Architecture/integration mapping; pick slice
- Day 4–6: Build spike; mocks; early perf/security checks
- Day 7: Validate with users/stakeholders; adjust
- Day 8: Risk register; cost options; draft roadmap
- Day 9: Finalize docs; dry-run demo
- Day 10: Demo + decision; archive artifacts

8) Ready-to-use checklists
Interview readiness
- Scripts approved
- Target users recruited
- Consent/recording setup
- Note-taking template ready
Prototype readiness
- Repo scaffolded
- Contracts defined (OpenAPI/schema)
- Mocks/stubs available
- Seed/test data prepared
Decision memo contents
- Problem and evidence
- Alternatives considered
- Tech feasibility summary
- Risks and mitigations
- Costs, timelines, resourcing
- Recommendation and next steps
