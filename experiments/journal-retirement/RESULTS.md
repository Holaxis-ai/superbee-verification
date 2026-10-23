# Initial result, 2026-10-23

Status: **kernel-checked abstract policy experiment**, not an implementation correctness claim.
No independent semantic review has been completed.

- Lean4.27.0, compiler commit db93fe1608548721853390a10cd40580fe7d22ae, macOS arm64.
- Eight checked theorems, including one-step and arbitrary finite retirement-sequence preservation,
  concrete loss without admission, and a nonempty admitted-retirement example.
- Dependencies printed by Lean: only standard `propext` and `Quot.sound`, varying per theorem.
  No custom axioms or proof placeholders; generated audit checks every named theorem in this file.
- Final proof source132 lines /5575 bytes, SHA-256
  `79aa2ea267e4603fe887a0db940de2b3cda93ebdc7483c27844d02ccad682ab5`.
- Clean local compilation1.4618s; axiom audit0.1632s; required false-claim rejection0.1687s;
  total1.7937s. Fresh output directory, preinstalled toolchain; this excludes installation and
  does not imply a cold machine/filesystem cache. The rejected proof exits1 with an unsolved
  false goal; compile/audit exit0.
- Source identity checker accepted exacta63eef checkout/bytes (exit0), and rejected its different
  a2c6cda predecessor as stale (exit1). Temporary inspection checkout removed normally.
- Initial six-theorem draft compiled with one style warning; it was corrected. Positive nonempty
  admission witnesses were then added and all eight rechecked. No failed semantic proof or product
  bug was found; the unsafe removal is a deliberate control.

Reproduce with `python3 scripts/check.py --json-out .artifacts/check.json`. Receipts and binary
outputs stay untracked. The hosted result below records Linux setup/job timing separately.

The low cost reflects a deliberately small policy theorem. It does not establish feasibility of
full TypeScript, browser, storage or lifecycle proofs. Next work is independent statement/source
mapping review and assessment of a credible implementation bridge before expanding scope.

The initial hosted run39974502799 on bootstrapaaf8d0b stopped in action configuration because
lake-manifest.json was absent. It installed the pinned toolchain but did not execute the proof.
The follow-up adds Lake's generated manifest with an empty packages list; proof bytes are unchanged.
This setup failure is retained and is not counted as a failed theorem or a passing proof run.

## Hosted result

[Manual run39974787379](https://github.com/Holaxis-ai/superbee-verification/actions/runs/39974787379)
passed on exact973984d7320d2cff9c735c39bed5dce6e1c28c5d, standard ubuntu-latest, Lean4.27.0 Linux
x86_64. Clean compile0.4760s, axiom audit0.2349s, required false-claim rejection0.2559s: total
proof check0.9668s. The entire job took15s (15:02:22Z–15:02:37Z), including toolchain setup.
No proof-output cache or external Lean library was used. This is one observation, not a performance
guarantee. The documentation update reporting this result changes no checked proof or workflow input.
