import Base
import ./Model.bend as M

# Exact normalization for the two concrete joint states.
law correlated_total:
  {M.total(M.correlated()) == 2n : Nat}

law anticorrelated_total:
  {M.total(M.anticorrelated()) == 2n : Nat}

# Same R state, different accessible joint correlations.
law same_r_view:
  {M.reduce_r(M.correlated()) == M.reduce_r(M.anticorrelated()) : M.RView}

law joint_readout_differs:
  {Nat.is_eq(M.joint00(M.correlated()), M.joint00(M.anticorrelated())) == False{} : Bool}

law left_flip_changes_joint:
  {M.left_flip(M.correlated()) == M.anticorrelated() : M.Joint}

# Every finite adaptive R-only policy has the same complete weighted transcript
# tree when the initial R marginals agree. The two L states may differ.
law adaptive_r_equivalence:
  for +p: M.Procedure
  for -a: M.Joint
  for -b: M.Joint
  for +base_denom: Nat
  for eq: {M.reduce_r(a) == M.reduce_r(b) : M.RView}
  {M.run_from_joint(p, a, base_denom) ==
   M.run_from_joint(p, b, base_denom) : M.TranscriptTree}

# A sequence of arbitrary length of the declared L-local flip cannot affect
# any adaptive R-only transcript at zero coupling.
law left_flips_preserve_r:
  for n: Nat
  for +j: M.Joint
  {M.reduce_r(M.left_flips(n, j)) == M.reduce_r(j) : M.RView}

law left_flips_preserve_transcripts:
  for +p: M.Procedure
  for +n: Nat
  for +j: M.Joint
  for +base_denom: Nat
  {M.run_from_joint(p, M.left_flips(n, j), base_denom) ==
   M.run_from_joint(p, j, base_denom) : M.TranscriptTree}

law concrete_adaptive_example:
  {M.run_from_joint(M.adaptive_example(), M.correlated(), 2n) ==
   M.run_from_joint(M.adaptive_example(), M.anticorrelated(), 2n) : M.TranscriptTree}

law concrete_instruments_valid:
  {M.valid_procedure(M.adaptive_example()) == True{} : Bool}

law concrete_transcript_weights:
  {M.run_from_joint(M.adaptive_example(), M.correlated(), 2n) ==
   M.Fork{M.Fork{M.End{0n, 2n}, M.End{1n, 2n}},
          M.Fork{M.End{0n, 2n}, M.End{1n, 2n}}} : M.TranscriptTree}
