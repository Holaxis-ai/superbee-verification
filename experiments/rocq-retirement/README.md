# Experimental typed acknowledged-retirement component

This component is written as executable Rocq source. `Kernel.v` owns the complete typed decision;
`Specification.v` independently states admission and output/frame laws. Only `Proof.v` is revised
by the bounded agent/checker loop after the contract files are frozen. Native checker results,
not this README, determine whether any candidate is accepted.

The boundary takes a supplied document snapshot, complete supplied same-target record set, named
metadata premises, selected IDs and metadata removals. It checks the full optional document
version/raw payload, unordered complete record equality, target consistency, unique IDs and
sequences, metadata presence/value, nonempty unique acknowledged-only selection and unique
removals scoped to named premises. It returns either no mutation (`None`) or exact ordered
remaining records/metadata, unchanged document and precisely requested removals. No external
callback supplies equality, guard matching or admission.

All modeled record fields are compared: identity, target, sequence, all six status constructors,
payload and opaque residual payload. No residual field is ignored by equality. Opaque payloads
are typed lists of naturals here; no claim is made that they are decoded production bytes or
canonical JSON. Natural IDs/sequences are a deliberate new representation without JS safe-integer,
UUID, path or nonzero validation. Those are separate schema decisions. Caller-supplied snapshot
truth/completeness relative to actual storage remains a premise, not something this pure function
can establish.

Metadata has three different observations: absent row, present undefined (`None` value), and
present value including an empty value. The specification expresses these using membership and
absence, separately from the executable lookup. The actual metadata view may include unnamed
rows, which remain unchanged. A named absent metadata key may be removed. Guard record order may
change without refusing; uniqueness prevents equal-member guards hiding duplicate identities.

`retirement_correct` requires admission soundness and completeness, exact successful outputs,
refusal iff admission is false, independent remaining-record and metadata membership/frame laws,
and preservation of every unacknowledged row. Its fixed useful positive witness removes one of
two acknowledged rows, retains the second and an unknown outstanding row, checks a permuted guard,
preserves the document and an unnamed metadata value, and removes a present-undefined and named
absent key. This prevents an always-refuse candidate passing as a useful component.

The selected production correspondence reference is `captureRetireAcknowledged` and
`assertJournalGuard` in `packages/core/src/journaled-backend.ts` at
`2d856c492f146a14e71ee2aafac3f4bc593fe942`. This is a **new experimental typed implementation**,
not a proof of that TypeScript, JS object capture, deep JSON grammar, codec, binary, extraction,
backend transaction or actual storage preservation. No production behavior changes here.

A successful proof establishes laws about this actual Rocq decision function under its typed
boundary. The broader substantial-component and second-implementation proof-reuse milestones
remain open until separately assessed. Proof reuse, extraction and process/wire integration are
subsequent gates, not consequences of installing the checker.
