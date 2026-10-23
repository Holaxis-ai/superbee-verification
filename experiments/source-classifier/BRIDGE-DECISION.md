# First implementation-bridge decision

Choose mechanically derived source syntax plus explicitly trusted restricted semantics for the
first feasibility experiment. This closes manual transcription, source drift and vacuous
source/specification coupling risks. It does not close parser, translation, semantic-adequacy or
actual engine/compiler correctness gaps. The result must be called a source-derived semantic
proof, never a full shipped-JavaScript or binary proof.

| Route | Evidence and present fit | Decision |
| --- | --- | --- |
| Existing ECMAScript formal interpreter | [JSCert](https://github.com/jscert/jscert) describes ES5 and verified reference interpretation. Native Set and modern TypeScript need additional treatment. | Useful research baseline; not a drop-in checker for this function. |
| Article's binary route | [Theorem Labs proof release](https://github.com/theorem-labs/oss-verify-proofs) targets RISC-V executables under an explicit Linux-process model. | Applying it to this application requires including/abstracting a JS engine or changing the implementation pipeline; not established by this experiment. |
| Verified generation/extraction | Generate executable behavior from a proved definition, then trust or verify extraction and the deployment compiler. | Potentially stronger bridge, but changes the production source pipeline and needs a separate adoption decision. No runtime rewrite authorized here. |
| Trusted restricted source lowering | Parse the actual complete pure function, fail closed on unsupported syntax, prove over its emitted AST and test semantic mutants. | Chosen for the scoped first connection; trust remains visible and bounded. |
| More handwritten mathematical models | Cheap policy proofs, as in the initial retirement experiment. | Retain for design, but not sufficient to claim source correspondence. |

The [TypeScript compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API)
owns parsing; the experiment pins its package/lockfile. Semantics are manually compared with
[ECMAScript logical operators](https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-binary-logical-operators-runtime-semantics-evaluation)
and [Set.has](https://tc39.es/ecma262/multipage/keyed-collections.html#sec-set.prototype.has).
Under pure Boolean operands, ordinary string data properties and unmodified native string-only
sets, the small rules match those operations. This correspondence is reviewed, not itself proved.

Independent plan review required an independent six-code specification, missing-code inputs,
true UTF-16 representation, runtime Set assumptions, fresh source-derived generation, semantic
mutants with checked witnesses, and explicit limits. Those requirements shaped this experiment.

## What would justify expansion

First certify or replace the trusted lowering/semantics for a bounded reusable language fragment,
with a stated trusted computing base and replayable validation. Then select a real journal guard
with state and atomicity obligations and assess the additional semantics it needs. Broader
lifecycle proofs require a connection to actual transition implementations and storage behavior,
not merely more inductive constructors. Larger proof infrastructure and automatic/required gates
need a measured cost and scope decision after that evidence exists.
