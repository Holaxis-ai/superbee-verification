import Bridge.Semantics

namespace SourceBridge

set_option maxRecDepth 10000
set_option maxHeartbeats 1000000

/- Independent decoder for the explicitly bounded ASCII source fragment. This is not
    an ECMAScript parser or a proof that the fragment semantics implements ECMAScript. -/
namespace SourceDecode

inductive Token where
  | word (value : Text)
  | quoted (value : Text)
  | punct (value : Nat)
  deriving DecidableEq, Repr

def space (c : Nat) : Bool := c == 32 || c == 9 || c == 10 || c == 13

def letter (c : Nat) : Bool := (65 ≤ c && c ≤ 90) || (97 ≤ c && c ≤ 122) || c == 95

def wordChar (c : Nat) : Bool := letter c || (48 ≤ c && c ≤ 57)

/-- No escapes, control characters, or non-ASCII literal contents are admitted. -/
def quoted : Nat → Text → Option (Text × Text)
  | 0, _ => none
  | _ + 1, [] => none
  | n + 1, c :: cs =>
    if c == 34 then some ([], cs)
    else if c < 32 || 126 < c || c == 92 then none
    else do
      let (value, rest) ← quoted n cs
      return (c :: value, rest)

def lex : Nat → Text → Option (List Token)
  | 0, _ => none
  | _ + 1, [] => some []
  | n + 1, c :: cs => do
    if space c then lex n cs
    else if c == 34 then
      let (value, rest) ← quoted (cs.length + 1) cs
      return .quoted value :: (← lex n rest)
    else if letter c then
      let suffix := cs.takeWhile wordChar
      let rest := cs.dropWhile wordChar
      -- JavaScript automatic semicolon insertion forbids a line terminator between
      -- return and its expression, even though ordinary whitespace is otherwise ignored.
      if c :: suffix == ascii "return" && (rest.takeWhile space).any (fun b => b == 10 || b == 13) then
        none
      else return .word (c :: suffix) :: (← lex n rest)
    else if c == 38 then
      match cs with
      | 38 :: rest => return .punct 256 :: (← lex n rest)
      | _ => none
    else if c == 124 then
      match cs with
      | 124 :: rest => return .punct 257 :: (← lex n rest)
      | _ => return .punct c :: (← lex n cs)
    else if c == 61 then
      match cs with
      | 61 :: 61 :: rest => return .punct 258 :: (← lex n rest)
      | _ => return .punct c :: (← lex n cs)
    else if [40, 41, 91, 93, 123, 125, 58, 59, 44, 46, 60, 62, 61, 38, 124].contains c then
      return .punct c :: (← lex n cs)
    else none

def tokenize (bytes : Text) : Option (List Token) := lex (bytes.length + 1) bytes

/-- Only internal, fixed ASCII grammar strings use this convenience definition. -/
def grammar (text : String) : List Token := (tokenize (ascii text)).getD []

def consume : List Token → List Token → Option (List Token)
  | [], rest => some rest
  | _ :: _, [] => none
  | x :: xs, y :: ys => if x == y then consume xs ys else none

def field (tokens : List Token) : Option (Field × List Token) := do
  let rest ← consume (grammar "outcome.") tokens
  match rest with
  | .word name :: tail =>
    if name == ascii "kind" then some (.kind, tail)
    else if name == ascii "code" then some (.code, tail)
    else none
  | _ => none

def atom (tokens : List Token) : Option (Expr × List Token) :=
  match tokens with
  | .word name :: rest =>
    if name == ascii "true" then some (.literal true, rest)
    else if name == ascii "false" then some (.literal false, rest)
    else if name == ascii "AUTHORIZATION_REFUSAL_CODES" then do
      let tail ← consume (grammar ".has(") rest
      let (selected, tail) ← field tail
      let tail ← consume (grammar ")") tail
      return (.has selected, tail)
    else do
      let (selected, tail) ← field tokens
      let tail ← consume (grammar "===") tail
      match tail with
      | .quoted value :: tail => some (.eq selected value, tail)
      | _ => none
  | _ => none

/- Pratt parsing: && binds more tightly than ||, both associate left. Fuel exhaustion
    always rejects. Parentheses recurse through the same parser. -/
