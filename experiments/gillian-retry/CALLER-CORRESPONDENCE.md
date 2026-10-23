# Safe retry caller correspondence

This is read-only source correspondence at OSS6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72, independently
inspected alongside the complete helper. It is not symbolic verification of the caller, backend,
wire protocol or async interleavings. Existing regression tests below were inspected; this record
does not claim that the product suites were rerun by the proof experiment.

## Validity and evidence before eligibility

[captureBlobIntentRecord](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/src/blob-journal.ts#L189)
requires nonnegative safe-integer attempts; a missing/undefined prefix denotes zero, otherwise it
is a safe integer between zero and attempts. Null prefix is invalid. Positive prefix requires
typed deletion-hold or not-dispatched evidence. Terminal state is equivalent to receipt presence;
a present receipt must have canonical matching content. Payload identity, target, sequence and
timestamps have separate checks. The eligibility helper proves none of these capture rules.

A captured-valid record is not necessarily transition-reachable. Capture accepts synthetic
receiptless in-flight records with zero attempts, which ordinary claim transitions do not produce.
The field-projection/native labels in this experiment never assert full payload validity, typed
evidence authenticity or reachability. Removing the receipt clause can be equivalent on fully
captured-valid records because state eligibility already excludes terminal states. Its negative
control therefore tests the broader helper contract, not a new reachable production bug.

## Three production uses

| Source boundary | Observed behavior |
| --- | --- |
| [Drive decision](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/src/hosted-client/blob-write.ts#L438) | Existing receipts are handled first. Eligible rows still require requested mode, held-delete acceptance, capability and admission checks before claim-and-submit. Receiptless rows failing the helper go to explicit lookup. |
| [Forget exclusion](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/src/hosted-client/blob-write.ts#L479) | Only unknown, receiptless, non-resendable rows proceed toward fresh absence lookup and guarded forgetting. Forgetting is not proof of non-execution. |
| [Held-record projection](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/src/hosted-client/blob-write.ts#L944) | Exposes eligibility to the consumer; it sends nothing. |

These are all production calls found by frozen-source search. Initial fresh admission is a
separate path: admission creates pending/zero attempts, then invokes claim-and-submit without
calling this helper. Thus it would be false to claim every submission directly passes this function.

## Claim before wire is independently enforced

[claimAndSubmit](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/src/hosted-client/blob-write.ts#L397)
awaits guarded update to in-flight with one increment before delivery. Refresh/retry operates on
complete same-key guards, not a blind overwrite. The transition owner
[nextBlobIntentRecord](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/src/blob-journal.ts#L380)
independently requires no receipt, pending/unknown current state, in-flight next state, exactly
one increment, complete before-prefix coverage and unchanged prefix/evidence. A prefix extension
requires typed evidence for that precise claim; local not-dispatched requires this handle's claim.
Receipt freezes state/counters/evidence. The full guard match and atomic application belong to
other code and backend contracts, not the isolated predicate proof.

At MAX_SAFE_INTEGER the helper may allow eligibility, while capture of the incremented next
record rejects overflow. A true eligibility result does not guarantee claim success or a send.

[performHostedBlobDelivery](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/src/hosted-client/blob-delivery.ts#L60)
recaptures records and checks trusted scope/no receipt. Explicit claimed starts are separately
validated by uncertain-write. Explicit lookup does not authorize a fresh submission on absence.
Those source observations support the intended admission interpretation; no end-to-end exactly-once,
crash/persistence, callback, locking, cancellation or authority guarantee is proved here.

## Existing regression anchors

- [Journal transitions](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/test/blob-journal-transitions.test.ts#L145): claims consume eligibility; count/prefix/evidence restrictions, same-session claims and guard conflicts.
- [Rollback/reopen and legacy records](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/test/blob-journal-transitions.test.ts#L322): typed non-dispatch remains resendable; unknown gaps remain lookup-only; positive prefixes need evidence.
- [Hosted write uncertainty](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/test/hosted-client-blob-write.test.ts#L471): unclear attempts, claim failure/crash, non-dispatch rollback and guarded concurrency.
- [Delivery lookup/claim boundaries](https://github.com/Holaxis-ai/superbee/blob/6092eaf6d16c8bf2c25d526cbbb768cfa07e9b72/packages/core/test/hosted-client-blob-delivery.test.ts#L151): absent/contradictory lookup never sends, invalid claims fail before factory and evidence cannot fill gaps.
