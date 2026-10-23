# Safe retry admission under established ES5 semantics

Status: isolated Gillian separation-logic symbolic verification of the complete emitted
`blobIntentResendable` function. No JavaScript evaluator/model extension or product change.
Compiler, model, solver and actual-runtime correspondence remain trusted; this is not a
Lean-kernel certificate, binary proof or end-to-end exactly-once guarantee.

## Useful admission law

Fresh submission may be considered only when the record has no receipt, its scheduling state is
pending or unknown, and the non-execution evidence covers every claimed attempt. An uncovered
attempt must remain lookup-only. Zero attempts with omitted evidence is the initial positive case;
a positive fully covered prefix is the recovery positive case. All owned fields are preserved.

[contract.js](contract.js) contains52 independently specified pre/post cases, ordered and named in
[cases.json](cases.json). The contracts are partitions of that law, not an evaluation of the source
expression in a second custom model. The original body is analyzed by Gillian, never replaced with
`@onlyspec` or a trusted admission result.

| Case family | Required result |
| --- | --- |
| No receipt, pending/unknown, zero attempts, missing/undefined prefix | Eligible |
| No receipt, pending/unknown, positive attempts, missing/undefined prefix | Refuse |
| No receipt, pending/unknown, complete numeric prefix | Eligible |
| No receipt, pending/unknown, incomplete numeric prefix | Refuse |
| Numeric prefix greater than attempts | Refuse; defensive invalid-record case |
| In-flight or any other noneligible state | Refuse |
| Any object receipt | Refuse |
| Null prefix | Nullish-language control only; actual record capture rejects it |
| Null receipt | Refuse; defensive invalid-record case |

Each input optional property is modeled separately as own absence, own undefined, null or a
numeric/object value as applicable. The contracts cover every combination in this stated field
domain. Their larger domain includes deliberately inconsistent field projections; it does not
claim every model input is a valid or reachable journal record.

## Complete source and transformation

[source-pin.json](source-pin.json) fixes OSS6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72, complete
blob-journal.ts SHA256225aaaa8e6e148ad85d9a9ff2f32f6b96f95295faf4e8cecc96c3e283cfa029c and
complete declaration bytes[33709,33922). Raw byte selection independently matches the TypeScript
AST node. The whole source file is unchanged from the previous OSSa63eef pin, but the new experiment
names the current inspected main rather than silently blessing historical correspondence.

The preparer removes the leading export token and uses existing pinned TypeScript5.9.3 to emit
strict ES5. Nullish coalescing becomes one local `_a` and a null/undefined conditional. That exact
emitted body is verified; no handwritten replacement, polyfill or native library substitution is
introduced. TypeScript compilation and source/module isolation remain trusted links to shipped code.

## Numeric qualification

Actual captureBlobIntentRecord requires nonnegative safe-integer attempts and a safe-integer prefix
between zero and attempts; omitted/undefined prefix means zero. Positive prefix also requires typed
evidence. State/receipt consistency and evidence validity are enforced elsewhere, not by this helper.

The pinned Gillian SMT backend represents symbolic NumberType as mathematical reals. `types(...:
Num)` therefore must not be advertised as a universal IEEE754 guarantee. Contracts quantify bounded
real values in [0,9007199254740991], a domain containing the validated integer values. The helper does
only strict equality and zero fallback, with no counter arithmetic. Exact safe integers embed in
that domain; signed zero collapses harmlessly because strict equality treats -0 and 0 identically.
This embedding and model/runtime adequacy are reviewed justifications, not additional checked
compiler/runtime theorems. NaN, infinities, unsafe integers, general floating arithmetic and
numeric coercions receive no production claim. Fractions in the stronger symbolic domain receive
no valid-record claim. Do not extrapolate this qualification to attempts+1.

