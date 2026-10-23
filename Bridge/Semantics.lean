namespace SourceBridge

/-- JavaScript strings represented as UTF-16 code units. The theorem also quantifies
    over larger Nat lists; every real UTF-16 string, including lone surrogates, is included. -/
abbrev Text := List Nat
inductive Field where
  | kind | code
  deriving DecidableEq, Repr
structure Input where
  kind : Text
  code : Option Text
  deriving Repr

/-- Only boolean-valued, side-effect-free expressions are admitted by the source extractor. -/
inductive Expr where
  | eq (field : Field) (literal : Text)
  | has (field : Field)
  | and (left right : Expr)
  | or (left right : Expr)
  | literal (value : Bool)
  deriving Repr

def read (input : Input) : Field → Option Text
  | .kind => some input.kind
  | .code => input.code

/-- Restricted semantics: plain data properties, native string equality and native Set.has
    on string-only contents. The ifs preserve short-circuit order. No ECMAScript-wide claim. -/
def eval : Expr → List Text → Input → Bool
  | .eq field literal, _, input => decide (read input field = some literal)
  | .has field, codes, input => (read input field).any (fun code => codes.contains code)
  | .and left right, codes, input => if eval left codes input then eval right codes input else false
  | .or left right, codes, input => if eval left codes input then true else eval right codes input
  | .literal value, _, _ => value

/-- Used only for independently specified ASCII policy literals, never arbitrary JS strings. -/
def ascii (text : String) : Text := text.toList.map Char.toNat

def refusedTag : Text := ascii "refused"
def policyCodes : List Text := [ascii "AUTH_REQUIRED", ascii "FORBIDDEN", ascii "UNAUTHORIZED",
  ascii "PERMISSION_DENIED", ascii "REQUEST_CAPACITY_PRINCIPAL", ascii "REQUEST_CAPACITY_BUNDLE"]

def Policy (input : Input) : Prop := input.kind = refusedTag ∧
  ∃ code, input.code = some code ∧ code ∈ policyCodes

end SourceBridge
