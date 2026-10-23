---
type: Recipe
id: verification-pipeline
title: Verification Pipeline
version: 0.1.0
summary: Exact verification targets, proof obligations, reusable components and native-checker
  evidence.
content_policy: definitions-only
references:
- references/verification-pipeline-workflow.md
---

# Verification Pipeline

Coordinate agent-assisted proof work using explicit statements, dependencies and reproducible evidence. Installs four conventions and workflow guidance; no instances, provider access, executable module, proof runner or automatic scheduling.

Compose with the project's existing Task and Review kinds. This recipe neither owns nor changes them. Install from the recipe directory with `superbee recipe add /absolute/path/to/recipes/verification-pipeline --dir /explicit/existing/bundle --actor openai/codex`. Inspect existing conventions and run recipe validate first. Generic legacy VerificationCase/VerificationRun records retain their names and bodies; explicit selected CAS updates can add fields. An incompatible existing convention must be resolved through reviewed recipe evolution, never overwritten.

The recipe records kernel proofs, symbolic verification, bounded model checking, testing and assumptions separately. Proof artifacts stay in their owning repository/artifact storage; the native checker remains authoritative. See the installed workflow reference for claims, freshness, evidence, reuse, integration boundaries and acceptance criteria.
