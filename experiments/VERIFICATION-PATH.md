# Implementation-verification path decision

Decision: **GO for scoped verification of compatible pure decision functions using an established
execution model. NO-GO on growing the custom Lean fragment into a general TypeScript/storage
verifier or claiming the article's binary-level assurance.** Keep all experiments isolated,
manual-only and optional. This is a demonstrated narrow path, not an adopted product correctness
guarantee or required gate.

## What changed the decision

The original mathematical retirement invariant is useful but assumes atomic removal and valid
acknowledgement bookkeeping. The source-classifier experiment then coupled actual declaration
bytes to a Lean theorem under a small reviewed semantics. Its decoder is deliberately tailored
to one signature, two fields and six entries; adding more target-specific decoders would not
establish a scalable implementation-verification method.

Instead, the [settlement experiment](gillian-settlement/README.md) used Gillian's existing ES5
execution model on the complete isolated type-erased `settleAgainstIntent` function. No runtime
helper, native-library replacement, product rewrite or new JavaScript evaluator was needed.
Four independent separation-logic cases check own-version recovery, rejection of another/absent
head, unchanged non-conflicts, input preservation and fresh matching output. Three real semantic
mutants fail the unchanged postconditions; a behavior-equivalent changed program passes. This is
more useful evidence of semantic discrimination and reuse than a third bespoke decoder proof.

The trust boundary remains materially larger than a small Lean proof checker: source isolation
and TypeScript erasure, Gillian translation/verifier, its ES5/string/heap semantics, Z3, explicitly described
input records and actual Node/V8 adequacy. The result is symbolic verification under that boundary,
not a proof about the original deployed binary. See [measured results](gillian-settlement/RESULTS.md).

## Alternatives assessed

| Route | Evidence | Current choice |
| --- | --- | --- |
| Custom Lean JS fragment | Exact-byte correspondence and universal policy proof work, but each new operation needs justified semantics and each new fixed signature exposes tailored infrastructure | Retain completed evidence; stop interpreter expansion |
| Gillian / JaVerT | Existing ES5 source model and separation-logic contracts; official prebuilt Gillian+Z3 run locally without framework work; demonstrated settlement contract | GO for compatible isolated pure decisions with explicit trust |
| JSCert / JSRef | Mechanized ES5 semantics with a proved reference-interpreter relation; old build dependencies, parser assumptions and incomplete native-library proof coverage | Credible foundational research, no immediate port/build project |
| KJS | Established ES5.1-oriented K model, but old custom build and incomplete builtins | No modernization project for this spike |
| RISC-V binary route | Published OSS Verify artifacts concern exact static binaries under an explicit Linux-process model | Does not directly cover this JS/Node app; no engine/runtime binary campaign now |
| Verified generation | Prove an intentionally isolated decision kernel and relate generated executable artifacts to it | Separate architecture/build/runtime decision; no production language rewrite authorized by this result |

Primary sources: [Gillian ES5 scope](https://gillianplatform.github.io/instantiations/js/index.html),
[JaVerT architecture](https://gillianplatform.github.io/publications/javert.html),
[JSCert](https://github.com/jscert/jscert), [KJS](https://github.com/kframework/javascript-semantics),
[OSS Verify artifacts](https://github.com/theorem-labs/oss-verify-proofs).
The article's evidence is stronger at executable-byte binding; it also depends on stated execution
semantics and environment assumptions. The aim is to make the trust boundary credible and reusable,
not to pretend all formal verification removes every trusted component.

## Where this helps Superbee

The demonstrated contract prevents falsely turning another remote version into an acknowledgement
while preserving recovery when the shared head already names this write's own content. This is a
real uncertainty/recovery decision. It does not prove that equal identifiers denote equal bytes,
that authority replies are truthful, that the caller chooses this function or that storage is atomic.

The [safe retry experiment](gillian-retry/README.md) separately qualifies `blobIntentResendable`
for equality/zero fallback on bounded safe-integer inputs and explicit optional-field shapes. It
verifies 52 case partitions without adding an evaluator. It does not qualify general IEEE754
arithmetic, claim increments, evidence provenance or async/storage behavior. `refusalLeavesUnknown`
adds helper linkage and arbitrary-value presence semantics. The larger `captureRetireAcknowledged`
entrypoint depends on capture/clone helpers, descriptors, arrays/Set, metadata checks, exceptions and
matching state inside storage. Proving one local subexpression would not prove that whole entrypoint.
`nextBlobIntentRecord` additionally needs arithmetic, evidence provenance, callbacks and transition
invariants. Do not smuggle those obligations into a small Boolean whitelist.

For journal preservation now, keep the unbounded abstract invariant, existing bounded lifecycle
models and executable adapter contract tests as distinct evidence. There is no demonstrated
complete Node async/storage semantics for the application, and no measured case for replacing
those tests with a source-proof campaign.

## Adoption rule and limits

Use the new checker as a manual research/reference check. Qualify a new target only when all of:

1. The complete real function and dependencies fit the existing tool's model without semantic
   rewriting, replacement builtins, a private interpreter or production changes.
2. The property addresses a documented failure mode, is independently specified, includes positive
   and unchanged cases, and states input/alias/environment assumptions a maintainer can assess.
3. Genuine source mutants reach analysis and fail the unchanged contract, an explicit witness
   confirms meaning, and a harmless/equivalent change is not misclassified as a bug.
4. Source/tool identities, setup and checking costs, false starts and trust gaps are preserved;
   exact independent review and manual native CI pass before merge.

Do not add automatic/required product CI, rewrite a runtime language or make full-runtime/binary
marketing claims from this evidence. Those need a new concrete adoption decision. No significant
new spending, production deployment, product patch or disclosure action was part of this work.

This concludes the bounded path experiment: a credible useful source-verification path exists
for a narrow pure-function domain, while broader journal implementation verification is not yet
justified. The remaining architectural choice is whether to intentionally isolate and specify
more deterministic decisions; that is a product/reliability priority decision, not a missing proof
that can be solved by endlessly adding custom grammar.
