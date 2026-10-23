---
type: Convention
title: Proof Obligation
governs: Proof Obligation
path: proof-obligations/
fields:
  required:
  - title
  - statement
  - progress_status
  - assurance
  optional:
  - assignee
  - subject_revision
  - spec_revision
  - input_domain
  - assumptions
  - recheck_reason
  values:
    progress_status:
    - open
    - in_progress
    - established
    - refuted
    - needs_recheck
    assurance:
    - kernel_proof
    - symbolic_verification
    - bounded_model_check
    - testing
    - assumption
    - unqualified
links:
  for case: VerificationCase
  depends on: Proof Obligation
  reuses: Proof Component
  supported by: VerificationRun
---

# Proof Obligation

One Proof Obligation in the verification pipeline. Read the installed references/verification-pipeline-workflow before assigning evidence or advancing status. Exact statements, input domains and assumptions remain part of the claim.

Case/run conventions preserve existing ids and narrative evidence: only title is required for legacy compatibility. New pipeline records must supply the workflow's identity and classification fields. Labels and links do not establish proof validity, invalidate dependants automatically, or execute tools. New obligation/component required fields enforce a minimum shape; independent review and native checker evidence establish meaning.
