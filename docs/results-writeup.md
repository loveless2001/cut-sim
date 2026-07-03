# Results: Ruler Cancellation / Universal Co-Dispersion Test

**Date:** 2026-07-03 · **Spec:** `spec.md` · **Verdict criteria pre-registered in:** `plans/260703-1555-ruler-cancellation-sim/plan.md`

## TL;DR — which verdict rule fired

**The dimensionless battery detects the substrate axis → ruler cancellation FAILS in
general → the framework's naive Lorentz claim is FALSIFIED** (spec verdict rule 2).

Simultaneously, `A_endo` for the observer's *long-wavelength* signals sits between 1 and
`A_god` and flows to 1 approaching the continuum fixed point → the **corrected
(fixed-point co-dispersion) claim is SUPPORTED, but only for the IR observable class**.
The observer's *fastest* signal (the Lieb-Robinson front) remains a dimensionless internal
experiment that detects the axis at **every** tuning value, including arbitrarily close to
the fixed point. The corrected claim survives only if "dimensionless internal experiment"
is restricted to observables that flow to the fixed point; the strong reading ("no
dimensionless internal experiment detects anisotropy") is dead.

## Quantitative law found (not in the spec's expectations)

The endogenous rods (impurity bound-state widths) absorb **exactly half** the anisotropy:

```
rod_x / rod_y → sqrt(Jx/Jy)      (measured 1.4142 at r=2, 1.7321 at r=3 — 4-digit match)
```

Ballistic front speeds scale as `J_d`, binding lengths as `sqrt(J_d)`, so

```
A_endo(front) → sqrt(A_god)      (measured 1.4195 vs sqrt(2.0075)=1.4169 at r=2)
```

— a clean partial-cancellation law: the observer sees the anisotropy *square-rooted*, not
cancelled. Low-energy wavepacket speeds scale as `J_d·k_d` with `k_d ∝ 1/rod_d ∝ 1/sqrt(J_d)`,
so for IR signals both sides scale as `sqrt(J_d)` and the ratio cancels exactly — this is
the mechanism of fixed-point co-dispersion, verified numerically below.

## Setup (details in README / code)

2D anisotropic tight-binding free fermions, PBC, exact FFT propagator (no Trotter error).
- God's-eye: LR front fits in bare lattice units (Airy-corrected; ~1%/axis systematic).
- Rod(d): RMS width of an attractive point-impurity bound state (exact lattice Green's
  function) — static binding length; never site counting, never signal-defined.
- Clock: beat period of a 5×5 cavity's two lowest modes (shared scalar; cancels in ratios).
- Tuning: impurity strength ε sets rod size ξ; ε→0 ⇒ bound state at threshold ⇒ ξ→∞ =
  approach to the continuum Gaussian fixed point ("criticality" for this free theory).
- Battery: front-speed ratio, endogenous-wavepacket ratio, spreading (birefringence)
  anisotropy — all pure rods-per-tick ratios. Detection = |R−1| > max(2%, 5σ), fixed
  before running.

**Validation gates all passed** (`src/validate-physics-sanity-checks.py`): unitarity at
machine precision; front fits within 1.6% of the exact band-edge velocities 2J; band-edge
wavepacket check at 0.2%; isotropic substrate gives every ratio = 1.0000 (no fake
anisotropy); and — spec's trap #4 — the battery fed god's-eye data DETECTS the anisotropy
on all three tests at r=2 and stays null at r=1. Its endogenous nulls are therefore live.

## Results at several coupling ratios (largest rod = most-continuum point)

| r=Jx/Jy | A_god (meas.) | rod_x/rod_y | A_endo front | √A_god | A_endo wavepacket | battery |
|---------|---------------|-------------|--------------|--------|-------------------|---------|
| 1.0     | 1.0000±0.011  | 1.0000      | 1.0000       | 1.0000 | 1.0000            | null ✓  |
| 1.25    | 1.2516±0.016  | 1.1181      | 1.1194       | 1.1188 | 1.0006            | DETECTS |
| 1.5     | 1.5075±0.020  | 1.2248      | 1.2308       | 1.2278 | 1.0004            | DETECTS |
| 2.0     | 2.0075±0.048  | 1.4142      | 1.4195       | 1.4169 | 1.0002            | DETECTS |
| 3.0     | 2.9222±0.038  | 1.7321      | 1.6871       | 1.7095 | 1.0002            | DETECTS |

(A_god carries the ~1%/axis front-fit systematic; exact values are r. rod ratios match
√r to 4 digits. "battery DETECTS" is driven by the front-ratio test at large ξ.)

## The tuning sweep (r=2; plot: `results/tuning-sweep-r2.png`)

| ξ (sites) | A_endo front | A_endo wavepacket | spreading R |
|-----------|--------------|-------------------|-------------|
| 0.18      | 1.097        | 1.093             | 1.030       |
| 0.45      | 1.269        | 1.264             | 0.918       |
| 0.97      | 1.375        | 1.450             | 0.971       |
| 2.03      | 1.409        | 1.064             | 0.993       |
| 3.68      | 1.416        | 1.018             | 0.998       |
| 8.94      | 1.419        | 1.0030            | 0.9997      |
| 39.3      | 1.4195       | 1.0002            | 1.0000      |

Exactly the spec's "expected honest result" — for IR observables: `A_endo(wp)` ≈ A_god at
lattice scale, → 1 approaching the fixed point (deviation shrinking roughly as 1/ξ²), and
the spreading/birefringence test goes null the same way. **But the front experiment never
renormalizes**: it saturates at √A_god = 1.42 and stays 5σ-DETECTED at every ξ, because
the LR front velocity is set by band-edge (UV) modes that do not flow — while the rods do.

## Interpretation

1. **Naive claim (any endogenous observer is blind to substrate anisotropy): FALSIFIED.**
   An observer that times its fastest signals against its binding-length rods measures a
   direction-dependent "speed of light", ratio √(Jx/Jy), at any coupling and any tuning.
2. **Corrected claim (co-dispersion at the RG fixed point): SUPPORTED, with a sharp
   scope restriction.** Everything built from long-wavelength physics — wavepacket
   speeds, dispersion/birefringence, packet shapes — co-disperses with the rods and
   becomes exactly isotropic at the fixed point. Emergent effective Lorentz invariance
   holds for the IR sector only.
3. **The loophole is physical, not numerical:** rods renormalize as √J (bound-state
   scaling), ballistic fronts as J (band edge). Any observable mixing the two scales
   detects the axis. For the framework this means Prop 7.1 needs the qualifier
   "fixed-point observables"; an endogenous observer with access to lattice-scale
   signals (its own LR cone) registers the anisotropy from inside.
4. **Spec's "surprising result worth watching for"** (automatic cancellation everywhere,
   off-criticality too) did **not** occur: at lattice-scale rods (ξ ≲ 1) even the
   wavepacket observable tracks — and transiently overshoots — A_god.

