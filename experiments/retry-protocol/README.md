# Bounded retained-request retry protocol

This experiment checks a manually modeled retry protocol with the established TLC model checker.
It is not a TypeScript refinement proof, a Lean/Rocq certificate, an unbounded theorem, a database
atomicity proof or an end-to-end exactly-once guarantee. The earlier Gillian experiment checks the
actual pure eligibility function; this experiment examines asynchronous ordering around that rule.

## Question and bounds

For one existing, retained, immutable blob request, can competing handles or crash/reopen authorize
another automatic submission while an earlier attempt might still apply? The finite model contains
two handles, two attempt numbers, and at most one crash/reopen per handle. Snapshots may become stale,
including pending-state ABA after a claim and rollback. The request is already admitted. Explicit
forgetting, retirement, new admission, request-ID reuse, predecessor chains, independent requests,
full same-key metadata, and document content/CAS are outside this slice. In particular, explicit
forgetting after absence is not modeled as proof that a forgotten attempt cannot later apply.

The persisted row has attempt, covered prefix, state and receipt. Each handle reads a snapshot. An
atomic claim validates that complete modeled snapshot and the actual-current transition rule,
increments the attempt once, and grants one local wire token with handle/session provenance.
Invoking a dispatched wire consumes that token. Crash/reopen discards the token and changes session;
an already dispatched operation may still apply afterwards. A lost pre-wire token leaves a gap,
not automatic permission to retry. Unknown/absent lookup changes state only and never covers a gap.

`mayApply` is independent ghost environment state, not defined from the prefix. Claim conservatively
sets it true even before wire. Authentic local not-dispatched evidence can clear it only for the
current owning session's unconsumed token and zero dispatched wires. Typed host non-execution is a
separate action: it requires a dispatched invocation and no application, and represents an authentic
host guarantee that also prevents future late application. An ordinary absent lookup is explicitly
not that guarantee. The host authority/truthfulness/continued exclusion guarantee remains trusted.
This does not claim deletion holds apply to every operation or guarantee evidence availability.

## Checked properties and nonvacuity

The safe configuration explores all reachable states under the stated bounds, with no fairness
assumed for safety. It checks:

- `NoUnsafeClaim`: each successful claim consumes a previously unused attempt and no lower attempt
  may still apply. The historical ghost records violations; it does not guard the claim action.
- `PrefixSound`: every covered attempt actually cannot apply and has not applied.
- `AtMostOneWire`: at most one dispatched invocation per attempt.
- `NoOverlappingApplications`: both attempts cannot apply.
- `TypeOK`: row/counter and selected ghost domains remain bounded and well typed.

Four expected invariant counterexamples separately demonstrate reachability of initial submission,
own pre-wire rollback followed by retry submission, a dispatched operation applying after its
owner crashed, and a pre-wire crash followed by lookup without new permission. These are deliberate
false invariants over the correct model, not bugs or failed safety checks.

The recovery configuration starts at an unknown, once-dispatched first attempt with lost local
provenance. It checks eventual dispatch of attempt two in a **fault-free recovery epoch**: no new
crashes, application outcomes or local cancellations, truthful host non-execution evidence for
attempt one eventually available, and weak fairness of host evidence, each handle's snapshot
refresh, the claim group and the wire group. It does not require both handles to win. Unknown/absent
lookup alone is intentionally permitted to remain unresolved in the safety model. This is conditional
non-execution retry recovery, not universal terminal settlement or unconditional liveness.

## Controls

| Configuration | Required actual TLC result |
| --- | --- |
| `safe` | Complete graph, no error, all five invariants |
| `guard-only` | Complete graph, no error, same five invariants |
| `stale-claim` | Counterexample to `NoUnsafeClaim` |
| `absence-evidence` | Counterexample to `PrefixSound` |
| `foreign-rollback` | Counterexample to `PrefixSound` after a dispatched invocation |
| `initial-wire` | Counterexample to false `NoInitialWire` |
| `rollback-retry` | Counterexample to false `NoRollbackRetry` |
| `crash-late-apply` | Counterexample to false `NoCrashLateApply` |
| `crash-lookup` | Counterexample to false `NoCrashLookup` |
| `recovery` | Complete temporal check, eventual retry dispatch |
| `deny-recovery` | Temporal counterexample under the same recovery fairness |

The stale/blind mutation removes **both** complete-guard comparison and actual-current transition
validation, deciding from a stale snapshot instead. It is not evidence that removing only the guard
breaks this safety property. The `guard-only` control removes snapshot equality but retains actual
current state/attempt/prefix eligibility and next-count validation. It passes because the remaining
validation independently enforces these modeled fields. Complete guards also protect omitted
same-key metadata and snapshot integrity; no claim of their dispensability follows.

