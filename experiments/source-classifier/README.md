# Source-derived classifier proof

Status: experimental source-derived semantic proof. An independent Lean decoder checks exact restricted declaration bytes against the externally
lowered AST. Adequacy of that reviewed grammar and restricted semantics remains trusted. This is not a proof of all TypeScript, compiled JavaScript,
Node/V8, authorization enforcement, the full uncertain-write protocol or journal preservation.

## Actual implementation target

The complete `isAuthorizationRefusal` function and its `AUTHORIZATION_REFUSAL_CODES` initializer
come from `packages/core/src/uncertain-write.ts` at public Superbee commita63eef111001974a89ce35a83759bbe183814a1c.
[source-pin.json](source-pin.json) binds the complete input file SHA-256. Source is read from an
explicit checkout and never edited by this experiment. It is not hand-copied into a Lean behavior
function. A pinned TypeScript5.9.3 parser reads its AST, and a small fail-closed lowering emits
`SourceGenerated.program` and `SourceGenerated.codes` as data consumed by the Lean interpreter.

This predicate distinguishes authorization/quota refusals that pause further shared operations
from other refusals. Its role makes classification useful to verify; this result does not prove
the caller handles that classification correctly.

## Checked statements

- `source_codes_match_policy`: extracted initialization matches the six independently specified
  policy codes. Changing source data cannot silently redefine the intended policy.
- `source_true_requires_refusal`: for arbitrary set contents, a true result requires refused kind.
- `source_classifier_exact`: with the initial configured set, interpretation returns true exactly
  for refused outcomes carrying an approved code. Soundness and completeness quantify over all
  modeled inputs, not just enumerated test cases.

Strings are lists of UTF-16 code units. Real JS strings, including lone surrogates and non-BMP
pairs, are covered by that representation; the mathematical domain additionally includes invalid
code-unit Nats, which does not exclude any real string. `kind` is a string and `code` is a string
or missing/undefined. This includes valid Outcome variants without code. Other value types are
outside the domain. Boolean-valued short-circuit AND/OR, strict string comparison and native
string-only Set membership are the only execution operations.

The source-derived mathematical proof consumes generated syntax. It does not merely prove a
handwritten desired predicate or assume a Boolean saying the source is equivalent. The Lean kernel
checks theorems using only standard logical axioms, printed and audited by the runner.

## Trust and excluded environments

| Component | Status |
| --- | --- |
| Lean theorem derivations over generated syntax | Kernel checked; source-input hashes and axiom dependencies recorded |
| Product acquisition and identity | Exact commit in manual CI plus whole-file hash; changed bytes fail closed |
| TypeScript parser and AST lowering | Pinned and reviewed; output must additionally match independent kernel-reduced decoding of the original declaration bytes |
| Lean restricted-source decoder | Executed by kernel reduction; grammar adequacy to TypeScript/ECMAScript is reviewed, not formally proved |
| UTF-16 encoding and restricted semantics vs ECMAScript | Explicit small model, manually mapped; not a proved refinement of the standard |
| Native transpiler and Node/V8 execution | Trusted; fixture agreement is empirical and not universal runtime conformance |
| Input records and set/builtin environment | Assumed ordinary side-effect-free data properties; no getters, proxies, prototype surprises or concurrent mutation |

`ReadonlySet` and `const` do not freeze runtime contents. The fixed-policy theorem assumes the
exported set retains its initialized contents and native Set/.has meanings. The no-false-kind
lemma quantifies over arbitrary string-set contents, but still assumes ordinary native membership
and pure property reads. Nothing here proves those runtime assumptions or authorizes production
changes to enforce them.

## Controls

The checker first verifies the pinned input, then creates temporary controlled source mutations
and parses/lowers each again. Replacing AND with OR and changing FORBIDDEN to NOT_FORBIDDEN must
fail the same independently specified theorem. Each mutant also has a kernel-checked concrete
policy counterexample. A rejected proof script alone is not treated as evidence of a false claim.

