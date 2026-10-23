# Local safe retry admission result, 2026-10-23

PASS for the complete isolated emitted guard under the [explicit numeric, field and heap
boundary](README.md). Exact-change independent review and native Linux evidence follow this
builder record; no production code was changed.

| Analyzed variant | Successful cases | Failed cases | Postcondition failure paths |
| --- | ---: | ---: | ---: |
| Baseline |52|0|0|
| Prefix gap admitted by <= |36|16|16|
| Always deny |36|16|16|
| Always allow |16|36|36|
| Unknown replaced with in-flight |36|16|16|
| Receipt bypass |44|8|16|
| State bypass |44|8|8|
| Equivalent state-order change |52|0|0|

Case identities are checked against the committed case plan using Gillian's structured
verif_results.json, not just progress-line counts. Failures must be postcondition failures;
syntax errors, unsupported semantics, missing fields, solver errors and timeouts do not count.
Always-allow and always-deny jointly exercise every partition as a nonvacuity control.

Each of nine native variants (including layout) has1,512 fixtures. Original/equivalent variants
have zero differences. Gap admission104 differences, always-deny56, always-allow1,456,
unknown-to-inflight56, receipt bypass56 and state bypass140. Projection labels distinguish
captured-field-compatible and defensive inputs without claiming full record validity or
reachability. Receipt-bypass differences are all defensive; they are not current product bugs.
Explicit witnesses retain ambiguous unknown attempts1/prefix0, covered unknown attempts1/prefix1,
in-flight denial, receipt presence and maximum-counter eligibility without a successful-claim promise.

Final first-complete local checker2.1585s summed subprocess stages, excluding archive hashing,
setup and evidence copies. The prior settlement contract regression also passed after shared
executable validation was extracted; its exact local report is retained with this run. Toolchain
archives and dependencies are reused unchanged. Peak memory and per-proof construction token/dollar
cost are not separately instrumented; timings cannot be extrapolated to full async/storage proofs.

## Failed attempts retained

An authoring draft inserted per-case // notes inside the annotation block. Gillian interpreted
those as part of a logical postcondition and rejected the input before analysis. Removing those
notes from the logical block fixed syntax; case names remain in the separately committed case plan.
No behavioral property was changed.

The first integrated run incorrectly expected a single progress marker before each verdict.
Some symbolic cases print intermediate branch success followed by final failure (`s f Failure`).
All expected structured case identities already agreed. A bounded diagnostic confirmed the issue;
the runner now checks final status after any intermediate markers and independently checks all
structured case results. This was a reporting-parser correction, not a solver/source/policy fix.

## Interpretation and reuse

52 contract cases reason over explicit field projections with bounded model-real counters, covering
validated safe-integer values under the documented embedding justification. Defensive null and
inconsistent-state/receipt projections remain labeled. No proof establishes capture/evidence
truthfulness, transition reachability, TypeScript compilation, IEEE754 arithmetic, Node/V8 adequacy,
backend atomicity, async scheduling or end-to-end no-duplicate execution.

Source drift is rejected. A receipt that names forged executable bytes is rejected against the
pinned archive content without executing the fake file. Raw cases, source/emission/annotation hashes,
structured verdicts, native witnesses, exact nine-input hashes and failed attempts are retained in
artifacts/safe-retry-admission-20261023 in the coordinator workspace. The caller mapping is separate
reviewed source evidence, not another verified theorem.
