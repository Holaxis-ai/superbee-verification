From Stdlib Require Import List Bool Arith.PeanoNat Lia.
From Retirement Require Import Kernel Specification.
Import ListNotations.

Lemma equalb_spec {A} eq_dec (x y : A) : equalb eq_dec x y = true <-> x = y.
Proof. unfold equalb. destruct (eq_dec x y); intuition discriminate. Qed.
Lemma memberb_spec {A} eq_dec (x : A) xs : memberb eq_dec x xs = true <-> In x xs.
Proof.
  unfold memberb. rewrite existsb_exists. split.
  - intros [y [Hy He]]. apply equalb_spec in He. now subst.
  - intros H. exists x. split; [exact H|apply equalb_spec; reflexivity].
Qed.
Lemma memberb_false {A} eq_dec (x : A) xs : memberb eq_dec x xs = false <-> ~ In x xs.
Proof.
  pose proof (memberb_spec eq_dec x xs) as H.
  destruct (memberb eq_dec x xs); intuition discriminate.
Qed.
Lemma unique_spec xs : uniqueb xs = true <-> NoDup xs.
Proof.
  induction xs as [|x xs IH]; simpl.
  - split; constructor.
  - rewrite andb_true_iff, negb_true_iff, memberb_false, IH.
    split; [intros [H1 H2]; constructor|intros H; inversion H]; auto.
Qed.
Lemma all_spec {A} f P (H : forall x : A, f x = true <-> P x) xs :
  forallb f xs = true <-> Forall P xs.
Proof.
  rewrite forallb_forall, Forall_forall. split; intros Hx x Hin.
  - apply H, Hx, Hin.
  - apply H, Hx, Hin.
Qed.
Lemma contained_spec xs ys : records_containedb xs ys = true <-> incl xs ys.
Proof.
  unfold records_containedb, incl. rewrite forallb_forall.
  split; intros H row Hin.
  - exact (proj1 (memberb_spec record_eq_dec row ys) (H row Hin)).
  - exact (proj2 (memberb_spec record_eq_dec row ys) (H row Hin)).
Qed.
Lemma selected_spec i : selected_acknowledgedb i = true <->
  (forall id, In id (selected_ids i) -> exists row,
    In row (actual_records i) /\ record_id row = id /\ record_status row = Acknowledged).
Proof.
  unfold selected_acknowledgedb. rewrite forallb_forall.
  split; intros H id Hin; specialize (H id Hin).
  - apply existsb_exists in H. destruct H as [row [Hr H]].
    apply andb_true_iff in H. destruct H as [Hi Hs].
    apply equalb_spec in Hi. unfold row_acknowledgedb in Hs. apply equalb_spec in Hs.
    exists row. auto.
  - destruct H as [row [Hr [Hi Hs]]]. apply existsb_exists.
    exists row. split; [exact Hr|]. apply andb_true_iff. split.
    + apply equalb_spec. symmetry. exact Hi.
    + unfold row_acknowledgedb. apply equalb_spec. exact Hs.
Qed.
Lemma nonempty_spec {A} (xs : list A) : negb (Nat.eqb (length xs) 0) = true <-> xs <> [].
Proof. destruct xs; simpl; intuition discriminate. Qed.
Lemma lookup_none rows key : lookup_meta key rows = None <-> ~ In key (map fst rows).
Proof.
  induction rows as [|[k v] tail IH]; simpl.
  - tauto.
  - destruct (Nat.eq_dec key k) as [<-|Hne].
    + split; [discriminate|intros H; exfalso; apply H; now left].
    + rewrite IH. simpl. intuition congruence.
Qed.
Lemma lookup_some rows key value : NoDup (map fst rows) ->
  (lookup_meta key rows = Some value <-> In (key,value) rows).
Proof.
  induction rows as [|[k v] tail IH]; simpl; intros Hnd.
  - split; [discriminate|contradiction].
  - inversion Hnd as [|h t Hnot Htail]; subst.
    destruct (Nat.eq_dec key k) as [<-|Hne].
    + split.
      * intros H; inversion H; now left.
      * intros [H|H]; [inversion H; reflexivity|].
        exfalso. apply Hnot. apply in_map with (f := fst) in H. exact H.
    + rewrite (IH Htail). split; [now right|].
      intros [H|H]; [congruence|exact H].
Qed.
Lemma lookup_spec rows key observed : NoDup (map fst rows) ->
  (lookup_meta key rows = observed <-> MetaObserved rows key observed).
Proof.
  intros H. destruct observed as [value|]; simpl [MetaObserved].
  - apply lookup_some, H.
  - apply lookup_none.
Qed.
Lemma metadata_guard_spec i : NoDup (map fst (actual_metadata i)) ->
  (Forall (fun premise => lookup_meta (fst premise) (actual_metadata i) = snd premise)
      (expected_metadata i) <->
   Forall (fun premise => MetaObserved (actual_metadata i) (fst premise) (snd premise))
      (expected_metadata i)).
Proof.
  intros H. rewrite !Forall_forall. split; intros Hf premise Hin.
  - exact (proj1 (lookup_spec _ _ _ H) (Hf premise Hin)).
  - exact (proj2 (lookup_spec _ _ _ H) (Hf premise Hin)).
