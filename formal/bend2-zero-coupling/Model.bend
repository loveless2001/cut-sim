import Base

# Exact counts for the four joint outcomes (R bit, L bit).
# A total of 2 represents probabilities with denominator 2.
type Joint is Data:
  Joint{r0l0: Nat, r1l0: Nat, r0l1: Nat, r1l1: Nat}

type RView is Data:
  RView{w0: Nat, w1: Nat}

def reduce_r(j: Joint) -> RView:
  match j:
    case Joint{r0l0, r1l0, r0l1, r1l1}:
      RView{Nat.add(r0l0, r0l1), Nat.add(r1l0, r1l1)}

def total(j: Joint) -> Nat:
  match j:
    case Joint{r0l0, r1l0, r0l1, r1l1}:
      Nat.add(Nat.add(r0l0, r1l0), Nat.add(r0l1, r1l1))

def joint00(j: Joint) -> Nat:
  match j:
    case Joint{r0l0, r1l0, r0l1, r1l1}:
      r0l0

def correlated() -> Joint:
  Joint{1n, 0n, 0n, 1n}

def anticorrelated() -> Joint:
  Joint{0n, 1n, 1n, 0n}

# A local L bit flip changes the joint distribution but not R's marginal.
def left_flip(j: Joint) -> Joint:
  match j:
    case Joint{r0l0, r1l0, r0l1, r1l1}:
      Joint{r0l1, r1l1, r0l0, r1l0}

def left_flips(n: Nat, j: Joint) -> Joint:
  match n:
    case 0n:
      j
    case 1n+p:
      left_flips(p, left_flip(j))

# A two-state, exact-count linear map. An instrument has one map per R outcome.
# For a valid stochastic instrument, both outcome maps' column sums equal denom.
type Matrix2 is Data:
  Matrix2{out0in0: Nat, out0in1: Nat, out1in0: Nat, out1in1: Nat}

def apply_matrix(m: Matrix2, state: RView) -> RView:
  match m state:
    case Matrix2{a, b, c, d} RView{+w0, +w1}:
      RView{Nat.add(Nat.mul(a, w0), Nat.mul(b, w1)),
            Nat.add(Nat.mul(c, w0), Nat.mul(d, w1))}

type Instrument is Data:
  Instrument{denom: Nat, outcome0: Matrix2, outcome1: Matrix2}

# A valid instrument has a positive denominator and its outcome maps' two
# column sums equal that denominator. This is the exact normalization rule.
def valid_instrument(inst: Instrument) -> Bool:
  match inst:
    case Instrument{+denom, Matrix2{a, b, c, d}, Matrix2{e, f, g, h}}:
      Bool.and(
        Nat.is_gt(denom, 0n),
        Bool.and(
          Nat.is_eq(Nat.add(Nat.add(a, c), Nat.add(e, g)), denom),
          Nat.is_eq(Nat.add(Nat.add(b, d), Nat.add(f, h)), denom)))

def read_bit() -> Instrument:
  Instrument{1n, Matrix2{1n, 0n, 0n, 0n},
              Matrix2{0n, 0n, 0n, 1n}}

def flip_then_read() -> Instrument:
  Instrument{1n, Matrix2{0n, 1n, 0n, 0n},
              Matrix2{0n, 0n, 1n, 0n}}

# Every finite procedure chooses the next R-only instrument from the prior
# outcome, allowing adaptive preparation, controls, and readout.

type Procedure is Data:
  Done{}
  Ask{instrument: Instrument, on_zero: Procedure, on_one: Procedure}

def valid_procedure(p: Procedure) -> Bool:
  match p:
    case Done{}:
      True{}
    case Ask{instrument, on_zero, on_one}:
      Bool.and(valid_instrument(instrument),
        Bool.and(valid_procedure(on_zero), valid_procedure(on_one)))

# Each leaf is an exact transcript weight with its denominator. A Fork's
# left/right subtrees correspond to the next recorded R bit 0/1.
type TranscriptTree is Data:
  End{weight: Nat, denom: Nat}
  Fork{next0: TranscriptTree, next1: TranscriptTree}

# Zero-coupling semantics: the local instrument sees only the R marginal.
# Branch states retain their unnormalized weights across adaptive steps.
def run_r(p: Procedure, +state: RView, +scale: Nat) -> TranscriptTree:
  match p:
    case Done{}:
      match state:
        case RView{w0, w1}:
          End{Nat.add(w0, w1), scale}
    case Ask{instrument, on_zero, on_one}:
      match instrument:
        case Instrument{+denom, outcome0, outcome1}:
          Fork{
            run_r(on_zero, apply_matrix(outcome0, state), Nat.mul(scale, denom)),
            run_r(on_one, apply_matrix(outcome1, state), Nat.mul(scale, denom))
          }

def run_from_joint(p: Procedure, j: Joint, base_denom: Nat) -> TranscriptTree:
  run_r(p, reduce_r(j), base_denom)

def adaptive_example() -> Procedure:
  Ask{read_bit(),
      Ask{flip_then_read(), Done{}, Done{}},
      Ask{read_bit(), Done{}, Done{}}}
