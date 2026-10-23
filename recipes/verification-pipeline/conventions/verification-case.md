---
type: Convention
title: VerificationCase
governs: VerificationCase
path: verification-cases/
fields:
  required:
  - title
  optional:
  - progress_status
  - assurance
  - source_revision
  - artifact_revision
  - artifact_digest
  - property
  - input_domain
  - semantics
  - assumptions
  - milestone
  values:
    progress_status:
    - proposed
    - in_progress
    - checked
    - needs_recheck
    - archived
    assurance:
    - kernel_proof
    - symbolic_verification
    - bounded_model_check
    - testing
    - assumption
    - unqualified
links:
  requires: Proof Obligation
  supported by: VerificationRun
---

# VerificationCase

One VerificationCase in the verification pipeline. Read the installed references/verification-pipeline-workflow before assigning evidence or advancing status. Exact statements, input domains and assumptions remain part of the claim.

Case/run conventions preserve existing ids and narrative evidence: only title is required for legacy compatibility. New pipeline records must supply the workflow's identity and classification fields. Labels and links do not establish proof validity, invalidate dependants automatically, or execute tools. New obligation/component required fields enforce a minimum shape; independent review and native checker evidence establish meaning.
