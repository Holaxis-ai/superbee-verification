# Verification experiment

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
