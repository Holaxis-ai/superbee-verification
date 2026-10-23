-------------------------- MODULE RetryProtocol --------------------------
EXTENDS Naturals, FiniteSets, TLC
CONSTANTS Mode, Recovery
Handles == {1, 2}
Attempts == 1..2
VARIABLES row, seen, session, token, owner, ownerSession, wires,
          mayApply, applied, safeClaims, events
vars == <<row, seen, session, token, owner, ownerSession, wires,
          mayApply, applied, safeClaims, events>>
Record(a, p, s, r) == [attempt |-> a, prefix |-> p, state |-> s, receipt |-> r]
Eligible(r) == ~r.receipt /\ r.state \in {"pending", "unknown"}
               /\ r.prefix = r.attempt
Init ==
 /\ row = IF Recovery THEN Record(1,1,"pending",FALSE)
                         ELSE Record(0,0,"pending",FALSE)
 /\ seen = [h \in Handles |-> row]
 /\ session = [h \in Handles |-> IF Recovery THEN 1 ELSE 0]
 /\ token = [h \in Handles |-> 0]
 /\ owner = [a \in Attempts |-> IF Recovery /\ a=1 THEN 1 ELSE 0]
 /\ ownerSession = [a \in Attempts |-> 0]
 /\ wires = [a \in Attempts |-> IF Recovery /\ a=1 THEN 1 ELSE 0]
 /\ mayApply = [a \in Attempts |-> FALSE]
 /\ applied = [a \in Attempts |-> FALSE]
 /\ safeClaims = TRUE
 /\ events = {}
Read(h) ==
 /\ seen' = [seen EXCEPT ![h] = row]
 /\ UNCHANGED <<row,session,token,owner,ownerSession,wires,mayApply,applied,safeClaims,events>>
Claim(h) ==
 LET a == seen[h].attempt+1 IN
 /\ Mode # "deny"
 /\ Eligible(seen[h]) /\ a \in Attempts
 /\ IF Mode="stale" THEN TRUE
    ELSE IF Mode="guard-only" THEN Eligible(row) /\ seen[h].attempt=row.attempt /\ seen[h].prefix=row.prefix /\ seen[h].state=row.state
    ELSE seen[h]=row /\ Eligible(row)
 /\ row' = Record(a,seen[h].prefix,"in_flight",FALSE)
 /\ token' = [token EXCEPT ![h] = a]
 /\ owner' = [owner EXCEPT ![a] = h]
 /\ ownerSession' = [ownerSession EXCEPT ![a] = session[h]]
 /\ mayApply' = [mayApply EXCEPT ![a] = TRUE]
 /\ safeClaims' = (safeClaims /\ owner[a]=0
                  /\ (\A b \in Attempts : b<a => ~mayApply[b]))
 /\ UNCHANGED <<seen,session,wires,applied,events>>
Wire(h) ==
 LET a == token[h] IN
 /\ a \in Attempts /\ owner[a]=h /\ ownerSession[a]=session[h]
 /\ token' = [token EXCEPT ![h] = 0]
 /\ wires[a]<2 /\ wires' = [wires EXCEPT ![a] = @+1]
 /\ UNCHANGED <<row,seen,session,owner,ownerSession,mayApply,applied,safeClaims,events>>
CrashReopen(h) ==
 /\ ~Recovery /\ session[h]=0
 /\ session' = [session EXCEPT ![h] = 1]
 /\ token' = [token EXCEPT ![h] = 0]
 /\ events' = events \cup {IF row.attempt \in Attempts /\ owner[row.attempt]=h /\ wires[row.attempt]>0 THEN IF row.attempt=1 THEN "crashAfterWire1" ELSE "crashAfterWire2" ELSE IF token[h]>0 THEN IF token[h]=1 THEN "crashBeforeWire1" ELSE "crashBeforeWire2" ELSE IF row.attempt=1 /\ row.prefix=1 /\ row.state="pending" THEN "durableEvidenceReopen" ELSE "otherCrash"}
 /\ UNCHANGED <<row,seen,owner,ownerSession,wires,mayApply,applied,safeClaims>>
Unknown ==
 /\ row.state="in_flight"
 /\ row' = [row EXCEPT !.state="unknown"]
 /\ UNCHANGED <<seen,session,token,owner,ownerSession,wires,mayApply,applied,safeClaims,events>>
