# Superbee verification experiments

Current research milestone: [a substantial implementation proof with demonstrated transfer to a
second target](experiments/PIPELINE-MILESTONE.md). The existing experiments below are qualified
foundations; they do not complete that milestone. The [verification-pipeline recipe](recipes/verification-pipeline/recipe.md)
provides reusable coordination definitions and evidence guidance without executing proofs.

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

## Bounded retry protocol

The [retry protocol experiment](experiments/retry-protocol/README.md) examines two handles sharing
one retained blob request across guarded claims, typed non-execution evidence, crashes and late
carrier outcomes. It complements the source-level eligibility check with bounded TLC model
checking and explicit implementation correspondence. It does not prove backend durability,
truthful host evidence, unbounded behavior or TypeScript refinement. Explicit forget and identity
reuse have a separate contract and are outside this automatic-retry model.

Select `experiment=protocol` on the existing manual workflow. No product CI gate is added.

## Published binary-proof capability

The [Rocq/RISC-V checkpoint](experiments/rocq-binary-capability/README.md) prepares the published
OSS Verify toy binary proofs and admission controls in one manual, isolated job. It qualifies
tooling rather than proving Superbee or completing the substantial implementation milestone.
Select `experiment=rocq` on the existing manual workflow; no product CI dependency is added.

## Bounded agent/checker construction loop

The [Rocq work cycle](experiments/rocq-work-cycle/README.md) checks agent-authored candidates
against frozen executable source and an independently reviewed statement, retaining every attempt
and enforcing a local attempt/time budget. Its first complete typed guarded-retirement component
[passed after two native diagnostic-driven revisions](experiments/rocq-retirement/RESULTS.md).
Select `experiment=rocq-cycle`, then `cycle_candidate=final` or `controls` on the existing manual
workflow. An agent coordinates proof edits; the checker is authoritative. This is source-level
verified construction, without a claim about the current TypeScript or compiled binary.
