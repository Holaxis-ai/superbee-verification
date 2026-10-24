# Actual production retirement: finite proof-backed qualification

This manual pilot executes the actual TypeScript-produced capture/guard code and both production
retirement adapters at the exact commit in [pins.json](pins.json). It compares their observed
results to the unchanged proved Rocq retirement decision. Evidence is **testing with kernel-checked
finite correspondence**, not a universal TypeScript, storage, runtime or binary proof.
Native Rocq acceptance remains unestablished until the isolated job actually succeeds.

The production owners are `captureRetireAcknowledged`, `assertJournalGuard` and the actual
`FileJournaledBackend.retireAcknowledged` / `IndexedDbBackend.retireAcknowledged` methods at
[2d856c4](https://github.com/Holaxis-ai/superbee/tree/2d856c492f146a14e71ee2aafac3f4bc593fe942/packages/core/src).
No owning function is copied into a replacement implementation or supplied as a trusted callback.
The existing shared journal contract already tests basic acknowledged-only retirement and stale
guards. This pilot adds systematic correspondence, queued retirement-specific caller aliasing,
selective multiple-row retirement through close/reopen, complete retained-history/residual checks,
and existing unnamed metadata / foreign-document framing.

## What runs

The Node observer verifies the product commit and 224 pinned source/config/runtime files, compiler
version and bytes, then invokes the actual TypeScript compiler with the product's actual options.
Every unmodified emitted core JavaScript module must equal its existing normal-build module
byte for byte. Compilation writes only into an in-memory output map. Variants run copies of the
actual built module graph, with only the selected real source changes re-emitted; the pinned
product checkout is never edited. Type errors, changed source, nonunique mutation selectors,
loading failures and malformed fixture values fail setup, never count as a semantic mutant kill.
Original and changed TypeScript source, emitted-module identities and compiler options are retained.

Each of six variants runs fourteen cases on each adapter (168 actual adapter executions):

- baseline and a behavior-equivalent guard expression;
- full guard comparison bypass;
- acknowledged-only selection bypass;
- deleting all guarded target records instead of only requested IDs;
- retaining caller aliases instead of cloning retirement request IDs and metadata removals.

Cases include same-version/different-raw and same-raw/different-version guards, retained acknowledged
history, pending residual payload, absent versus stored undefined metadata, selected pending work,
named absent removal, guard permutation, duplicate IDs, unscoped metadata and caller mutation
immediately after retirement invocation. Positive cases retain outstanding work and unselected
acknowledged history. Both adapters close/reopen after every operation. IndexedDB reopens a fresh
adapter against the same retained `fake-indexeddb` factory. That is execution of the actual adapter
against the pinned test implementation, not proof of a real browser's IndexedDB implementation.

## Finite observation boundary

The observer records actual before/options/after/reopened snapshots and explicit accept/refuse
outcomes. The guard/options snapshot is captured before the caller-alias mutation. Actual removed
IDs and metadata keys are derived from before/after differences, not copied from the request.
Document raw/version, all document intent fields, target and foreign document/intent history,
and all seeded named/unnamed metadata remain in the evidence.

The tagged fixture domain distinguishes undefined, null, booleans, safe nonnegative integers,
strings, arrays and plain objects. It rejects accessors, symbols, nonenumerable properties,
sparse arrays, extra array properties, null/custom prototypes, signed zero and unsupported values.
This is a closed observation domain; it does not assert production rejects every value outside it.
Wrong target, unknown input/guard/premise fields and inconsistent presence encodings fail projection.

A single global finite dictionary interns complete tagged values injectively across all cases and
variants. It retains every tagged value and validates tag round trips and unique code assignments;
no hash-collision assumption substitutes for equality. Each modeled record's residual contains the
**entire tagged record**, including every field beyond identity/target/sequence/state/content.
Natural sequence emission is bounded below 1000 for these fixtures. This is trusted finite
observation/reification plumbing, not a verified general JS-value decoder. Its correctness and
provenance need independent review; source hashes do not prove the Node execution or projection.

Generated stock Rocq examples check:

```text
state_view (decision projected_input) = actual_accept_or_refuse_and_remaining_state
```

They also check full observed reopen equality, unchanged foreign-document/intent framing, and
complete before/after equality on every refusal. The production API returns void; it exposes no
ordered deletion-intent list. Therefore `state_view` deliberately projects the proved result to
remaining records, metadata and document. It does not invent an observed request-order list,
especially for deleting a named absent metadata row. Actual diff lists stay independently visible.
Blob-family records, reserved-file state and body-cleanup selection are outside this pilot's
observed frame. `retireAcknowledgedBody` policy is a separate consumer boundary.

The unchanged `Kernel.v`, `Specification.v` and accepted `Proof.v` are byte-pinned. Each baseline /
equivalent adapter case file must compile successfully and report exactly `Closed under the global
context` for the proved reference. Each mutant's file for **each adapter** must fail at a native
computed-equality contradiction (`Unable to unify`), after successful Node/compiler execution and
an actual observed law deviation. A filename, syntax, source-pin or setup failure is not accepted
as the expected counterexample. The finite examples do not complete the broader substantial
production-implementation or proof-transfer milestone.

## Reproduce

Use the existing manual `.github/workflows/check-proof.yml`, `experiment=retirement-production`.
It checks out the pinned product with read-only credentials, runs its normal npm install/build on
Node26.12.1, acquires the digest-pinned public Rocq image and runs the pilot. No automatic trigger,
required gate, product CI dependency or production behavior change is introduced.

For the pinned, normally installed/built checkout locally:

```sh
python3 scripts/check_production_retirement.py \
  --source-root /path/to/pinned/product \
  --evidence-dir .artifacts/retirement-pilot/evidence \
  --json-out .artifacts/retirement-pilot/result.json --node-only
```

`--node-only` records observations and generates cases, reporting
`observations_ready_unchecked_by_rocq`. It never reports native Rocq acceptance. Omit it only on a
native Linux/amd64 Docker host with the exact public image already pulled.

Node/compiler/adapter execution has a 300-second limit. Generated Rocq source is capped at 16MiB
and the dictionary at 8192 entries; limits refuse excess rather than truncate evidence. Native
checking has no network or forwarded credentials, read-only root/input, nonexecutable private
work/tmp filesystems, no capabilities, two CPUs, 6GiB RAM, 256 processes and a 900-second limit.
The entire manual job has a 35-minute cap, including a 600-second public image pull. Python and an
unconditional job cleanup remove only this run's container. The Docker socket, product checkout
and host dependencies are never mounted into the checker. Evidence and exact source controls are
uploaded for fourteen days; generated module copies are removed after observation.

## Repeat against a changed implementation

This is a repeatable reliability check, not a claim that frozen `2d856c4` is current. Changed source
fails closed. To qualify another actual implementation, review an explicit update to the product
commit/ref, full source/config/runtime hashes and compiler bytes, rebuild it normally and rerun
against the **unchanged** Rocq property and meaningful controls. Update only mutation selectors
and projection/schema support that are justified by the real change; review those separately.
Do not change the law to hide a mismatch or reuse old evidence as fresh. A genuine policy change
requires its own specification decision and proof review.

The preceding feasibility assessment inspected the actual owner closure and existing tests. It
found no qualified complete modern JS/storage semantics: current Gillian lacks required builtins;
a source-derived syntax hash or a second extracted implementation does not itself supply a
production refinement proof. Primary owners and existing coverage remain inspectable in
[journaled-backend.ts](https://github.com/Holaxis-ai/superbee/blob/2d856c492f146a14e71ee2aafac3f4bc593fe942/packages/core/src/journaled-backend.ts),
[file adapter](https://github.com/Holaxis-ai/superbee/blob/2d856c492f146a14e71ee2aafac3f4bc593fe942/packages/core/src/file-journaled-backend.ts),
[IndexedDB adapter](https://github.com/Holaxis-ai/superbee/blob/2d856c492f146a14e71ee2aafac3f4bc593fe942/packages/core/src/indexeddb-backend.ts)
and the [existing contract tests](https://github.com/Holaxis-ai/superbee/blob/2d856c492f146a14e71ee2aafac3f4bc593fe942/packages/core/test/journaled-backend-contract.ts).