AbsentLookup ==
 /\ ~row.receipt /\ row.attempt>row.prefix
 /\ IF Mode="absence" THEN row'=Record(row.attempt,row.attempt,"pending",FALSE)
                         ELSE row'=[row EXCEPT !.state="unknown"]
 /\ events' = IF (row.attempt=1 /\ "crashBeforeWire1" \in events) \/ (row.attempt=2 /\ "crashBeforeWire2" \in events) THEN events \cup {"lookupAfterCrash"} ELSE events
 /\ UNCHANGED <<seen,session,token,owner,ownerSession,wires,mayApply,applied,safeClaims>>
NotDispatched(h) ==
 LET a == row.attempt IN
 /\ ~Recovery
 /\ a \in Attempts /\ row.state="in_flight" /\ row.prefix=a-1
 /\ ~row.receipt
 /\ IF Mode="foreign" THEN (owner[a]#h \/ ownerSession[a]#session[h]) /\ wires[a]>0
    ELSE token[h]=a /\ owner[a]=h /\ ownerSession[a]=session[h] /\ wires[a]=0
 /\ row' = Record(a,a,"pending",FALSE)
 /\ token' = [token EXCEPT ![h] = 0]
 \* Only authentic local non-dispatch changes actual possible application.
 /\ mayApply' = IF Mode="foreign" THEN mayApply
                ELSE [mayApply EXCEPT ![a]=FALSE]
 /\ events' = events \cup {"localRollback"}
 /\ UNCHANGED <<seen,session,owner,ownerSession,wires,applied,safeClaims>>
HostEvidence ==
 LET a == row.attempt IN
 /\ a \in Attempts /\ row.prefix=a-1 /\ ~row.receipt /\ wires[a]>0
 /\ ~applied[a] /\ (row.state \in {"unknown","in_flight"})
 /\ ~Recovery \/ a=1
 \* Trusted host guarantee prevents future application, including late delivery.
 /\ row' = Record(a,a,"pending",FALSE)
 /\ mayApply' = [mayApply EXCEPT ![a]=FALSE]
 /\ token' = [h \in Handles |-> IF token[h]=a THEN 0 ELSE token[h]]
 /\ UNCHANGED <<seen,session,owner,ownerSession,wires,applied,safeClaims,events>>
Apply(a) ==
 /\ ~Recovery /\ wires[a]>0 /\ mayApply[a] /\ ~applied[a]
 /\ applied' = [applied EXCEPT ![a]=TRUE]
 /\ events' = IF (a=1 /\ "crashAfterWire1" \in events) \/ (a=2 /\ "crashAfterWire2" \in events) THEN events \cup {"lateApply"} ELSE events
 /\ UNCHANGED <<row,seen,session,token,owner,ownerSession,wires,mayApply,safeClaims>>
Receipt ==
 /\ ~row.receipt /\ row.attempt \in Attempts /\ applied[row.attempt]
 /\ row' = [row EXCEPT !.receipt=TRUE, !.state="terminal"]
 /\ UNCHANGED <<seen,session,token,owner,ownerSession,wires,mayApply,applied,safeClaims,events>>
Claims == \E h \in Handles : Claim(h)
Wires == \E h \in Handles : Wire(h)
Next == Claims \/ Wires \/ Unknown \/ AbsentLookup \/ HostEvidence \/ Receipt
        \/ (\E h \in Handles : Read(h) \/ CrashReopen(h) \/ NotDispatched(h))
        \/ (\E a \in Attempts : Apply(a))
Spec == Init /\ [][Next]_vars
RecoverySpec == Spec /\ WF_vars(Claims) /\ WF_vars(Wires)
                /\ \A h \in Handles : WF_vars(Read(h))
TypeOK == /\ row.attempt \in 0..2 /\ row.prefix \in 0..row.attempt
          /\ row.state \in {"pending","in_flight","unknown","terminal"}
          /\ row.receipt \in BOOLEAN /\ safeClaims \in BOOLEAN
          /\ \A a \in Attempts : wires[a] \in 0..2 /\ mayApply[a] \in BOOLEAN
                                 /\ applied[a] \in BOOLEAN
NoUnsafeClaim == safeClaims
PrefixSound == \A a \in Attempts : a<=row.prefix => ~mayApply[a] /\ ~applied[a]
AtMostOneWire == \A a \in Attempts : wires[a]<=1
NoOverlappingApplications == ~ (applied[1] /\ applied[2])
NoInitialWire == wires[1]=0
NoRollbackRetry == ~("localRollback" \in events /\ "durableEvidenceReopen" \in events /\ wires[2]=1)
NoCrashLateApply == ~("lateApply" \in events)
NoCrashLookup == ~("lookupAfterCrash" \in events)
RecoveredRetry == <> (wires[2]=1)
=============================================================================