mutual
  def expression : Nat → Nat → List Token → Option (Expr × List Token)
    | 0, _, _ => none
    | n + 1, minimum, tokens => do
      let (left, rest) ← match tokens with
        | .punct 40 :: rest => do
          let (inner, tail) ← expression n 0 rest
          let tail ← consume (grammar ")") tail
          pure (inner, tail)
        | _ => atom tokens
      continuation n minimum left rest
  def continuation : Nat → Nat → Expr → List Token → Option (Expr × List Token)
    | 0, _, _, _ => none
    | n + 1, minimum, left, tokens =>
      let operator : Option (Bool × Nat × List Token) := match tokens with
        | .punct 256 :: tail => some (true, 2, tail)
        | .punct 257 :: tail => some (false, 1, tail)
        | _ => none
      match operator with
      | none => some (left, tokens)
      | some (isAnd, precedence, tail) =>
        if precedence < minimum then some (left, tokens)
        else do
          let (right, rest) ← expression n (precedence + 1) tail
          continuation n minimum (if isAnd then .and left right else .or left right) rest
end

def codes : Nat → Nat → List Token → Option (List Text × List Token)
  | 0, _, _ => none
  | _ + 1, 0, tokens => do
    let rest ← consume (grammar "]);") tokens
    return ([], rest)
  | n + 1, count + 1, tokens => do
    match tokens with
    | .quoted value :: tail =>
      let tail ← consume (grammar ",") tail
      let (remaining, rest) ← codes n count tail
      return (value :: remaining, rest)
    | _ => none

end SourceDecode

/-- Decode exactly two complete declarations, including the fixed type signatures.
    Six ASCII strings and the restricted Boolean body are reconstructed from bytes.
    A trailing comma on all six set entries is required, matching the pinned source. -/
def decode (bytes : List Nat) : Option (Expr × List Text) := do
  let tokens ← SourceDecode.tokenize bytes
  let rest ← SourceDecode.consume (SourceDecode.grammar
    "export const AUTHORIZATION_REFUSAL_CODES: ReadonlySet<string> = new Set([") tokens
  let (values, rest) ← SourceDecode.codes 8 6 rest
  let rest ← SourceDecode.consume (SourceDecode.grammar
    "export function isAuthorizationRefusal(outcome: Outcome | RecordedWriteOutcome): boolean { return") rest
  let (program, rest) ← SourceDecode.expression (rest.length * 4 + 8) 0 rest
  let rest ← SourceDecode.consume (SourceDecode.grammar "; }") rest
  if rest.isEmpty then some (program, values) else none

namespace SourceDecode

private def sample (body : String) : Text := ascii (
  "export const AUTHORIZATION_REFUSAL_CODES: ReadonlySet<string> = new Set([" ++
  "\"A\",\"B\",\"C\",\"D\",\"E\",\"F\",]);" ++
  "export function isAuthorizationRefusal(outcome: Outcome | RecordedWriteOutcome): boolean { return " ++
  body ++ "; }")

-- Precedence is observable in reconstructed syntax, independently of evaluation.
example : (expression 32 0 (grammar "true || false && true")).map Prod.fst =
    some (.or (.literal true) (.and (.literal false) (.literal true))) := by decide +kernel

example : (expression 32 0 (grammar "(true || false) && true")).map Prod.fst =
    some (.and (.or (.literal true) (.literal false)) (.literal true)) := by decide +kernel

-- A complete declaration fragment with appended tokens must fail.
example : decode (sample "true" ++ ascii "true") = none := by decide +kernel
example : tokenize (ascii "outcome?.kind") = none := by decide +kernel
example : tokenize (ascii "\"refu\\sed\"") = none := by decide +kernel
example : atom (grammar "console.log(true)") = none := by decide +kernel
example : tokenize (ascii "true & & false") = none := by decide +kernel
example : (expression 32 0 (grammar "true | | false")).map Prod.snd =
    some (grammar "| | false") := by decide +kernel
example : atom (grammar "outcome.kind = = = \"refused\"") = none := by decide +kernel

end SourceDecode
end SourceBridge