Primary basis: [pinned SMT encoding](https://github.com/GillianPlatform/Gillian/blob/469aa5c134ba7790c40669bd4bc50483aff36d7b/GillianCore/smt/smt.ml#L472),
[GIL literal domain](https://github.com/GillianPlatform/Gillian/blob/469aa5c134ba7790c40669bd4bc50483aff36d7b/GillianCore/GIL_Syntax/Literal.ml#L11),
[strict equality](https://github.com/GillianPlatform/Gillian/blob/469aa5c134ba7790c40669bd4bc50483aff36d7b/Gillian-JS/runtime/JS2JSIL/Internals.jsil#L1251).

## Heap, optional-field and evidence boundary

Inputs are nonnull extensible standard-Object.prototype records. Owned data properties have
writable/enumerable/configurable descriptors. There are no getters, proxies, arbitrary descriptors,
prototype pollution or concurrent field changes. Own absence is explicitly owned with
`((#o,"field")->none)`, distinct from `DataProp(...,undefined)`. The upstream ObjectPrototype frame
also establishes no relevant custom inherited fields: own absence alone would not establish an
undefined lookup. [Actual upstream predicates](https://github.com/GillianPlatform/Gillian/blob/469aa5c134ba7790c40669bd4bc50483aff36d7b/Gillian-JS/runtime/JSLogic/javert_internal_functions.jsil).

The formal object-prototype predicate is a minimal model; real runtime/prototype correspondence
remains a trust boundary. Validated state strings are six ASCII tags. Wider model string cases do
not establish a universal Node/V8 UTF16 theorem.

A fully captured record additionally has correct identity, prepared payload, sequence, timestamp,
canonical receipt, prefix bounds and typed evidence. A captured-valid record need not be reachable
through normal transitions. Neither validity nor reachability is inferred from a fixture projection.
At MAX_SAFE_INTEGER with complete evidence, the predicate may return true; the subsequent transition
rejects increment overflow. Eligibility is not a promise of a successful claim or send.

## Controls and preservation

Every analyzed variant reaches all 52 contracts. The plan names exactly which cases must fail:

- Prefix equality changed to <= must reject the ambiguity contract, with a concrete unknown
  attempts=1/prefix=0 witness. This is a valid field projection with a possibly applied attempt.
- Always-deny fails all 16 positive cases; always-allow fails all 36 negative cases. Together they
  check nonvacuity of every stated partition.
- Unknown eligibility changed to in-flight fails required unknown recovery and in-flight denial.
- Receipt bypass fails 8 receipt-presence cases. Those counterexamples are defensive projections;
  removing that clause can be equivalent on fully captured-valid records because receipt iff
  terminal state is enforced separately. This is not a discovered production vulnerability.
- State bypass fails 8 noneligible-state cases. Some in-flight fixtures pass capture field checks
  but may be unreachable through valid transitions; that limit remains explicit.
- Reordered pending/unknown disjunction must pass every contract despite changed emitted bytes.
  Harmless layout/comments emit identical bytes and need no duplicate analysis.

Native fixtures use ordinary descriptor-matching records and snapshot their descriptors, nested
values, prototype and extensibility. They include missing/undefined, null diagnostics, all six
states plus an invalid-state control, signed zero and safe-integer limits. Native diagnostics do
not prove the real-number/runtime bridge. Source drift and forged executable receipts fail closed.

## Run, reuse and costs

```sh
npm ci --ignore-scripts --no-audit --no-fund
python3 scripts/setup_gillian.py --dir .artifacts/gillian-tools \
  --pin experiments/gillian-settlement/toolchain.json
python3 scripts/check_retry.py --source-file /path/to/pinned/blob-journal.ts \
  --tool-dir .artifacts/gillian-tools --json-out .artifacts/retry-result.json \
  --evidence-dir .artifacts/retry-evidence
```

The experiment reuses the existing archive pins, setup and shared executable validation. It does
not introduce another toolchain or private semantics. The unchanged settlement contracts are
regression-checked after extracting the shared tool-validation helper. Binary bytes remain bound
back to the committed archive hashes, independently of the mutable receipt.

Select `experiment=retry` on the existing manual workflow. Only the retry job runs, on standard
ubuntu24.04/read-only permissions/10min bound, with a settlement regression inside that job. The
old Lean and standalone settlement jobs are skipped. No product installation/build or required CI
change. Analysis subprocesses remain60s-bounded. See [results](RESULTS.md) and the independently
reviewed [caller correspondence](CALLER-CORRESPONDENCE.md).
