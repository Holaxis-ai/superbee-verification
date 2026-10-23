From Stdlib Require Import List Bool Arith.PeanoNat.
Import ListNotations.

(* New executable typed component. These natural-number lists are opaque
   typed payloads, not a claimed wire or production JSON representation. *)
Inductive journal_status := Pending | InFlight | Acknowledged | Refused | Conflict | Unknown.
Definition status_eq_dec : forall x y : journal_status, {x = y} + {x <> y}.
Proof. decide equality. Defined.
Definition words := list nat.
Definition words_eq_dec := list_eq_dec Nat.eq_dec.
Record document := Document { doc_version : words; doc_raw : words }.
Definition document_eq_dec : forall x y : document, {x = y} + {x <> y}.
Proof. decide equality; apply words_eq_dec. Defined.
Record journal_record := JournalRecord {
  record_id : nat; record_target : nat; record_sequence : nat;
  record_status : journal_status;
  record_payload : words;
  record_residual : words
}.
Definition record_eq_dec : forall x y : journal_record, {x = y} + {x <> y}.
Proof. decide equality; try apply Nat.eq_dec; try apply status_eq_dec; apply words_eq_dec. Defined.
(* Outer lookup option represents row absence; a present None represents
   undefined, and Some [] is a present empty value. *)
Definition option_dec {A} (eq_dec : forall x y : A, {x = y}+{x <> y})
  : forall x y : option A, {x = y}+{x <> y}.
Proof. decide equality; apply eq_dec. Defined.
Definition meta_value := option words.
Definition meta_value_eq_dec := option_dec words_eq_dec.
Definition meta_observation_eq_dec := option_dec meta_value_eq_dec.
Definition document_option_dec := option_dec document_eq_dec.
Record retirement_input := RetirementInput {
  target : nat;
  actual_document : option document; expected_document : option document;
  actual_records : list journal_record; expected_records : list journal_record;
  actual_metadata : list (nat * meta_value);
  expected_metadata : list (nat * option meta_value);
  selected_ids : list nat; metadata_removals : list nat
}.
Record retirement_output := RetirementOutput {
  remaining_records : list journal_record;
  remaining_metadata : list (nat * meta_value);
  unchanged_document : option document;
  removed_ids : list nat; removed_metadata : list nat
}.
Definition equalb {A} (eq_dec : forall x y : A, {x = y}+{x <> y}) (x y : A) : bool :=
  if eq_dec x y then true else false.
Definition memberb {A} (eq_dec : forall x y : A, {x = y}+{x <> y}) (x : A) (xs : list A) :=
  existsb (equalb eq_dec x) xs.
Fixpoint uniqueb (xs : list nat) : bool :=
  match xs with [] => true | x::rest => negb (memberb Nat.eq_dec x rest) && uniqueb rest end.
Fixpoint lookup_meta (key : nat) (rows : list (nat * meta_value)) : option meta_value :=
  match rows with
  | [] => None
  | (k,v)::rest => if Nat.eq_dec key k then Some v else lookup_meta key rest
  end.
Definition records_containedb (xs ys : list journal_record) :=
  forallb (fun row => memberb record_eq_dec row ys) xs.
Definition row_acknowledgedb (row : journal_record) :=
  equalb status_eq_dec (record_status row) Acknowledged.
Definition selected_acknowledgedb (i : retirement_input) :=
  forallb (fun id => existsb (fun row =>
    equalb Nat.eq_dec id (record_id row) && row_acknowledgedb row) (actual_records i)) (selected_ids i).
Definition admissionb (i : retirement_input) : bool :=
  equalb document_option_dec (actual_document i) (expected_document i) &&
  forallb (fun row => equalb Nat.eq_dec (record_target row) (target i)) (actual_records i) &&
  uniqueb (map record_id (actual_records i)) &&
  uniqueb (map record_sequence (actual_records i)) &&
  uniqueb (map record_id (expected_records i)) &&
  uniqueb (map record_sequence (expected_records i)) &&
  records_containedb (actual_records i) (expected_records i) &&
  records_containedb (expected_records i) (actual_records i) &&
  uniqueb (map fst (actual_metadata i)) &&
  uniqueb (map fst (expected_metadata i)) &&
  forallb (fun premise => equalb meta_observation_eq_dec
    (lookup_meta (fst premise) (actual_metadata i)) (snd premise)) (expected_metadata i) &&
  negb (Nat.eqb (length (selected_ids i)) 0) &&
  uniqueb (selected_ids i) && selected_acknowledgedb i &&
  uniqueb (metadata_removals i) &&
  forallb (fun key => memberb Nat.eq_dec key (map fst (expected_metadata i))) (metadata_removals i).
Definition keep_record (i : retirement_input) (row : journal_record) :=
  negb (memberb Nat.eq_dec (record_id row) (selected_ids i)).
Definition keep_metadata (i : retirement_input) (row : nat * meta_value) :=
  negb (memberb Nat.eq_dec (fst row) (metadata_removals i)).
Definition decision (i : retirement_input) : option retirement_output :=
  if admissionb i then
    Some (RetirementOutput (filter (keep_record i) (actual_records i))
      (filter (keep_metadata i) (actual_metadata i))
      (actual_document i) (selected_ids i) (metadata_removals i))
  else None.
