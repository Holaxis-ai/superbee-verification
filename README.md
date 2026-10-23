# Superbee verification experiments

Small, reproducible mathematical-proof experiments, kept outside the product repository and its
normal CI. Status: experimental. The initial retirement model has manual source correspondence; the new
source-classifier experiment derives syntax from a shipped function under trusted restricted
semantics. Neither is a full TypeScript/runtime refinement proof.

The first experiment proves a focused journal-retirement rule with Lean 4.27.0. Given valid
acknowledgement accounting, preserved local payloads, and acknowledged-only admission, one
abstract atomic retirement preserves outstanding accepted payloads. Induction extends that result
to arbitrary finite sequences of admitted retirements. There is no fixed journal-size bound.

The proof also contains a concrete payload-loss counterexample when the admission premise is
bypassed, and a nonempty admitted retirement witness. This does not prove the complete lifecycle,
backend atomicity, acknowledgement validity, or the shipped TypeScript implementation.

## Source-derived implementation bridge

The [classifier experiment](experiments/source-classifier/README.md) parses the actual shipped
`isAuthorizationRefusal` function and derives the syntax consumed by a checked universal policy
theorem. Independent policy, source mutants, kernel counterexamples, native replay and source
staleness controls keep the connection inspectable. An additional Lean decoder independently reconstructs syntax from exact declaration bytes and
kernel-checks its equality with the external AST. Restricted grammar/semantic adequacy, acquisition,
module context and runtime remain trusted. The manual workflow has a separate standard-runner job; product CI is unchanged.

## Run

Install elan, then the pinned toolchain if it is not already present:

```sh
elan toolchain install leanprover/lean4:v4.27.0
python3 scripts/check.py --json-out .artifacts/check.json
```

For the retirement experiment, Python 3 and the Lean standard library suffice. The separate
source bridge also uses Node and a pinned TypeScript parser in this repository only. Each subprocess has a 60-second limit. The checker
compiles from source into a fresh temporary directory, audits all experiment theorem dependencies,
and requires Lean to reject a deliberately false preservation claim. It permits only Lean's
standard logical axioms, never proof placeholders or custom theorem assumptions introduced as axioms.

`.github/workflows/check-proof.yml` runs this same check **only on manual dispatch**, on a standard
`ubuntu-latest` runner with a ten-minute job limit and read-only permissions. No push, pull-request,
scheduled, or product-repository workflow calls it. No generated binaries or large artifacts are
committed. Initial cold toolchain setup is measured separately from proof-check time in job logs.

## Scope and evidence

- [Theorems](Journal/Retirement.lean)
- [Source pin, assumptions, correspondence and next milestone](experiments/journal-retirement/README.md)
- [Initial measured result](experiments/journal-retirement/RESULTS.md)
- [Superbee work record](https://github.com/Holaxis-ai/superbee-dev/blob/board/tasks/journal-preservation-mathematical-proof-experiment.md)

This experiment follows the agent-assisted, machine-checked-proof idea discussed in
[Anthropic's article](https://www.anthropic.com/research/formal-verification), using a small Lean
source model rather than their Rocq/RISC-V binary verification pipeline. The kernel checks the
proof; people still need to review the theorem, assumptions and implementation connection.

Licensed under Apache-2.0, matching Superbee.

## Established-tool implementation experiment

The [settlement experiment](experiments/gillian-settlement/README.md) verifies a useful pure
recovery function with Gillian's existing ES5 model. Four separation-logic cases distinguish
recognizing an own-version conflict from incorrectly acknowledging unrelated content. It uses
pinned prebuilt tools, semantic mutants and an equivalent changed-code control, with no custom
JS semantics added. This is trusted-tool symbolic verification, distinct from the Lean kernel
proofs and from a proof of actual Node/V8 execution. See the [scope/adoption decision](experiments/VERIFICATION-PATH.md).

The [safe retry admission experiment](experiments/gillian-retry/README.md) reuses that toolchain on
`blobIntentResendable`. It separately qualifies bounded safe-integer equality/zero fallback and
missing/undefined fields, verifies positive and denial contracts, and records caller enforcement
as source correspondence. No asynchronous/storage or IEEE754-arithmetic proof is implied.
