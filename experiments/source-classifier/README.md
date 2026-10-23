# Source-derived classifier proof

Status: experimental source-derived semantic proof. The parser, lowering and adequacy of the
restricted semantics are trusted. This is not a proof of all TypeScript, compiled JavaScript,
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
| TypeScript parser and AST lowering | Trusted, pinned and independently reviewed; not formally verified |
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
python3 scripts/check_bridge.py \
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