Qed.
Lemma admission_spec i : admissionb i = true <-> Allowed i.
Proof.
  unfold admissionb.
  rewrite !andb_true_iff, equalb_spec, !unique_spec, !contained_spec, selected_spec, nonempty_spec.
  rewrite (all_spec _ _ (fun row => equalb_spec Nat.eq_dec (record_target row) (target i))).
  rewrite (all_spec _ _ (fun premise => equalb_spec meta_observation_eq_dec
    (lookup_meta (fst premise) (actual_metadata i)) (snd premise))).
  rewrite forallb_forall. setoid_rewrite memberb_spec. unfold incl.
  split; intros H.
  - assert (Hu : NoDup (map fst (actual_metadata i))) by tauto.
    pose proof (metadata_guard_spec i Hu) as Hm. unfold Allowed, incl. tauto.
  - assert (Hu : NoDup (map fst (actual_metadata i))) by (unfold Allowed in H; tauto).
    pose proof (metadata_guard_spec i Hu) as Hm. unfold Allowed, incl in H. tauto.
Qed.
Lemma exact_output_unique i o : ExactOutput i o ->
  o = RetirementOutput (filter (keep_record i) (actual_records i))
    (filter (keep_metadata i) (actual_metadata i))
    (actual_document i) (selected_ids i) (metadata_removals i).
Proof. destruct o; unfold ExactOutput; simpl. intros [H1 [H2 [H3 [H4 H5]]]]. now subst. Qed.
Lemma decision_spec i o : decision i = Some o <-> Allowed i /\ ExactOutput i o.
Proof.
  unfold decision. destruct (admissionb i) eqn:H.
  - apply admission_spec in H. split.
    + intros E. inversion E; subst. split; [exact H|]. unfold ExactOutput; simpl; auto.
    + intros [_ Ho]. apply exact_output_unique in Ho. now subst.
  - split; [discriminate|]. intros [Ha _]. apply admission_spec in Ha. congruence.
Qed.
Lemma refusal_spec i : decision i = None <-> ~ Allowed i.
Proof.
  unfold decision. destruct (admissionb i) eqn:H.
  - apply admission_spec in H. split; [discriminate|tauto].
  - split; [intros _ Ha; apply admission_spec in Ha; congruence|auto].
Qed.
Lemma remaining_spec i o row : decision i = Some o ->
  (In row (remaining_records o) <-> In row (actual_records i) /\ ~ In (record_id row) (selected_ids i)).
Proof.
  intros H. apply decision_spec in H. destruct H as [_ [H _]]. rewrite H, filter_In.
  unfold keep_record. rewrite negb_true_iff, memberb_false. tauto.
Qed.
Lemma unique_id rows x y : NoDup (map record_id rows) ->
  In x rows -> In y rows -> record_id x = record_id y -> x = y.
Proof.
  induction rows as [|head tail IH]; simpl; intros Hnd Hx Hy Heq; [contradiction|].
  inversion Hnd as [|h t Hnot Htail]; subst.
  destruct Hx as [<-|Hx]; destruct Hy as [<-|Hy].
  - reflexivity.
  - exfalso. apply Hnot. rewrite Heq. apply in_map. exact Hy.
  - exfalso. apply Hnot. rewrite <- Heq. apply in_map. exact Hx.
  - apply IH; assumption.
Qed.
Lemma selected_row_unique i row : Allowed i -> In row (actual_records i) ->
  In (record_id row) (selected_ids i) -> record_status row = Acknowledged.
Proof.
  intros H Hin Hselected.
  assert (Hunique : NoDup (map record_id (actual_records i))) by (unfold Allowed in H; tauto).
  assert (Hselecteds : forall id, In id (selected_ids i) -> exists other,
    In other (actual_records i) /\ record_id other = id /\ record_status other = Acknowledged)
    by (unfold Allowed in H; tauto).
  destruct (Hselecteds _ Hselected) as [other [Hother [Hid Hack]]].
  assert (row = other).
  { apply (unique_id (actual_records i) row other Hunique Hin Hother).
    symmetry. exact Hid. }
  now subst.
Qed.
Theorem retirement_correct_holds : retirement_correct.
Proof.
  unfold retirement_correct, CorrectFor. split.
  { intros i. split; [intros o; apply decision_spec|]. split; [apply refusal_spec|].
  split; [intros; apply remaining_spec; assumption|]. split.
  - intros o row Hrun Hin Hnot. apply (proj2 (remaining_spec i o row Hrun)).
    split; [exact Hin|]. intros Hsel. apply Hnot.
    apply (selected_row_unique i row); [exact (proj1 (proj1 (decision_spec i o) Hrun))|exact Hin|exact Hsel].
  - intros o key value Hrun. apply decision_spec in Hrun.
    destruct Hrun as [_ [_ [Hmeta _]]]. rewrite Hmeta, filter_In.
    unfold keep_metadata. simpl. rewrite negb_true_iff, memberb_false. tauto. }
  vm_compute. reflexivity.
Qed.

Theorem refuse_all_fails : refuse_all_incorrect.
Proof. intros [_ H]. discriminate H. Qed.
Theorem drop_all_fails : drop_all_incorrect.
Proof. intros [_ H]. vm_compute in H. discriminate H. Qed.
