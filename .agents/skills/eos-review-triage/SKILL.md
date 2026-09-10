---
name: eos-review-triage
description: Assess EOS Workbench review findings using evidence, user impact and duplicate checks. Use for human or automated review reports; it does not implement fixes or write GitHub findings unless the request authorizes those actions.
---

# EOS review triage

Read AGENTS.md, docs/development.md, the reviewed revision and existing issues.

1. Separate observations from confirmed findings. For each actionable finding identify location, behavior, evidence, impact and remaining uncertainty.
2. Check existing issues before proposing a new one. Keep the issue backlog canonical; a review report is supporting evidence rather than a second task list.
3. Distinguish in-scope fixes from follow-up work and questions requiring a decision. Do not invent editorial rules or expand the content model.
4. Draft a concise measure with acceptance criteria. Write it to GitHub or implement it only within the user's actual authorization; a review request alone remains read-only.
5. Do not resolve a PR thread until its finding is understood and addressed. Recheck changed revisions. Automated review does not replace the human review or merge approval required by AGENTS.md.
