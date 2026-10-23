namespace SuperbeeVerification

structure Row where
  requestId : Nat
  /-- Symbolic tag for a complete immutable edit payload, distinct from request identity. -/
  payload : Nat
  acknowledged : Bool
  deriving DecidableEq, Repr

structure State where
  journal : List Row
  view : Option Nat
  accepted : List Nat
  discharged : List Nat
  deriving Repr

/-- Acknowledgement bookkeeping is a trusted premise of this focused theorem. -/
def Valid (s : State) : Prop :=
  ∀ row ∈ s.journal, row.acknowledged = true → row.payload ∈ s.discharged

/-- Only local working content and payload-bearing journal rows count as recovery copies. -/
def Preserved (s : State) : Prop :=
  ∀ edit ∈ s.accepted, edit ∉ s.discharged →
    s.view = some edit ∨ ∃ row ∈ s.journal, row.payload = edit

/-- The acknowledged-only admission rule; full snapshot/target guards are outside this model. -/
def Admitted (s : State) (ids : List Nat) : Prop :=
  ∀ row ∈ s.journal, row.requestId ∈ ids → row.acknowledged = true

/-- One abstract atomic removal; metadata and predecessor scheduling are not modeled. -/
def retire (s : State) (ids : List Nat) : State :=
  { s with journal := s.journal.filter (fun row => decide (row.requestId ∉ ids)) }

/-- No finite journal-size or payload bound: a permitted retirement preserves every
    outstanding accepted edit, assuming valid acknowledgement accounting and atomic removal. -/
theorem retire_preserves_outstanding (s : State) (ids : List Nat)
    (valid : Valid s) (preserved : Preserved s) (admitted : Admitted s ids) :
    Preserved (retire s ids) := by
  intro edit accepted outstanding
  rcases preserved edit accepted outstanding with view | ⟨row, member, payload⟩
  · exact Or.inl view
  · have retained : row.requestId ∉ ids := by
      intro selected
      have discharged := valid row member (admitted row member selected)
      rw [payload] at discharged
      exact outstanding discharged
    exact Or.inr ⟨row, by simpa [retire, retained] using member, payload⟩

/-- Valid acknowledgement bookkeeping also survives retirement. -/
theorem retire_preserves_validity (s : State) (ids : List Nat) (valid : Valid s) :
    Valid (retire s ids) := by
  intro row member ack
  have original : row ∈ s.journal := (List.mem_filter.mp member).1
  exact valid row original ack

/-- Iterate only admitted retirements. This is not the entire journal lifecycle. -/
inductive RetirementReachable (initial : State) : State → Prop where
  | initial : RetirementReachable initial initial
  | step {s : State} (reachable : RetirementReachable initial s)
      (ids : List Nat) (admitted : Admitted s ids) :
      RetirementReachable initial (retire s ids)

/-- Arbitrarily many admitted retirements preserve the property. -/
theorem retirement_sequence_preserves {initial final : State}
    (valid : Valid initial) (preserved : Preserved initial)
    (reachable : RetirementReachable initial final) : Valid final ∧ Preserved final := by
  induction reachable with
  | initial => exact ⟨valid, preserved⟩
  | step previous ids admitted ih =>
    exact ⟨retire_preserves_validity _ _ ih.1,
      retire_preserves_outstanding _ _ ih.1 ih.2 admitted⟩

/-- A genuine older outstanding payload alongside a newer working document. -/
def witness : State :=
  { journal := [{ requestId := 1, payload := 10, acknowledged := false },
                { requestId := 2, payload := 20, acknowledged := false }]
    view := some 20, accepted := [10, 20], discharged := [] }

theorem witness_valid : Valid witness := by
  intro row member ack
  simp [witness] at member
  rcases member with rfl | rfl <;> contradiction

theorem witness_preserved : Preserved witness := by
  intro edit accepted outstanding
  simp [witness] at accepted
  rcases accepted with rfl | rfl
  · exact Or.inr ⟨{ requestId := 1, payload := 10, acknowledged := false }, by simp [witness], rfl⟩
  · exact Or.inl rfl

/-- Removing the admission premise permits concrete loss; the safety statement is not vacuous. -/
theorem unsafe_retirement_loses_payload : ¬ Preserved (retire witness [1]) := by
  intro preserved
  have recovery := preserved 10 (by simp [retire, witness]) (by simp [retire, witness])
  simp [retire, witness] at recovery

/-- Nonempty admissible retirement, with newer outstanding work. -/
def settledWitness : State :=
  { journal := [{ requestId := 1, payload := 10, acknowledged := true },
                { requestId := 2, payload := 20, acknowledged := false }]
    view := some 20, accepted := [10, 20], discharged := [10] }

theorem nonempty_retirement_admitted : Admitted settledWitness [1] := by
  intro row member selected
  simp [settledWitness] at member
  rcases member with rfl | rfl
  · rfl
  · simp at selected

theorem safe_retirement_keeps_pending :
    (retire settledWitness [1]).journal =
      [{ requestId := 2, payload := 20, acknowledged := false }] ∧
    Preserved (retire settledWitness [1]) := by
  constructor
  · rfl
  · intro edit accepted outstanding
    simp [retire, settledWitness] at accepted
    rcases accepted with rfl | rfl
    · exact False.elim (outstanding (by simp [retire, settledWitness]))
    · exact Or.inl rfl

#print axioms nonempty_retirement_admitted
#print axioms safe_retirement_keeps_pending

#print axioms retire_preserves_outstanding
#print axioms retire_preserves_validity
#print axioms retirement_sequence_preserves
#print axioms witness_valid
#print axioms witness_preserved
#print axioms unsafe_retirement_loses_payload

end SuperbeeVerification
