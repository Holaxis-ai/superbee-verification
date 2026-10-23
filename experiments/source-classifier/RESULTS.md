# Local source-bridge result, 2026-10-23

PASS for the restricted source-derived semantic experiment, conditional on the trusted components
and runtime assumptions in README.md. This is not a full proof of shipped TypeScript/JavaScript.
Exact-source independent code review and hosted run follow this builder result.

Product sourcea63eef111001974a89ce35a83759bbe183814a1c, whole-file SHA-256 in source-pin.json.
Pinned TypeScript5.9.3, Node24.22.1, Lean4.27.0. No product checkout dependency installation,
build, runtime modification or CI gate was added. Generated ASTs and fixtures are not committed.

| Check | Result |
| --- | --- |
| Universal baseline policy and independent set equality | pass; standard propext/Classical.choice/Quot.sound only |
| Native baseline vs independent policy |112 cases,0 differences |
| AND→OR actual-source mutant | Unchanged claim rejected; concrete policy counterexample kernel checked;50 native policy differences |
| Wrong-code actual-source mutant | Independent policy equality/claim rejected; concrete counterexample kernel checked;2 native policy differences |
| Native result replay through generated AST |112 cases each for baseline and both mutants, all kernel replay checks pass |
| Unsupported call | Rejected before transpilation/execution |
| Any whole-file source drift | Rejected by the source pin |

First complete pipeline6.9589s; final builder pipeline6.5049s across recorded stage commands.
Both exclude initial parser/toolchain installation; the parser install added one package in0.624s
on this machine, not a clean-network performance guarantee. Native/replay case counts include
both absent code and own-property undefined. Generated Lean source including all finite native
replays40030bytes, all temporary. Proof-construction token/dollar usage was not instrumented and
is not estimated here. The result is small because the grammar and target are deliberately small.

## Actual failed attempts

The initial theorem draft failed elaboration/style checks because the ASCII policy tag needed an
explicit checked equality with its UTF16 literal representation, and two unused simp arguments
were rejected as warnings. A checked tag equality lemma resolved this without changing the policy.
The first full harness run failed before the generated module could be checked because its Lean
package root pointed at the repository rather than the temporary generated-source directory.
An explicit temporary package root fixed the harness. Neither was a production defect.

A source-derived proof depends on the trusted translator and restricted semantics. Matching finite
native executions does not prove those components correct. The semantic mutants have independent
kernel counterexamples, so their failure is not inferred solely from proof-tactic rejection.

The next implementation-proof milestone must certify/replace this trusted bridge or adopt a
suitable established execution model before widening claims. This experiment does not establish
that Node/V8 or a full journal/storage implementation can be proved at this cost.

## Independent byte-decoding follow-up, 2026-10-23

The earlier result above describes the first bridge. The follow-up adds pure Lean decoding of
complete original declaration byte spans, not a verified general TypeScript parser. External
TypeScript lowering is now cross-checked by a kernel-reduced independent decoder before linking
the decoded program to the unchanged universal policy. Grammar/ECMAScript adequacy, acquisition,
span selection/embedding, surrounding module context and runtime assumptions remain trusted.

Local integrated run passed in 37.9416s summed stages, including the earlier source/native suite
(6.9107s internally; 7.2403s outer wall time), fresh decoder compilation (10.042s), original and
two mutant decoding certificates, decoded-source policy, three corrupted generated-artifact
rejections and seven unsupported-source rejection proofs. Each individual subprocess remains
limited to60s. Setup costs and construction token/dollar cost remain excluded/uninstrumented.
The decoder is deliberately small; these timings are not full-application estimates.

Pinned original byte spans are [10267,10480) and [10574,10752). Their concatenation with two
newlines and a final newline has SHA256
`0a1ba5db2b3deb5bc5a67ec706910d1f41218709d0079b018e56a73473ce9abf`.
All accepted certificates use only propext, Classical.choice and Quot.sound. Corrupted external
program, tag encoding and set contents each make the correspondence certificate fail. Existing
actual-source mutations still decode, fail the unchanged policy and retain checked counterexamples.
Unsupported-source controls include return-newline ASI, additional statement, optional access,
default argument, extra call, escaped literal and trailing declaration.

Actual failed attempts were retained. A parser-level parenthesis example caught Lean nested
`return` exiting before the enclosing continuation; using `pure` restored the intended parse.
Independent design review caught split operator acceptance and return-newline ASI; the lexer now
requires contiguous operators and rejects line terminators after return. The first integrated
certificate run also failed because saved evidence omitted compiled generated modules; recompiling
those inputs freshly fixed module resolution. No intended policy was weakened, and none of these
verification-tool failures is presented as a production bug. Exact-candidate independent review
and hosted manual run are recorded in the linked Superbee follow-up task after completion.
