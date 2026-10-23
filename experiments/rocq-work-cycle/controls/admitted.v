From Retirement Require Import Kernel Specification.
Theorem retirement_correct_holds : retirement_correct.
Admitted.

Theorem refuse_all_fails : Retirement.Specification.refuse_all_incorrect.
Admitted.
Theorem drop_all_fails : Retirement.Specification.drop_all_incorrect.
Admitted.
