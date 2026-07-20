# Spec: Orientation-Gauge Test (Prop 7.2 candidate) — two-sided fermion TFD

Extension of `loveless2001/cut-sim`. Follow that repo's conventions exactly:
kebab-case modules, importlib bootstrap in drivers, pre-registered gates that
must ALL pass before the experiment runs, honest verdict write-up, results as
JSON + plots, exact methods only (no Trotter error).

## Claim under test

**P7.2a (orientation gauge).** For a pure global state cut into two sides L | R
with no cross-cut interaction, the relative time-orientation of the two sides is
gauge for internal observers: no dimensionless experiment performed entirely on
side R, using rods and clocks built from side-R dynamics, can detect a flip of
side L's modular time direction.

**P7.2b (purification indistinguishability).** Same setup: no side-R internal
dimensionless experiment can distinguish whether the complement L is (i) the
mirror TFD partner or (ii) a scrambled Gaussian purification with the same
reduced state ρ_R. (Mathematically this is a theorem — all R-observables are
functionals of ρ_R. The sim's job is to confirm the machinery realizes the
theorem to numerical precision, and to demonstrate the positive controls where
the distinction DOES become physical.)

**Physicality condition (positive control, must fire).** Both distinctions
become detectable from inside R the moment a cross-cut coupling g ≠ 0 is
switched on (traversable cut). The battery must demonstrably fire in that case;
otherwise a null result on P7.2a/b is meaningless.

Framing for the writeup: falsification of P7.2a/b = any internal battery item
discriminating at g = 0. Confirmation is only reportable alongside proof that
the same battery discriminates at g > 0 and at God's-eye level.

## Model

1D tight-binding free fermions, chain length N per side (N = 256 default;
sweep 64–512), periodic boundaries. H_side = -J Σ (c†_i c_{i+1} + h.c.).
Global state: fermionic thermofield double at inverse temperature β over the
doubled lattice L ⊗ R:

|TFD(β)⟩ ∝ Σ_n e^{-βE_n/2} |n⟩_L ⊗ |n̄⟩_R

For free fermions this is Gaussian: per momentum mode k, occupations
⟨c†_{L,k} c_{L,k}⟩ = ⟨c†_{R,k} c_{R,k}⟩ = n_F(ε_k) and anomalous cross
correlations |⟨c_{L,k} c_{R,k}⟩| = sqrt(n_F(1-n_F)). Represent the full state
as a 4N × 4N Majorana (or complex Nambu) correlation matrix. All evolution is
exact one-particle propagation of the correlation matrix.

Orientation flip Θ_L: anti-unitary time reversal on the L sector
(equivalently: evolve L under -H_L and complex-conjugate the L block of the
correlation matrix). Pre-registered requirement: Θ_L must leave ρ_R(t=0)
invariant exactly — this is a gate, not an assumption.

Global evolutions to compare:
- O+ : H = H_L + H_R (both times forward)
- O- : H = Θ_L-flipped, i.e. -H_L + H_R (relative orientation reversed)

Complement swap for P7.2b: replace the L block + cross correlations with a
Haar-random Gaussian purification of the same ρ_R (random orthogonal rotation
in the purifying sector; same single-particle entanglement spectrum). Verify
ρ_R identical to machine precision before running.

Cross-cut coupling for positive control: H_g = g Σ_{i ∈ window}
(c†_{L,i} c_{R,i} + h.c.), quadratic, so everything stays exact. Sweep
g ∈ {0, 1e-3, 1e-2, 1e-1} J.

## Endogenous observer (side R only) — reuse cut-sim constructions

- **Rod**: impurity bound-state width on side R (static binding length, same
  construction as `endogenous-observer-rods-clock.py`).
- **Clock**: beat period of the two lowest modes of a small cavity carved into
  side R. All times reported as ticks; all lengths as rods. No bare lattice
  units anywhere in the battery.

## Dimensionless internal battery (all side-R, all rods-per-tick or pure ratios)

Each item is computed under {O+, O-} × {mirror, scrambled} × g-sweep.

1. **Clock-ratio invariance**: ratio of beat periods of two different cavities
   on R.
2. **Two-time correlators in internal units**: G(x,t) = ⟨c†_R(x, t) c_R(0,0)⟩
   with x in rods, t in ticks; compare full functions (L2 distance).
3. **KMS check**: verify the KMS relation for R correlators at the modular
   temperature; the extracted dimensionless βω product must be
   orientation-invariant.
4. **Quench arrow test**: local quench on R; S_A(t) for an R-subregion must
   grow toward R's own future identically under O+ and O-.
