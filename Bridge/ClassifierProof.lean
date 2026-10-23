import SourceGenerated

namespace SourceBridge

theorem refused_tag_encoding : refusedTag = [114, 101, 102, 117, 115, 101, 100] := by decide

/-- Policy is specified independently of the extracted binding. A wrong-code source mutation
    must fail this equality, rather than silently changing the property being proved. -/
theorem source_codes_match_policy : SourceGenerated.codes = policyCodes := by decide

/-- For arbitrary set contents, a true result requires an actual refused outcome kind. -/
theorem source_true_requires_refusal (codes : List Text) (input : Input) :
    eval SourceGenerated.program codes input = true → input.kind = refusedTag := by
  intro result
  by_cases kind : input.kind = refusedTag
  · exact kind
  · simp [SourceGenerated.program, eval, read] at result
    exact False.elim (kind (refused_tag_encoding.symm ▸ result.1))

/-- Exact soundness and completeness for the independent six-code policy, including missing code. -/
theorem source_classifier_exact (input : Input) :
    eval SourceGenerated.program SourceGenerated.codes input = true ↔ Policy input := by
  rw [source_codes_match_policy]
  cases code : input.code with
  | none => simp [SourceGenerated.program, eval, read, Policy, code]
  | some value => simp [SourceGenerated.program, eval, read, Policy, code, refused_tag_encoding]

#print axioms refused_tag_encoding
#print axioms source_codes_match_policy
#print axioms source_true_requires_refusal
#print axioms source_classifier_exact

end SourceBridge
