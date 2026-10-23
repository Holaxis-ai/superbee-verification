# Verification experiment

Read experiments/PIPELINE-MILESTONE.md before selecting new research work. The current milestone
is a substantial actual implementation property and demonstrated proof-component reuse on a second
implementation target; another isolated helper or bounded abstract model does not complete it.
Use recipes/verification-pipeline and the existing selected bundle for obligations, dependencies,
exact runs and coordination. Its recipe does not execute checks or automatically invalidate evidence.

This repository owns experimental proof artifacts, not Superbee production behavior. Product
source and normal CI live in Holaxis-ai/superbee; work coordination lives in the existing selected
superbee-dev bundle. Do not initialize another bundle here or add a product CI dependency.

Read README.md and experiments/journal-retirement/README.md before changing a theorem or claim.
Use the pinned Lean version and python3 scripts/check.py; no Mathlib is required. For source
bridge work also read experiments/source-classifier/README.md and run scripts/check_source_decode.py
with the pinned source; it includes the pinned-parser checker and independent byte decoding.
Do not describe a source-derived semantic proof as verified TypeScript or binary execution. Preserve
counterexamples and report axiom dependencies, exact inputs, failed attempts and scope limits.
Do not use proof placeholders, custom axioms, or weaken an intended property to obtain a pass.
A failed proof is not an implementation bug; a checked abstract theorem is not a TypeScript proof.

Keep CI manual until a separate adoption decision. Do not add automatic triggers, large generated
proofs, binary artifacts, or a required product gate without an explicit cost/scope decision.
Proof checking does not replace independent review of statement usefulness and source mapping.

Public proof work must not disclose exploitable production findings. Use the product repository's
private security advisory route for sensitive findings; public records carry sanitized status only.

For established-tool settlement work, read experiments/gillian-settlement/README.md and
experiments/VERIFICATION-PATH.md. Use scripts/setup_gillian.py and scripts/check_settlement.py
with the pinned archives/source. Preserve all four independent contract cases, real postcondition
failures for the three semantic mutants, the equivalent-null-check passing control and exact
input/tool identities. Do not label Gillian output as a Lean-kernel certificate. Keep compiler,
model, verifier/solver, input-record and module/runtime assumptions visible. New targets must fit
an established execution model without unreviewed language/runtime extensions.

For safe retry admission, read experiments/gillian-retry/README.md, RESULTS.md and
CALLER-CORRESPONDENCE.md; use scripts/check_retry.py with pinned source and the same tool receipt.
Preserve exact case identities from cases.json and structured verifier results, complete positive
and denial controls, and the passing equivalent changed program. Keep bounded-real/safe-integer,
missing/undefined, descriptor/prototype, captured-valid versus reachable and caller/evidence limits
explicit. Changes to shared gillian_runtime.py require the existing settlement regression. Do not
turn a defensive null/receipt/state projection into a claimed reachable production bug.

For the bounded retry protocol experiment, read experiments/retry-protocol/README.md and its
source correspondence before modifying the model or claims. Use scripts/check_retry_protocol.py
with the checksum-pinned TLC release. Preserve meaningful initial/recovery/crash witnesses,
independent possible-application state, the semantic negative controls and useful positive recovery.
Do not describe a bounded TLC pass as an unbounded mathematical proof or implementation refinement.
Explicit forget, retirement and identity reuse remain outside the retained-request model. Guard
and transition checks overlap: do not invent a source vulnerability by removing one check from
an abstraction that has silently omitted the other. Keep fairness and evidence assumptions explicit.
