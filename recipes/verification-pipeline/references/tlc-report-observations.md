---
type: Reference
title: Retained TLC report observations
resource: urn:superbee:verification:tlc
target_kind: VerificationRun
identity:
  id: "{key}"
fields:
  observed_status:
    from: verification.reported_status
    values:
      reported_pass: reported_pass
      reported_fail: reported_fail
    unmapped: refuse
  observed_input_match:
    from: verification.input_match
    values:
      matches: matches
      mismatch: mismatch
    unmapped: refuse
  observed_report_digest: verification.report_digest
  observed_artifact_revision: verification.artifact_revision
  observed_source_revision: verification.source_revision
  observed_variant_count: verification.variant_count
  observed_expected_variant_count: verification.expected_variant_count
  observed_report_completion:
    from: verification.report_completion
    values:
      complete: complete
      partial: partial
    unmapped: refuse
  observed_source_check: verification.reported_source_check
  observed_association:
    from: verification.association
    values:
      caller_asserted: caller_asserted
    unmapped: refuse
owned_fields:
  - observed_status
  - observed_input_match
  - observed_report_digest
  - observed_artifact_revision
  - observed_source_revision
  - observed_variant_count
  - observed_expected_variant_count
  - observed_report_completion
  - observed_source_check
  - observed_association
auto_apply: [new, changed]
needs_review: [disappeared]
completeness: partial
---

# Retained TLC report observations

This is an inert snapshot declaration for the separately acquired and reviewed
[verification local-operation plugin](https://github.com/Holaxis-ai/superbee-plugins/tree/main/integrations/verification).
Recipe installation never registers code, binds this source, executes a checker or imports a report.
The optional observed_* fields are machine observations, separate from reviewed verdict, assurance,
source/artifact revisions, body, statement and discharge decisions. No proof admission is automated.

For deliberate adoption, use executable CLI 0.4.4-pre.3 / Core 0.2.0-pre.38 and the plugin's documented
closed resource plan. Install the canonical source-feeds recipe for its Signal convention if absent.
Register reviewed plugin bytes, explicitly bind captured input files and export the snapshot. Add
an explicit sources entry to the chosen existing VerificationRun, with this resource and the
caller-selected stable runKey as id. Preview and accept native source snapshot bind/run for
references/tlc-report-observations. No mirrored run or proof graph is created.

A reported_pass means that a retained native report passed consistency/identity checks against a
caller-selected original plan. Selected files are hashed now; neither that observation nor the
historical reported_source_check flag establishes past checker consumption or a TypeScript proof.
A partial failed report remains reported_fail with expected/observed counts. Freshness covers only
explicit original inputs and required archive identity, not unrecorded assumptions or dependency
changes. Preserve original runs, raw reports, failed attempts, exact scope and independent review.
Replay, generations, conflicts and snapshot freshness use Core's existing machinery. The adapter
does not monitor sources, invalidate dependants or schedule checks. Source declaration/owned-field
changes require an explicit reviewed rebind; installation alone grants no execution authority.