Each of baseline and two mutants executes112 native cases, including six positive codes, missing
and explicitly undefined code, unknown codes, empty strings, lone surrogates and non-BMP strings.
Kernel reduction replays those observed results on the generated AST. These finite agreements
support the bridge engineering; they do not discharge its trusted semantic connection.
Unsupported call syntax and any unapproved source drift are separate fail-closed controls.

## Reproduce

Install the pinned Lean toolchain and Node24.22.1, then in this repository:

```sh
npm ci --ignore-scripts --no-audit --no-fund
python3 scripts/check_source_decode.py \
  --source-file /path/to/pinned-superbee/packages/core/src/uncertain-write.ts \
  --json-out .artifacts/bridge-result.json \
  --evidence-dir .artifacts/bridge-evidence
```

Every subprocess has a60s limit. Fresh temporary output prevents stale compiled proof reuse.
No generated syntax, native fixtures, compiler output or large binary is committed. The existing
manual workflow now has an isolated source-bridge job,10min maximum on standard ubuntu-latest;
it sparsely reads the pinned public product source without installing/building the product.
There is no automatic trigger, production dependency, required product CI gate or runtime rewrite.

## Feasibility decision

This demonstrates a maintainable source-coupling path for a very small pure fragment, conditional
on a trusted translation and explicit semantics. It has not reproduced the article's direct
binary proof. The next scaling decision must address certification of that bridge or adoption of
an established execution model before widening implementation claims. Extending a whitelist to
async state recovery without such work would grow an unverified JavaScript model, not eliminate
the gap. Do not generate or adopt a new production implementation without a separate decision.

See [bridge alternatives](BRIDGE-DECISION.md), local/hosted measurements in RESULTS.md and the
[Superbee task](https://github.com/Holaxis-ai/superbee-dev/blob/board/tasks/connect-mathematical-proof-to-shipped-code.md).

## Independent source-byte check

The source pin now records two reviewed half-open byte spans in the immutable original file:
complete set declaration and complete function declaration. The Python runner reads those slices
directly, independently of TypeScript node positions or string decoding, joins them with whitespace,
and checks they equal the extracted declarations. The exact original bytes are embedded as numeric
lists in an ephemeral Lean input. Source acquisition, span review and numeric embedding remain part
of the external trust boundary; surrounding module execution is not checked.

`Bridge/SourceDecode.lean` independently recognizes a deliberately narrow grammar and reconstructs
Expr and code data. Lean checks `decode declarationBytes = some (generatedProgram, generatedCodes)`
by ordinary kernel reduction, then connects this result to the existing universal policy theorem.
The external TypeScript parser/lowering can no longer silently provide a different accepted AST.
This is not a proved-correct general TypeScript parser: the recognizer's grammar and its relation
to real TypeScript/ECMAScript are still reviewed assumptions.

Accepted source is ASCII with unescaped double-quoted printable literals, explicit known signatures,
exactly six set entries with trailing commas, ordinary kind/code reads, native membership syntax,
Boolean literals, parentheses, strict comparison,
AND and OR. Non-ASCII/escaped source literals and other language features are deliberately rejected;
this restriction applies to program text, not the theorem's arbitrary UTF16 runtime input strings.
Extra statements, optional access, defaults, calls, whitespace-split operators and trailing
declarations must fail closed. A line terminator after `return` is rejected to respect automatic
semicolon insertion.
Both controlled source mutants still decode successfully but violate the unchanged policy.
Separate controls retain original source while corrupting the external AST, literal encoding and
set contents; each correspondence proof must fail. No native-decision oracle is used.

The manual source-bridge job runs this checker, which includes the previous checker once.
This reduces reliance on external syntax lowering; it does not verify the JS engine, native Set,
module environment, actual runtime values or the decoder's adequacy to the language standard.
