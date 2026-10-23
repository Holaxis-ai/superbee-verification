From Stdlib Require Import List.
From Retirement Require Import Kernel.
Import ListNotations.

(* Independent domain premises, not an equation about admissionb. The supplied
   actual snapshot's truth/completeness relative to storage is a caller premise. *)
Definition MetaObserved (rows : list (nat * meta_value)) (key : nat)
    (observed : option meta_value) : Prop :=
  match observed with
  | None => ~ In key (map fst rows)
  | Some value => In (key,value) rows
  end.
Definition Allowed (i : retirement_input) : Prop :=
  actual_document i = expected_document i /\
  Forall (fun row => record_target row = target i) (actual_records i) /\
  NoDup (map record_id (actual_records i)) /\
  NoDup (map record_sequence (actual_records i)) /\
  NoDup (map record_id (expected_records i)) /\
  NoDup (map record_sequence (expected_records i)) /\
  incl (actual_records i) (expected_records i) /\
  incl (expected_records i) (actual_records i) /\
  NoDup (map fst (actual_metadata i)) /\
  NoDup (map fst (expected_metadata i)) /\
  Forall (fun premise => MetaObserved (actual_metadata i) (fst premise) (snd premise))
    (expected_metadata i) /\
  selected_ids i <> [] /\ NoDup (selected_ids i) /\
  (forall id, In id (selected_ids i) -> exists row,
    In row (actual_records i) /\ record_id row = id /\ record_status row = Acknowledged) /\
  NoDup (metadata_removals i) /\
  incl (metadata_removals i) (map fst (expected_metadata i)).

Definition ExactOutput (i : retirement_input) (o : retirement_output) : Prop :=
  remaining_records o = filter (keep_record i) (actual_records i) /\
  remaining_metadata o = filter (keep_metadata i) (actual_metadata i) /\
  unchanged_document o = actual_document i /\
  removed_ids o = selected_ids i /\ removed_metadata o = metadata_removals i.

Definition witness_input : retirement_input :=
  let ack1 := JournalRecord 1 10 1 Acknowledged [11;12] [91] in
  let ack2 := JournalRecord 2 10 2 Acknowledged [21;22] [92] in
  let outstanding := JournalRecord 3 10 3 Unknown [31;32] [93] in
  RetirementInput 10 (Some (Document [9] [10;11])) (Some (Document [9] [10;11]))
    [ack1;ack2;outstanding] [outstanding;ack2;ack1]
    [(4,None);(5,Some [7])] [(4,Some None);(8,None)] [1] [4;8].
Definition witness_output : retirement_output :=
  RetirementOutput
    [JournalRecord 2 10 2 Acknowledged [21;22] [92];
     JournalRecord 3 10 3 Unknown [31;32] [93]]
    [(5,Some [7])] (Some (Document [9] [10;11])) [1] [4;8].

Definition CorrectFor (f : retirement_input -> option retirement_output) : Prop := (forall i,
  (forall o, f i = Some o <-> Allowed i /\ ExactOutput i o) /\
  (f i = None <-> ~ Allowed i) /\
  (forall o row, f i = Some o ->
    (In row (remaining_records o) <->
      In row (actual_records i) /\ ~ In (record_id row) (selected_ids i))) /\
  (forall o row, f i = Some o -> In row (actual_records i) ->
    record_status row <> Acknowledged -> In row (remaining_records o)) /\
  (forall o key value, f i = Some o ->
    (In (key,value) (remaining_metadata o) <->
      In (key,value) (actual_metadata i) /\ ~ In key (metadata_removals i)))) /\
  f witness_input = Some witness_output.

Definition retirement_correct : Prop := CorrectFor decision.
Definition refuse_all : retirement_input -> option retirement_output := fun _ => None.
Definition drop_all_records (i : retirement_input) : option retirement_output :=
  match decision i with
  | None => None
  | Some o => Some (RetirementOutput [] (remaining_metadata o)
      (unchanged_document o) (removed_ids o) (removed_metadata o))
  end.
Definition refuse_all_incorrect : Prop := ~ CorrectFor refuse_all.
Definition drop_all_incorrect : Prop := ~ CorrectFor drop_all_records.
