# Implementation-proof pipeline milestone

Current research direction: establish a useful property of a substantial actual Superbee implementation,
then demonstrate transfer of proof machinery and reusable proof components to a second implementation
target. This replaces treating additional isolated helper proofs as the overall project's success
criterion. The earlier qualified results and their narrower adoption rules remain valid.

## What counts as success

1. Select a real component and independently useful property before selecting the easiest theorem.
   Record its complete entrypoint, dependencies, input domain, artifact identity and failure mode.
   Substantial means a meaningful implementation boundary and its relevant dependencies, rather
   than a line-count target or another isolated Boolean clause.
2. Qualify published proof infrastructure and execution semantics against that implementation.
   Investigate the article's released tools and alternatives; establish the TypeScript/JavaScript,
   compiler/runtime/library bridge explicitly. An abstract rewrite of the component is not an
   implementation proof. No new private interpreter, production language rewrite or full Node/V8
   binary campaign is authorized merely by this milestone.
3. Check the property with an established native checker, precise theorem/specification, exact
   inputs, explicit trusted assumptions, useful positive behavior and meaningful negative controls.
   Kernel proof, symbolic verification, bounded model checking and testing retain distinct labels.
4. Demonstrate reuse on a second implementation target with independently accepted evidence.
   Identify unchanged/adapted/new proof components and their dependency versions. Sharing a tool
   executable, two internal lemmas or task prose alone does not meet the transfer criterion.
5. Measure construction and checking cost where observable, preserve unknowns and failed attempts,
   review usefulness/correspondence independently, and document limitations. The result need not
   equal Anthropic's binary-level achievement to be useful, but must state precisely what remains.

This milestone is open. Installing a recipe does not complete or start an unbounded proof campaign.
No claim is made that the current experiments prove a substantial complete component or demonstrate
second-implementation proof transfer. Budget-intensive execution needs a concrete scoped plan.

## Coordination

The [verification-pipeline recipe](../recipes/verification-pipeline/recipe.md) declares cases,
obligations, reusable components and exact runs. Existing project Tasks own delivery claims and
permissions; Reviews own independent judgments. The selected superbee-dev bundle is the work record.
Proof sources and large logs stay here or in artifact storage. Preserve source/checker identity and
link dependencies so changes can be assessed. Automatic invalidation, scheduling and CI ingestion
are not implemented by the recipe.

The existing GitHub source plugin provides issue observations, not proof-run ingestion. A later
checker-result profile can reduce transcription and coordinate evidence only after a real target
establishes stable output/identity contracts. It must keep provider observations separate from
reviewed obligation discharge. Recipe installation never activates that integration.

## Continuing boundaries

[VERIFICATION-PATH.md](VERIFICATION-PATH.md) records the earlier pure-function qualification and
trust assessment. Its refusal to claim unsupported execution semantics remains applicable; its
small-target scope is no longer the ambition ceiling for research qualification. Existing Lean,
Gillian and TLC results retain their exact original claims and source pins. Do not strengthen them
by reclassifying metadata. Product runtime, mandatory CI, release, disclosure and deployment gates
are unchanged. No automatic product proof gate or significant spend is introduced by this document.
