# Journal retirement experiment

## Question

Can a small, checked mathematical proof express a useful preservation rule with low checking
cost, without increasing product CI or pretending an abstract function is verified TypeScript?

## Exact property

`retire_preserves_outstanding` quantifies over every finite `State` journal and request-ID list.
If `Valid s`, `Preserved s`, and `Admitted s ids`, then `Preserved (retire s ids)`.
`retirement_sequence_preserves` proves validity and preservation over arbitrarily many admitted
retirements. Its induction covers retirement sequences only; it is not lifecycle induction over
accept, supersede, claim, deliver, crash, resolve and retire.

Rows carry distinct request IDs and symbolic complete-payload tags. A payload tag represents the
entire immutable logical edit payload, not merely a receipt, request key or reference with missing
content. The working document or a surviving journal row must contain that payload. Translating
actual serialized bytes and logical edit identities into these symbols remains a correspondence
obligation. The proof does not require unique row IDs, but real adapter identity guarantees and
well-formed schemas have not been proved here.

`Valid` assumes each acknowledged row's payload is legitimately discharged. `Preserved` is an
initial conservation assumption; it is not assumed about the output. `Admitted` permits selecting
only acknowledged rows. `retire` removes selected rows in one abstract atomic operation without
changing accepted/discharged bookkeeping or the current working document. The preservation proof
shows an outstanding payload's journal witness cannot be among the selected rows: that would make
it discharged, contradicting its outstanding status.

`witness` has older outstanding payload10, newer payload20 and working document20. Removing row1
without admission loses payload10. Lean proves that loss and separately rejects the false claim
that the result remains preserved. `settledWitness` demonstrates a nonempty admitted retirement
that removes acknowledged history while keeping newer outstanding work.

## Source pin and mapping

[source-pin.json](source-pin.json) fixes public OSS source at
`a63eef111001974a89ce35a83759bbe183814a1c` and hashes four inspected files.

| Formal element | Product owner | Correspondence status |
| --- | --- | --- |
| `Admitted` acknowledged-only premise | core `captureRetireAcknowledged` in `journaled-backend.ts` | Manually mapped. Production also checks a complete current guard, target, nonempty unique IDs and metadata scope. None of those additional checks is proved. |
| Atomic `retire` removal | core IndexedDB and file `retireAcknowledged` methods | Trusted atomic-application assumption, not a proof of transactions, fsync, crash safety or replay. |
| Payload occurrence and acknowledgement discharge | durable intent content and settlement bookkeeping | Abstract representation/validity assumptions; no verified parser, serializer or network outcome semantics. |
| Retention eligibility beyond acknowledgement | browser-local `retireAcknowledgedBody` | Outside this theorem: newest-row retention, predecessor scheduling and body evidence validation require additional obligations. |

```sh
python3 scripts/check_source.py /path/to/a-pinned-superbee-checkout
```

This optional offline check verifies commit/file identity only. A changed commit is reported as
stale. It never blesses a new source revision or establishes semantic correspondence. A proof run
without this check refers to the pinned experiment only, not the current product branch.

## What has not been established

No TypeScript translation, refinement, extraction, actual backend atomicity, valid acknowledgement
protocol, full lifecycle preservation, liveness, multi-realm behavior, eviction/retention policy,
or meaningful real-world bug finding. No independent semantic review has been completed. A general
abstract theorem can be cheap because it omits difficult implementation behavior; its cost must
not be extrapolated to the full application or Anthropic's binary proofs.

## Next milestone

Independently assess statement usefulness and the source mapping. Then choose one concrete bridge:
prove a restricted executable implementation with checked translation, or keep this explicitly as
an abstract policy theorem and connect its cases through implementation tests. Do not rewrite core,
introduce a new production language, or add required CI merely to claim a stronger proof.