The absence mutation incorrectly promotes absence to prefix coverage. The foreign rollback mutation
accepts another/lost session's claimed attempt after dispatch, without authentic non-execution.
The blanket-deny mutation remains safe but fails recovery, preventing a never-submit implementation
from satisfying the experiment's useful behavior requirements.

## Source correspondence and trust boundaries

[source-pin.json](source-pin.json) freezes three complete source files at OSS commit
`6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72`. Optional `--source-root` checks their exact bytes.
This is manual correspondence, not extraction, compiler verification or a source semantics theorem.

| Model | Frozen product owner | Boundary |
| --- | --- | --- |
| Eligible | `blob-journal.ts`, `blobIntentResendable` | Validated-record projection; does not authenticate evidence or guarantee claim success |
| Snapshot/current Claim | `assertBlobGuardMatches`, `decideBlobUpdate`, `nextBlobIntentRecord` | Complete guard then independent actual-current increment/state/prefix validation; backend atomic execution assumed |
| Handle/session and local evidence | `claimedInThisSession`, update session bookkeeping, `blobNonExecutionPatch` | Actual session bookkeeping and truthful carrier classification manually mapped, not verified |
| Claim then Wire | `hosted-client/blob-write.ts`, `claimAndSubmit` | Await durable guarded update before delivery; admission/capability/hold gates outside model |
| Unknown/absent lookup | `blob-write.ts` drive path and `blob-delivery.ts` explicit lookup | Lookup does not itself dispatch; wire after false gap would require explicit modeled mutation |
| HostEvidence | typed `deletionHold` transition and delivery evidence | Exact-attempt typed correlation plus permanent non-application guarantee trusted; not generic absence |
| Apply/Receipt | abstract wire environment and terminal record | Server implementation, receipt authentication, content semantics, transport and persistence not proved |

Assumed atomicity is a single backend guarded read/decide/write, not a proof of multi-process file
locking, IndexedDB transaction behavior, fsync, multiple realms, distributed atomicity, or crash
persistence. Immutable request identity/payload, valid record capture, truthful typed evidence,
caller capability/admission checks, one-use local wire authorization and mapping fidelity remain
review obligations. Two attempts/two handles do not establish arbitrary retries or concurrency.
A model counterexample is not by itself a product vulnerability.

## Reproduce and tool identity

Use Python 3, Java 21 or another supported runtime, and the official TLA+ release v1.7.4 archive
pinned in source-pin.json. Its embedded banner is TLC2 Version 2.19, 08 August 2024; the release tag
and tool banner are different version labels. SHA256 is
`936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`, matching the earlier product
TLA workflow pin. No downloaded archive or generated binary is committed.

```sh
python3 scripts/check_retry_protocol.py --tlc-jar /absolute/path/tla2tools.jar \
  --evidence-dir /absolute/path/evidence --json-out /absolute/path/result.json \
  --source-root /absolute/path/frozen-product-source
```

`--java /absolute/path/java` optionally selects a real runtime; a macOS `/usr/bin/java` launcher
without an installed runtime is insufficient. The checker invokes actual TLC, one worker, 768 MiB
heap and at most 60 seconds per subprocess. Deadlock checking is disabled deliberately because
uncertainty can safely block; recovery has its separate temporal requirement. Each variant runs in
a fresh directory. The checker retains exact model/config/script inputs, raw logs, runtime identity,
input/log hashes, elapsed times and exact expected verdicts. Parser/tool errors, timeout, unexpected
invariant or missing counterexample cannot count as successful negative controls. TLC's fingerprint
collision risk and the Java/TLC runtime/checker remain trusted. No product CI is made required.

## Initial local result

Temurin21.0.9+10 aarch64 and the pinned TLC archive checked the final model. Safe and guard-only each
explored 13,432 distinct states, with all safety checks passing. Recovery explored 77 distinct
states and passed. The three semantic mutations, four reachability witnesses and denial control
produced their required exact counterexamples. Total observed checker subprocess time was about
7.4 seconds, excluding setup. Final exact input receipts and native CI are recorded with the PR.

The first authoring run correctly failed its stale-claim negative control: an unparenthesized ghost
conjunction accidentally restricted the action instead of recording unsafe history. The negative
control exposed that vacuity; the corrected model explicitly parenthesizes the ghost Boolean RHS.
That failed run and its raw output are retained in local evidence rather than represented as a pass.
