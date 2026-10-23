# Settlement guard under established ES5 semantics

Status: experimental Gillian separation-logic symbolic verification of the complete isolated
emitted function. This uses an established ES5 execution model rather than expanding the custom
Lean JavaScript fragment. It is not a Lean/Rocq-kernel certificate, verified TypeScript compilation,
a proof of Node/V8 execution, or verification of the asynchronous delivery/storage protocol.

## Useful implementation property

`settleAgainstIntent` in core uncertain-write.ts recognizes that an authority conflict already
names the intent's own local version. This lets lost-acknowledgement recovery acknowledge the
right content without treating another remote head as that content. The independent contract is:

| Input | Required result |
| --- | --- |
| Conflict against the same nonnull local string version | Fresh committed record at exactly that version |
| Conflict against a different string version | Identical original outcome object |
| Conflict against null/absent head | Identical original outcome object |
| Any non-conflict string kind | Identical original outcome object; no actual field required |

Each postcondition preserves the owned input fields and global/prototype frame. Separation
ownership requires the fresh committed result to be distinct from the two preserved input records.
Other caller-owned disjoint heap remains subject to Gillian's frame reasoning; it is not proof
that arbitrary references, aliases or effects are handled outside the specified domain.

## Source and transformation

[source-pin.json](source-pin.json) fixes the unchanged original product commit, whole-file hash
and complete declaration byte range [14680,14951). The preparer independently compares that raw
slice with the TypeScript AST selection, removes only the leading module export marker, and uses
pinned TypeScript5.9.3 to erase types into a standalone strict ES5 function. The emitted baseline
contains the same conditional/property reads/equalities/object construction/returns, with no
polyfill or runtime helper. Source and emitted hashes are recorded. The original product remains
unchanged. This proves a property of the emitted isolated function under the tool's model; source
selection, module isolation and TypeScript compilation remain trusted links to the shipped code.

[contract.js](contract.js) has four independently written pre/post pairs. No `@onlyspec` axiom
replaces the body. `gillian-js verify` analyzes the body for each pair. Although its log calls these
"symbolic tests", this command checks separation-logic specifications; it is distinct from the
123 finite native fixtures per variant. We do not describe its result as a kernel-checked proof.

## Input and environment assumptions

- Distinct ordinary nonnull outcome and intent records with own data properties, standard object
  behavior, and no getters/proxies or environmental mutation during evaluation.
- `intent.local` is a string in every case. A conflict owns actual as string or null; nonconflicts
  need not have an actual field. Kind may be any model string unequal to conflict in the last case.
- Strings have Gillian's formal string-theory meaning. Universal Node/V8 UTF16 correspondence,
  including lone-surrogate handling, is not proved. Native Unicode fixtures are diagnostic only.
- Standard global/object-prototype frame described by the upstream predicates is available.
- Truth of authority outcomes and the premise that equal version identifiers identify the same
  content belong to the protocol. This function cannot establish either premise.

Alias inputs, application modules, calls into this helper, transport truthfulness, cancellation,
Promise scheduling, storage/crash atomicity, liveness and full local-edit preservation are outside
scope. The function's caller can request recorded-only settlement; this result does not prove
which settlement mode the caller chooses.

## Genuine and equivalent controls

The same four-case contract is applied to:

- Baseline: four successful specifications.
- Actual equality changed to inequality: two postconditions fail. Native witnesses include both
  false acknowledgement of another head and failure to recover an own-version conflict.
- Returned version changed to WRONG_VERSION: the recovery postcondition fails; native matching-head
  witness returns an incorrect receipt version.
- Fallback changed to unconditional promotion: the three unchanged-result postconditions fail,
  including null and non-conflict cases. This is a coverage/vacuity control.
- Redundant nonnull conjunct removed in a temporary variant: all four pass under the declared
  local-string domain. This is a semantic discrimination fixture, not a product change proposal.

A harmless layout/comment variant emits byte-identical JavaScript after the declared compiler
options, demonstrating a maintenance case without another verifier run. Whole-file source drift
still fails the pin and requires an explicit reviewed update. All three bad variants must reach four
analyzed cases and fail specifically on postconditions: unsupported syntax/crash/timeout is not
counted as bug detection. Frozen native inputs exercise123 fixtures per variant; negative
fixtures are evidence of deliberately changed code, not newly discovered production defects.

## Reproduce and tool identity

Install the existing pinned Node/compiler dependency in this repository, then:

```sh
npm ci --ignore-scripts --no-audit --no-fund
python3 scripts/setup_gillian.py --dir .artifacts/gillian-tools \
  --pin experiments/gillian-settlement/toolchain.json
python3 scripts/check_settlement.py --source-file /path/to/pinned/uncertain-write.ts \
  --tool-dir .artifacts/gillian-tools --json-out .artifacts/settlement-result.json \
  --evidence-dir .artifacts/settlement-evidence
```

The setup supports Darwin-arm64 and Linux-x86_64 with glibc>=2.39, using official prebuilt Gillian
and Z3 4.16.0 archives. Each archive is size/SHA256 checked; extraction rejects links and unsafe
paths. The checker independently binds executed binary bytes back to the committed archive pins.
Each download is bounded to60s and analysis subprocesses to60s. No global package installation,
Docker daemon, opam build or framework modernization is required. Downloaded binaries stay outside
git. Gillian may cache its embedded runtime locally; this does not change product dependencies.

The nightly release name is mutable. Hashes pin the observed archive bytes and fail closed on
replacement; the observed source tag is metadata, not a reproduced-build or provenance attestation.
A future nightly update can require a reviewed tool pin update even when this target is unchanged.
Trusted components include the compiler/parser, Gillian's verifier/JS-to-GIL translation, ES5 model,
Z3 and their string/heap theories, source embedding/module environment and actual runtime adequacy.

The settlement job is selected with `experiment=settlement` on the existing manual-only workflow.
It uses a standard ubuntu-24.04 runner, read-only permissions and a10-minute job bound. It does not run the Lean suites or alter any product/required CI gate.
See [results](RESULTS.md) and [verification-path decision](../VERIFICATION-PATH.md).

## Primary foundations

- [Gillian-JS ES5 scope](https://gillianplatform.github.io/instantiations/js/index.html)
- [JaVerT architecture](https://gillianplatform.github.io/publications/javert.html)
- [Upstream contract predicates](https://github.com/GillianPlatform/Gillian/blob/469aa5c134ba7790c40669bd4bc50483aff36d7b/Gillian-JS/runtime/JSLogic/javert_js_predicates.jsil)
- [Multiple specification cases](https://github.com/GillianPlatform/Gillian/blob/469aa5c134ba7790c40669bd4bc50483aff36d7b/Gillian-JS/Examples/JaVerT/test262/switch-01.js)