## Caveats / error budget

- Front velocities carry a ~1%/axis Airy-edge systematic (threshold-front estimator),
  folded into σ; it slightly biases A_endo(front) at r=3 (1.687 vs √3=1.732, consistent
  within the stated systematics). Conclusions never hinge on <2% margins except where
  the pre-registered criteria demand it, and those points sit 10–30σ away.
- Mid-sweep wavepacket spikes (e.g. R=2.61 at r=3, ξ=0.67) occur where the endogenous
  wavelength hits the Brillouin-zone edge (UV cap engaged, flagged `uv_capped`) — the
  observer's continuum experiment degenerating at lattice scale, itself a detection.
- r=3, ε=1.5 (ξ=161) skipped: bound state exceeds the largest lattice (L=2048). One
  point, does not affect trends.
- Single-particle sector evolution is exact correlation-matrix dynamics for these
  quench/packet initial states; no many-body approximation is involved.
- The clock's beat frequency is set by the softer axis (0.732·min(Jx,Jy)); as a shared
  scalar it cancels in every ratio reported, so no directional leak.

## Not tested (by design)

The ontological postulate ("unregistrable ⟹ not a fact") — philosophy, out of scope.
This sim tested only the physical antecedent, and the answer is: **substrate anisotropy
IS registrable by an endogenous observer, except exactly at the fixed point and only for
fixed-point observables.**

## Unresolved questions

1. Does an interacting (non-Gaussian) fixed point change the front's status — i.e., can
   interactions make the *front itself* renormalize so the √A_god plateau also flows to 1?
   (Free-theory front is pinned at the band edge; this is the natural next sim, but needs
   MPS/tensor-network machinery, not Gaussian dynamics.)
2. Is the 1/ξ² approach of A_endo(wp) → 1 the leading irrelevant-operator exponent one
   would predict from the lattice dispersion's quartic term? (Consistent visually; a
   dedicated scaling fit was not run.)
3. Whether a smarter endogenous rod (e.g. built from the front itself) trivially cancels
   the front anisotropy — excluded here as tautological, but the framework text should
   state which rod constructions are admissible.
