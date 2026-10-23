# Published Rocq / RISC-V capability checkpoint

This is a tooling bootstrap using the published OSS Verify controls, not a proof of Superbee
or completion of the [substantial implementation milestone](../PIPELINE-MILESTONE.md).
Native acceptance remains unestablished until the manual workflow actually runs successfully.
No local Docker, compiler or new proof semantics is installed by this change.

The [pinned upstream source](https://github.com/theorem-labs/oss-verify-proofs/tree/98e995d4daced70a0a4aa2c810854b88720735f1/tests)
writes three real 132/136-byte static RISC-V Linux ELF binaries. Its Dune rules check their
committed SHA256 values and use the installed `elf-snapshot` to bind their Rocq memory images.
The original proofs establish allowed halting, permitted failure, equivalent padded execution,
and a refutation for exit status 1. The original checker must also reject all five admission
controls at their declared step and reason: `Admitted`, an extra axiom, the standard-library
admit axiom, a wrong statement and a doctored statement. A setup failure is not a passing
negative control.

## Exact boundary

[pins.json](pins.json) fixes the upstream commit, checker OCI digest and all 47 files in the
bounded source subset (189,516 bytes), including the unchanged proofs, statements, checker,
ELF generator and axiom allowlist. No upstream proof code is vendored. The workflow uses a
sparse checkout and verifies its HEAD; the wrapper independently hashes every selected file,
copies only those files to a fresh directory and rehashes the mounted bytes. Extra checkout
files never enter the checker. This sparse layout is a bootstrap variation to qualify in CI;
it has not been represented as an already successful upstream run.

The public checker is pinned to
`ghcr.io/theorem-labs/oss-fuzz-theorems-checker@sha256:cc9ae43a9f4b0dd59d7c8d30727d36e039bfe72a2a9f9c4a99c68e413037e902`
(Linux/amd64). It contains Rocq 9.2.0, Dune 3.23.0 and published Linux Process Semantics;
its pinned release identifies LPS commit `f1006fe8178338a499b5e5c41be83006c4edd058`.
The image download is about 1.33 GB compressed. A pinned image is an exact-byte dependency,
not evidence of an independently reproduced build or a complete Linux/CPU model.

The wrapper requires a native Linux/amd64 Docker daemon and refuses an emulation substitution.
After separate public image acquisition, the checker has no network, capabilities or forwarded
credentials. It runs as the host user, with a read-only root filesystem and input mount,
private writable work/tmp filesystems, two CPUs, 6 GiB RAM, 256 processes and a 900-second
execution limit. The job has a 30-minute cap, including a 600-second image-pull limit.
Both Python cleanup and an unconditional workflow cleanup remove its uniquely named container.
Only the evidence directory is writable on the host; the repository and Docker socket are
not mounted into the container. The host Docker CLI is the trusted execution mechanism.

## Run and evidence

Choose `experiment=rocq` on the existing manual `.github/workflows/check-proof.yml` workflow.
It adds one isolated job, read-only checkout credentials, no automatic trigger, no product CI
and no new required gate. Concurrent capability jobs queue rather than overlap.

For a prepared exact upstream subset and an already pulled image on a Docker-enabled Linux host:

```sh
python3 scripts/check_rocq_capability.py \
  --source-root /path/to/pinned/upstream \
  --evidence-dir .artifacts/rocq-evidence \
  --json-out .artifacts/rocq-result.json
```

The evidence directory must be new. `--validate-only` checks source identities without Docker
and reports `inputs_validated_only`, never native acceptance. The container invokes the
unchanged official commands in sequence:

```sh
dune build --root . @theories/default @tests/default
./tests/check.sh
```

Each official exit is retained; all must succeed, and the generated ELF hashes must match the
published pins. The wrapper supplies no replacement proof checker or theorem. It retains the
exact Docker argv and inspected image identity, source hashes, versions, build/checker exits,
wall time, generated binary hashes and the producer's per-control compilation, wrapper and
assumption-audit logs. Setting `TMPDIR` under retained evidence preserves the producer's temporary
control logs even on failure. Actions uploads only those records for 14 days, excluding the
build cache. A timeout or resource failure remains a failed attempt, not a semantic refutation.
`cleanup_exit` records Docker's raw result; exit 1 after successful `--rm` can simply mean that
there is no remaining container.

The default producer check compiles Rocq proof terms and checks exact statement ascription and
its explicit axiom allowlist. It does not run optional independent `rocqchk --full`; that is a
separate cost/assurance decision. The allowed assumptions include Rocq primitive-type axioms
and standard-library logical axioms. This is not an axiom-free proof, native RISC-V execution,
proof of Node/V8, or demonstration of an open-source automatic proof-generation system.

After this checkpoint succeeds, a useful new implementation, domain property, pinned compiler,
complete ABI and proof-construction plan still need qualification. Experimental language choice
is open. Production replacement and second-implementation proof reuse remain separate decisions
and uncompleted milestones.
