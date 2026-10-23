# Local established-tool result, 2026-10-23

PASS for the scoped complete emitted settlement function under the [declared domain and trust
boundary](README.md). Candidate exact-commit review and hosted result follow this builder record.

| Control | Actual Gillian result |
| --- | --- |
| Baseline | Four specifications succeed |
| Equality changed to inequality | Two postconditions fail |
| Wrong returned version | One postcondition fails |
| Unconditional fallback promotion | Three postconditions fail |
| Equivalent removal of nonnull conjunct | Four specifications succeed |
| Harmless layout/comment change | Canonical emitted bytes equal baseline;123 native cases agree |
| Unapproved whole-file drift | Rejected by source pin |

Each variant has123 native fixtures; original/equivalent variants have zero policy differences.
Bad comparison has25, wrong version5, unconditional promotion118. These finite results support
nonvacuity and interpretation of the mutations; the symbolic verification result comes from
Gillian's body analysis of four universally described pre/post cases, not enumerating fixtures.
The comparison-mutant evidence explicitly includes both failed own-version recovery and false
acknowledgement of actual="other" when local="local". The wrong-version witness recovers a matching
conflict with the wrong receipt value. These are intentional mutants, not current product bugs.

First integrated local checker1.4985s; final expanded checker1.2100s across recorded subprocesses,
excluding setup, archive hashing and evidence-copy bookkeeping. Final checker includes five
verification invocations (each under0.5s locally), native preparation and stale-source control.
Re-extraction/setup from cached verified archives took0.3204s; this is not a cold-network timing.
No opam, Docker daemon or framework build was needed. The macOS archives total46,048,296bytes;
Linux pins total62,533,030bytes. Binaries stay outside git. Peak memory, construction tokens and
dollar usage were not instrumented and are not estimated. Full-application cost is unknown.

## Actual failed attempts

The first TypeScript transpile used module=None with isolated-module ES5 settings and was rejected
by compiler option validation. Selecting CommonJS for the isolated non-exported script resolves
that setup error; the output has no module wrapper or generated helper.

The initial four-case contract gave the null-conflict case no owned local property, even though
the intended interface domain requires own local:string in every case. Baseline passed, while the
equivalent-conjunct-removal variant failed a missing-heap-field obligation when it read local.
Making that declared input domain consistent in every pre/post restored semantic equivalence.
The independent behavioral postconditions were retained. This was a specification boundary
correction, not a product defect or evidence that a real code bug was repaired.

Early executable help before Z3 was onPATH failed for missing Z3. Archive extraction during
research needed compatibility with the installed Python tar API; final setup validates archive
entries and writes regular files directly. Neither failed invocation analyzed a product function.

## Evidence and interpretation

Raw local logs, seven exact input hashes, transformed source/emitted hashes, per-case verdicts,
native witnesses, full annotations, pinned archive/executable receipts and failed attempts are
retained in artifacts/verification-path-decision-20261023 in the coordinator workspace. The source
pin and checked scripts make the experiment reproducible subject to archive availability. The
mutable nightly URL may require an explicit tool repin; digest mismatch never silently upgrades.
A source tag observation is not a reproduced-build attestation.

There is no custom interpreter/decoder addition here. TypeScript, Gillian JS-to-GIL/model/verifier,
Z3 and actual-runtime correspondence remain trusted. Four successful specifications are not a
kernel-generated proof certificate, and native UTF16 fixtures do not prove universal model-to-V8
string correspondence. No storage or asynchronous protocol correctness claim follows.
