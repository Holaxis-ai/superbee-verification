# Native proof-construction work cycle, 2026-10-23

The agent/checker loop completed against frozen executable Rocq source and an independently
reviewed specification. This is a new experimental typed implementation, not the existing
TypeScript, extracted executable, machine-code proof or storage-atomicity proof.

| Candidate | Native run | Result | Feedback |
| --- | --- | --- | --- |
| Initial `e8f43229` | [40039021257](https://github.com/Holaxis-ai/superbee-verification/actions/runs/40039021257) | needs_revision | Membership iff applied in the wrong direction, line35 |
| Revised `1991e4e6` | [40039345176](https://github.com/Holaxis-ai/superbee-verification/actions/runs/40039345176) | needs_revision | Equality symmetry not discharged by contradiction, line76 |
| Revised `f7534dbf` | [40039684942](https://github.com/Holaxis-ai/superbee-verification/actions/runs/40039684942) | accepted | All source, candidate and trusted-wrapper compilations exited0 |

Accepted source commit: `7523e17a7914aded5368e49ac518d0110b69986c`.
Kernel SHA256: `77ae40ce25631b133440f60e89ccc1ddcdb46056548121ce5d66aaf091348484`.
Specification SHA256: `be11d17b359cba294a8047ef7c8308b34667716cd459d73dba3cabd3476bfbcb`.
Frozen contract SHA256: `2e2e882e2b3b3c5247fd60836f52fb63382312637481f9e01794cccb99885c0b`.
Accepted proof SHA256: `f7534dbf676f8b947537d04ee4bea26b2c0c8846026aab9a7acb27fc632dbebf`.

The contract and executable source did not change across these attempts. Agents revised Proof.v
from actual native checker diagnostics. Initial.v preserves the original candidate; intermediate
candidates and full diagnostics remain in their run artifacts and Git history.

The checker accepted `retirement_correct_holds`, `refuse_all_fails`, and `drop_all_fails` at their
fixed independently reviewed types. Each Print Assumptions audit reported exactly
`Closed under the global context`; no axiom dependencies were reported. The correctness theorem
covers complete typed admission/refusal, exact outputs, record/metadata frame and preservation of
unacknowledged rows, plus a useful nonempty retirement witness. The two refutations reject actual
always-refuse and drop-all executable variants under the same correctness relation.

[Native controls40039481030](https://github.com/Holaxis-ai/superbee-verification/actions/runs/40039481030)
rejected all three invalid submissions: admitted proof and extra axioms were exposed by native
Print Assumptions; wrong statement failed trusted theorem ascription. An earlier
[control run40039265610](https://github.com/Holaxis-ai/superbee-verification/actions/runs/40039265610)
rejected the admitted proof but stopped on an orchestration bug: an underscore in the next Docker
container name was refused by the CLI. That failed run is retained and was not counted as three
valid controls. The bounded name validator was corrected to admit Docker-valid underscores.

Accepted check wall time: **1.468 seconds**, excluding cold image acquisition. The three-control
shared ledger charged **2.597 seconds**. These measurements do not estimate proof construction,
future targets or binary proof costs. Manual workflow dispatches use fresh local ledgers; root
coordination tracked the complete campaign across jobs. Ledger bounds are not a distributed
scheduler or tamper-proof audit service. GitHub run artifacts retain raw evidence for14days;
project artifacts preserve downloaded copies and independent review receipts.

Independent statement/source review and native evidence QA accepted this narrow result. The
substantial-current-product and second-implementation proof-component transfer milestones remain
open. No product runtime, required CI gate, automatic scheduling or automatic obligation discharge
was added. See [work-cycle instructions](../rocq-work-cycle/README.md).
