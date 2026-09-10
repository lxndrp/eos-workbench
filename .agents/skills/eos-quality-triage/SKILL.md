---
name: eos-quality-triage
description: Select and run proportionate checks for EOS Workbench changes using their risk and affected contracts. Use before reporting an implementation as verified or when deciding which checks a change needs.
---

# EOS quality triage

Read AGENTS.md, docs/development.md, the changed paths and the relevant CI workflow.

1. Classify risk by changed behavior and contracts, not just file extensions. Use the Project's live Complexity and the repository's rules for missing values or higher discovered risk.
2. Select the documented checks that can produce evidence for this change. Narrow documentation changes need whitespace and local links; skills, templates, validators and CI require their relevant structure and regression checks. Never infer a future application's test commands from the process tooling.
3. Run the selected checks and record their revision, result and material omissions. If local execution is blocked, identify the missing evidence and use available CI evidence without presenting it as a local pass.
4. For persistent failures, capture a focused reproduction and distinguish product, test, CI/toolchain and environment causes. Do not weaken a gate or repeat an unchanged broad failure to manufacture success.
5. Repeat affected checks after relevant changes. Structural skill validation does not prove behavior, and an accessibility scan does not prove usability. Add the focused behavioral review when the change requires it.

Read-only requests authorize analysis of check selection, not implementation of a fix.
