---
type: Convention
title: VerificationRun
governs: VerificationRun
path: verification-runs/
fields:
  required:
  - title
  optional:
  - verdict
  - assurance
  - artifact_revision
  - source_revision
  - input_manifest
  - toolchain
  - evidence_uri
  - elapsed_seconds
  - job_seconds
  - token_count
  - cost_usd
  values:
    verdict:
    - accepted
    - rejected
    - error
    - not_run
    assurance:
    - kernel_proof
    - symbolic_verification
    - bounded_model_check
    - testing
    - assumption
    - unqualified
  types:
    elapsed_seconds: number
    job_seconds: number
    token_count: integer
    cost_usd: number
links:
  for case: VerificationCase
  checks: Proof Obligation
  discharges: Proof Obligation
---

# VerificationRun

One VerificationRun in the verification pipeline. Read the installed references/verification-pipeline-workflow before assigning evidence or advancing status. Exact statements, input domains and assumptions remain part of the claim.

Case/run conventions preserve existing ids and narrative evidence: only title is required for legacy compatibility. New pipeline records must supply the workflow's identity and classification fields. Labels and links do not establish proof validity, invalidate dependants automatically, or execute tools. New obligation/component required fields enforce a minimum shape; independent review and native checker evidence establish meaning.
