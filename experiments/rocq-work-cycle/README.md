# Bounded agent and Rocq checker work cycle

An agent proposes `Proof.v`, the native checker reports diagnostics, and the agent revises that
candidate against the same frozen executable source and statement. The runner performs **one
attempt**. It does not call an LLM service, hold API credentials, schedule agents, or edit proofs.
The coordinating agent consumes retained diagnostics and decides the next candidate.

This experiment checks typed executable Rocq source. It does not establish correspondence with
existing TypeScript, extracted machine code, actual binary execution, or the substantial-component
milestone. Specification usefulness and source correspondence require independent review.

## Frozen boundary and permitted edits

`contract.json` pins `Kernel.v` and `Specification.v`, the fully qualified proposition and candidate
theorem name, exact checker image, empty axiom allowance, and cost limits. Freeze and independently
review these before the first attempt. The agent may revise only candidate proof source; changing
kernel, statement, limits or checker defines a new reviewed experiment, never a proof repair.
The runner hashes exact bytes and refuses a changed baseline. It copies only two frozen `.v` files
and one candidate `.v` into a fresh directory; caller-supplied compiled libraries are not loaded.

The namespace is `Retirement.Kernel`, `Retirement.Specification`, and `Candidate.Proof`. The
runner-owned wrapper ascribes `Candidate.Proof.retirement_correct_holds` to the pinned
`Retirement.Specification.retirement_correct`, also ascribes the two fixed reject-all/drop-all non-vacuity refutations, then prints fully
qualified assumptions for all three. Acceptance
requires actual native candidate and wrapper compilation, all preceding native stages successful,
and exactly three `Closed under the global context` lines with no other output. Custom axioms and admissions are forbidden,
including unused admission tokens (the conservative additional token check includes comments).
A different theorem cannot pass by compiling its own weaker type.

This first work cycle accepts reviewed internal agent candidates, not arbitrary untrusted proof
submissions. Rocq vernacular and installed plugins have broader authority than theorem terms;
container isolation and a textual assumption audit do not establish a malicious-code submission
service. Independent review must inspect candidate commands and the trusted checker boundary.

## Run one attempt

Acquire the exact image separately on a native Linux/amd64 Docker host, then run:

```sh
python3 scripts/check_rocq_work_cycle.py \
  --candidate experiments/rocq-retirement/Proof.v \
  --ledger .artifacts/rocq-cycle/ledger.json \
  --evidence-root .artifacts/rocq-cycle/attempts \
  --json-out .artifacts/rocq-cycle/result.json
```

`--validate-only` hashes inputs without running a checker, reserving an attempt or claiming proof
acceptance. A local ledger permits at most three attempts and 900 seconds charged total; each
attempt reserves at most 240 seconds before execution. Exclusive locking prevents overlapping
writers. A lost pending attempt retains its reserved charge. Tool probes and cleanup count toward
actual charged time; checker deadline reserves 15 seconds for cleanup. The ledger is trusted local
coordinator state, not a signed or adversary-resistant audit database. Preserve it between revisions.
The coordinator also bounds the number of dispatched Actions runs; a new job starts a new ledger
and cannot enforce a budget across jobs by itself.

Every admitted attempt creates a new directory containing exact candidate and frozen contract,
trusted wrapper, image identity, actual Docker argv, stage diagnostics/exits, wall time and evidence
hashes. Prior attempts are not overwritten. Contract mismatch, missing native markers or unavailable
tooling remain errors. They cannot become successful negative controls. Exit zero means either
`accepted` or the explicitly weaker `inputs_validated_only`; inspect status, not just process exit.

- `needs_revision`: candidate failed native Rocq compilation; diagnostics go back to the agent.
- `rejected`: candidate compiled but failed fixed theorem ascription or admission/assumption policy.
- `error`: setup, frozen baseline, timeout, interruption, missing evidence or exhausted budget.
- `accepted`: native compile, ascription and strict assumption audit all passed.

## Manual qualification

Select `experiment=rocq-cycle` in existing `check-proof.yml`, with `cycle_candidate=initial`,
`final`, or `controls`. Initial and final are separate retained attempts; after a genuine initial
failure, the agent must use those actual diagnostics to revise proof source. The three explicit
controls challenge admitted proof, custom axiom and a weaker True theorem. Controls each require
native execution and a rejected result; setup failures do not pass them. The controls share one
three-attempt ledger. No automatic workflow trigger, product gate or LLM credentials are added.

The pinned checker runs offline, unprivileged, without capabilities/host repository/Docker socket,
with a read-only root/input and private noexec work/tmp mounts. Only its evidence directory is
writable on the host. CPU2/RAM6GiB/PIDs256, 1GiB work tmpfs and 128MiB temporary tmpfs bound execution;
per-file generated logs are capped with Bash `ulimit -f`. Python timeout/signal cleanup and workflow
always-cleanup target only that attempt's named container. Job timeout is 30 minutes including at
most600 seconds image acquisition. All attempt artifacts upload even after failure, retained14days.
No optional full rocqchk, compiler extraction or RISC-V proof is claimed by this work cycle.
