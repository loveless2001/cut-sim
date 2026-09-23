import Base
import ./LAWS.bend as Laws
import ./Model.bend as M

def add_zero_right(n: Nat) -> {Nat.add(n, 0n) == n : Nat}:
  match n:
    case 0n:
      {==}
    case 1n+p:
      %add_zero_right(p) : {1n+Nat.add(p, 0n) == 1n+_ : Nat}
      {==}

def add_succ_right(n: Nat, m: Nat) ->
  {Nat.add(n, 1n+m) == 1n+Nat.add(n, m) : Nat}:
  match n:
    case 0n:
      {==}
    case 1n+p:
      %add_succ_right(p, m) :
        {1n+Nat.add(p, 1n+m) == 1n+_ : Nat}
      {==}

def add_comm(a: Nat, +b: Nat) -> {Nat.add(a, b) == Nat.add(b, a) : Nat}:
  match a:
    case 0n:
      Equal.sym(Nat, Nat.add(b, 0n), b, add_zero_right(b))
    case 1n+ +p:
      %Equal.sym(Nat, Nat.add(b, 1n+p), 1n+Nat.add(b, p),
        add_succ_right(b, p)) : {1n+Nat.add(p, b) == _ : Nat}
      %add_comm(p, b) : {1n+Nat.add(p, b) == 1n+_ : Nat}
      {==}

def left_flip_preserve_r(j: M.Joint) ->
  {M.reduce_r(M.left_flip(j)) == M.reduce_r(j) : M.RView}:
  match j:
    case M.Joint{+r0l0, +r1l0, +r0l1, +r1l1}:
      %add_comm(r0l1, r0l0) :
        {M.RView{Nat.add(r0l1, r0l0), Nat.add(r1l1, r1l0)} ==
         M.RView{_, Nat.add(r1l0, r1l1)} : M.RView}
      %add_comm(r1l1, r1l0) :
        {M.RView{Nat.add(r0l1, r0l0), Nat.add(r1l1, r1l0)} ==
         M.RView{Nat.add(r0l1, r0l0), _} : M.RView}
      {==}

def Laws.correlated_total():
  {==}

def Laws.anticorrelated_total():
  {==}

def Laws.same_r_view():
  {==}

def Laws.joint_readout_differs():
  {==}

def Laws.left_flip_changes_joint():
  {==}

def Laws.adaptive_r_equivalence(p, a, b, base_denom, eq):
  %eq : {M.run_r(p, M.reduce_r(a), base_denom) ==
         M.run_r(p, _, base_denom) : M.TranscriptTree}
  {==}

def Laws.left_flips_preserve_r(n, j):
  match n:
    case 0n:
      {==}
    case 1n+p:
      Equal.trans(M.RView,
        M.reduce_r(M.left_flips(p, M.left_flip(j))),
        M.reduce_r(M.left_flip(j)), M.reduce_r(j),
        Laws.left_flips_preserve_r(p, M.left_flip(j)),
        left_flip_preserve_r(j))

def Laws.left_flips_preserve_transcripts(p, n, j, base_denom):
  Laws.adaptive_r_equivalence(p, M.left_flips(n, j), j, base_denom,
    Laws.left_flips_preserve_r(n, j))

def Laws.concrete_adaptive_example():
  Laws.adaptive_r_equivalence(M.adaptive_example(), M.correlated(),
    M.anticorrelated(), 2n, Laws.same_r_view())

def Laws.concrete_instruments_valid():
  {==}

def Laws.concrete_transcript_weights():
  {==}
