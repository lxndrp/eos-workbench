---
name: eos-issue-delivery
description: Deliver a ready EOS Workbench development issue in an isolated worktree through implementation, verification and a linked PR. Use for requested implementation or closeout, not for editorial content or read-only planning.
---

# EOS issue delivery

Read the repository's AGENTS.md and docs/development.md before acting.
They define authority, risk, executable checks and closeout; this skill adds no permissions.

1. Read the live issue, comments, Project, dependencies, linked PRs and Git/worktree state. Confirm acceptance criteria and scope; resolve concrete readiness gaps before editing. Reuse an existing matching implementation rather than create competing work.
2. Use the issue's isolated task, branch and worktree. Preserve unrelated changes. Keep implementation bounded by the issue and record material discoveries there.
3. Apply eos-quality-triage when selecting checks. Read commands from the development guide. Separate unavailable evidence from failed evidence; do not invent tests or successful results.
4. Create a PR with the correct closing or non-closing link and populated issue metadata. Re-read the link and metadata, wait for CI on the current revision and inspect all relevant findings. Address findings before resolving their threads.
5. Deliver the verified PR for the explicit merge decision required by AGENTS.md. A ready PR is not a merged issue. After an authorized merge, verify follow-up CI and issue/Project state before closeout. Inspect residual changes before targeted cleanup; leave task archival to the maintainer.

Goal metrics are optional and must come from actual tool output when available.
Do not extend a software-development task into content approval, publication, deployment or skill installation.
