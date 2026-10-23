---
type: Reference
title: Verification pipeline workflow and evidence admission
---

# Verification pipeline workflow

## Purpose and success criterion

The larger research milestone is a useful property of a substantial actual implementation plus demonstrated reuse of proof machinery and components on a second implementation target. More small helper proofs, copied prose, a recipe installation or two internal lemmas do not by themselves meet that milestone. Choose the target and property independently of tool convenience; qualify execution semantics before promising code coverage.

## Records and responsibilities

- VerificationCase: target, property, input domain, execution semantics, trusted assumptions, source/artifact revisions and desired milestone. New cases supply assurance and progress_status. Existing narrative records remain valid historical evidence.
- Proof Obligation: one precise statement, assurance class, progress_status, subject/spec revisions, assumptions, optional assignee and linked case. Split only where separate proof/checker dependencies justify independent work. Use the existing Task for delivery claims, permissions and merge gates; obligation assignment is not a second delivery lock.
- Proof Component: a reusable statement/proof with exact symbol, artifact revision/digest/URI, toolchain, assumptions and reuse scope. A checked component needs a supported-by run. Distinguish observed internal theorem reuse from transfer to a second implementation. A shared script, decoder or execution model can be a supporting dependency described in the body; it is not automatically a proved lemma.
- VerificationRun: verdict, assurance, exact artifact/source revisions, complete checked-input manifest, pinned toolchain, evidence URI and measured costs. Missing costs stay omitted or explicitly unknown in prose, never fabricated as zero. A run can accept expected negative controls while the mutant itself fails its property. Preserve that distinction and retain raw counterexamples.

All records use exact existing ids and normal links. Dependencies use `depends on` between obligations; `reuses` points to Proof Component; `checks` and `discharges` point from a run to an obligation; `requires` points from case to obligation; `for case` points to VerificationCase; `supported by` points to VerificationRun. Preserve historical links. Do not install instances with the recipe or duplicate Tasks/Reviews.

## Evidence classes and admission

- kernel_proof: a named statement accepted by the pinned proof kernel, with axiom dependencies and semantics assumptions explicit.
- symbolic_verification: acceptance by a symbolic verifier/solver under its stated model and domain.
- bounded_model_check: complete exploration only within recorded bounds, with fairness stated for liveness.
- testing: empirical execution, never a universal proof.
- assumption: an unproved premise, never silently counted as discharged.
- unqualified: research target/toolchain not yet qualified; no assurance claimed.

An established obligation must name its exact statement/specification and subject revision, carry a matching assurance class and link supporting checker evidence. A discharges edge is admissible only when independent statement/correspondence review accepts the evidence and input/domain/assumption identities match. An accepted CI job alone is insufficient. The conventions enforce field/value shapes; they cannot enforce these semantic conditions or claim that an assumption was proved.

## Agent loop

1. Claim the existing delivery Task with CAS; select the case/property and inspect predecessors and current evidence.
2. Qualify an established execution/proof model against the actual component. Record unsupported runtime/compiler/library behavior as a gap, not a successful proof.
3. Create obligations, assign bounded work, and search component statements/assumptions before authoring another proof. Record dependency versions in the exact input manifest.
4. Agents build or adapt proofs in the owning repository, preserve failed attempts/counterexamples, and return exact artifacts. Independent review checks statement usefulness, semantic correspondence and assumptions. Genuine negative controls and useful positive behavior test vacuity.
5. Run the native checker on exact frozen inputs. Preserve tool version, axioms/trusted components, verdicts, raw outputs and costs in a run, then relate reviewed compatible obligations/components. Existing product shipping/release gates remain unchanged.
6. Demonstrate transfer to the second implementation with independently checked runs and explicit reused component identities. Measure reused/changed/new work where possible; reusing the tool executable alone does not meet proof-component reuse.

## Changes and freshness

Changing source, statement, assumptions, semantics, compiler, checker or dependency invalidates the applicability of earlier evidence to the new tuple. Preserve the old run and qualified historical statement. Record a needs_recheck status/reason on affected current obligations/components/cases through CAS, follow backlinks to enumerate dependants, and require a new run before restoring current applicability. Do not rewrite old runs as if they checked new bytes.

This version supplies relationships and a workflow, not automatic transitive invalidation, cycle detection, scheduling or source monitoring. Backlinks help inspect impact; an executable integration must implement and test any automatic freshness decisions. Dates alone are not proof freshness. Exact identities matter.

## Integration boundary

A Superbee source plugin/Connector is useful for importing native checker/CI observation metadata and exact artifact identities without manual transcription. It is optional for authoring/replay. Recipe installation must never acquire credentials, execute a checker or contact providers. Provider-owned observation fields must be separate from human/agent-owned statement, assumption, assignment and reviewed-discharge decisions. Imported pass is observed evidence, not automatic proof admission.

The inspected distributed GitHub plugin exposes github-issues, not proof/Actions result ingestion. Source run updates explicitly linked existing documents; do not assume it creates a proof graph. A future proof-run profile requires exact source/spec/tool/input matching, bounded recorded-fixture tests for error/stale/partial/conflict/counterexample handling and explicit binding/permissions. Do not add an unimplemented Connector or promise automated proof tracking in this recipe. Native checker artifact formats and stable identities should be established by the first substantial proof target before implementing that adapter.

## Authority and storage

Proof sources and large logs remain in the verification repository or artifact store. Superbee preserves statements, provenance, relationships, coordination and evidence links. Existing Tasks, Reviews, repository policy, private security routes and user permissions retain authority. This recipe does not add required product CI, change runtime languages, authorize spending, or declare binary/runtime correctness. Treat any actual sensitive production finding through the project's private disclosure route.
