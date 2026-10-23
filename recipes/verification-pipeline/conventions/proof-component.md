---
type: Convention
title: Proof Component
governs: Proof Component
path: proof-components/
fields:
  required:
  - title
  - statement
  - progress_status
  - assurance
  optional:
  - symbol
  - artifact_revision
  - artifact_digest
  - artifact_uri
  - toolchain
  - assumptions
  - reuse_scope
  values:
    progress_status:
    - candidate
    - checked
    - needs_recheck
    - retired
    assurance:
    - kernel_proof
    - symbolic_verification
    - bounded_model_check
    - testing
    - assumption
    - unqualified
links:
  reuses: Proof Component
  supported by: VerificationRun
---

# Proof Component

One Proof Component in the verification pipeline. Read the installed references/verification-pipeline-workflow before assigning evidence or advancing status. Exact statements, input domains and assumptions remain part of the claim.

Case/run conventions preserve existing ids and narrative evidence: only title is required for legacy compatibility. New pipeline records must supply the workflow's identity and classification fields. Labels and links do not establish proof validity, invalidate dependants automatically, or execute tools. New obligation/component required fields enforce a minimum shape; independent review and native checker evidence establish meaning.
