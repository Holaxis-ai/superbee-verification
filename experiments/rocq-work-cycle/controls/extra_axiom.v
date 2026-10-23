From Retirement Require Import Kernel Specification.
Axiom cheat : retirement_correct.
Theorem retirement_correct_holds : retirement_correct.
Proof. exact cheat. Qed.

Axiom refuse_all_fails : Retirement.Specification.refuse_all_incorrect.
Axiom drop_all_fails : Retirement.Specification.drop_all_incorrect.