5. **Coherence-floor test**: purity and entanglement spectrum of R-subregions
   over time.
6. **Adversarial discriminator**: train nothing; instead compute the maximal
   difference over the whole battery, D_internal = max over items of the
   normalized distance between orientation/purification variants. This is the
   single number the verdict reads.

## God's-eye discriminators (must fire — battery calibration)

- Two-sided mutual information I(L_window : R_window) over time under O+ vs O-.
- Cross correlator ⟨c†_L(x,t) c_R(0,0)⟩ phase structure under orientation flip.
- For P7.2b: any L-sector observable distinguishing mirror vs scrambled.

Each God's-eye discriminator must exceed threshold where the corresponding
internal item at g = 0 must not. Same logic as the anisotropy battery
calibration in cut-sim.

## Pre-registered sanity gates (ALL must pass before the experiment script runs)

G1. ρ_R of the constructed TFD equals the exact thermal state: max entry error
    of the R correlation block vs Fermi-Dirac < 1e-12.
G2. S_L = S_R for the global pure state to < 1e-10 (and global purity exact).
G3. Θ_L leaves ρ_R(0) invariant to < 1e-12.
G4. At g = 0, ρ_R(t) from the two-sided evolution matches single-sided thermal
    evolution of ρ_R to < 1e-10 for all sampled t.
G5. Scrambled purification reproduces ρ_R to < 1e-12 at t = 0.
G6. Cavity clock beat period matches the analytic two-mode value to < 1e-8.
G7. Each God's-eye discriminator fires (> pre-set threshold) on O+ vs O-.
G8. Each internal battery item fires at g = 0.1 J (traversable control).
G9. Energy and particle number conserved under evolution to < 1e-10.

## Verdict criteria (pre-registered; write them into plan.md before coding)

- **P7.2a HOLDS** iff D_internal(O+ vs O-, g=0) < 1e-9 across the full sweep
  (N, β, quench parameters) AND G7, G8 pass.
- **P7.2b HOLDS** iff D_internal(mirror vs scrambled, g=0) < 1e-9 AND the
  God's-eye mirror/scrambled discriminator fires.
- **FALSIFIED** iff any internal item exceeds tolerance at g = 0 with gates
  green. Report which item; do not tune it away.
- **INCONCLUSIVE** iff any gate fails or the positive controls don't fire.
  Fix or report; never delete a battery item to reach a verdict.
- Additionally report the crossover: smallest g at which each internal item
  fires (log-log plot of D_internal vs g). Expected slope near g→0 documents
  how fast "orientation becomes physical" as the cut opens.

## Deliverables

1. `src/tfd-gaussian-state-construction.py` — TFD + scrambled purification
   builders, correlation-matrix formalism, Θ_L implementation.
2. `src/orientation-flip-evolution.py` — exact evolution under O+/O-, coupling
   window, entropy from correlation matrices.
3. `src/internal-battery-side-r.py` — rods, clock, items 1–6.
4. `src/gods-eye-discriminators.py` — calibration discriminators.
5. `src/validate-orientation-gates.py` — G1–G9, hard exit on failure.
6. `src/run-orientation-gauge-experiment.py` — sweep driver → results/
   (results-orientation.json + plots).
7. `plans/<date>-orientation-gauge-sim/plan.md` — design + these verdict
   criteria, committed BEFORE experiment code.
8. `docs/results-writeup-orientation.md` — honest verdict, cut-sim style,
   including the g-crossover plot and the theorem-status caveat for P7.2b.
9. Optional web: `web/orientation-gauge-lab.html` embedding
   results-orientation.json, God's-eye ⇄ Cut toggle showing the same R-side
   data under both orientations (they must be pixel-identical) and the g-slider
   where they visibly diverge.

## Out of scope — state this in the writeup

- No claim about our cosmological vacuum. This is the idealized eternal-TFD
  construction only.
- Gaussian states: no pointer-basis formation, no Born rule, no branch
  structure. This tests orientation gauge, not branching (that is the separate
  qubit+apparatus+bath toy from the ⊥-criterion thread).
- P7.2b at g = 0 is a theorem; the sim demonstrates, it does not discover.
  Say so plainly. The non-trivial empirical content is the calibrated battery
  + the g-crossover.
- Anti-unitarity subtlety: document the exact correlation-matrix
  implementation of Θ_L in the plan; if implementation choices exist, run both
  and require identical verdicts.

## Numerics

numpy/scipy only, matplotlib for plots, same venv recipe as cut-sim README.
Everything via single-particle correlation matrices — nothing exponential in N.
Target runtime: full sweep under 10 minutes on a laptop at N = 256.