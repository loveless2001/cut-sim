# Plan: Orientation-Gauge Test (Prop 7.2 candidate) — two-sided fermion TFD

Fulfills `orientation-test.md`. Spec is the requirements doc; this plan fixes the design,
conventions, thresholds and verdict criteria BEFORE any experiment code is written or run.

**OUTCOME (2026-07-20):** all phases complete, gates G0–G9 all pass. **P7.2a HOLDS**
(max D_internal(O+ vs O−, g=0) = 2.0e−15 across the full sweep) and **P7.2b HOLDS**
(1.4e−14; theorem demonstrated, stated as such), with all positive controls firing.
Crossover law found: orientation onset ∝ g², purification onset ∝ g — see
`docs/results-writeup-orientation.md`. One pre-run amendment (A1, clock parity kick).

## Status
- [x] Phase 1: TFD Gaussian state machinery (`src/tfd-gaussian-state-construction.py`)
- [x] Phase 2: exact O+/O- evolution + coupling window (`src/orientation-flip-evolution.py`)
- [x] Phase 3: internal side-R battery (`src/internal-battery-side-r.py`)
- [x] Phase 4: god's-eye discriminators (`src/gods-eye-discriminators.py`)
- [x] Phase 5: gates G0–G9 (`src/validate-orientation-gates.py`)
- [x] Phase 6: sweep driver + plots → results, write-up

## Model & conventions (fixed here, used everywhere)
1D tight-binding free fermions per side, N sites, PBC, `h[i,i±1] = -J`, J = 1.
Doubled system: modes 0..N-1 = side L, N..2N-1 = side R. State stored as the complex pair
- `G[i,j] = <c†_j c_i>` (Hermitian), `F[i,j] = <c_i c_j>` (antisymmetric).
- Evolution under any real-symmetric single-particle `H1`: `U = exp(-i H1 t)` (eigh, exact),
  `G(t) = U G U†`, `F(t) = U F Uᵀ`. No Trotter error anywhere.
- Nambu block for a site set A: `Nmb = [[I-G_A, F_A], [F_A†, G_Aᵀ]]`; eigenvalues λ ∈ [0,1]
  come in pairs (λ, 1-λ); `S(A) = -Σ_λ λ ln λ`, `purity(A) = exp(½ Σ_λ ln(λ²+(1-λ)²))`,
  entanglement spectrum = sorted λ.
- TFD(β) built in the real eigenbasis {φ_a, ε_a} of one side's `h` (avoids ±k degeneracy
  ambiguity): `n_a = 1/(1+e^{βε_a})`, `G_LL = G_RR = Σ_a n_a φ_a φ_aᵀ`,
  `F_LR[x,y] = Σ_a φ_a(x) φ_a(y) √(n_a(1-n_a))` (sign convention: |1⟩ ≡ c†_{R,a} c†_{L,a}|0⟩,
  giving +√(n(1-n)); the opposite sign is a gauge phase, irrelevant to every observable used).
  All t=0 correlation matrices are REAL.

## Θ_L — anti-unitarity subtlety (documented per spec)
A strictly-L-local anti-unitary does not lift basis-independently to the tensor product; the
operational, unambiguous content of "flip L's modular time direction" is the flipped generator.
Two numerically distinct implementations, BOTH run, verdicts (and R-trajectories) must agree:
- **Impl A (flipped generator)**: evolve under `H1(s=-1) = -h_L ⊕ h_R (+ g coupling)`.
- **Impl B (conjugation sandwich)**: `K ∘ evolve under (+h_L ⊖ h_R + g·K-coupling) ∘ K`, where
  K = entrywise complex conjugation of (G, F) (legal because h is real in the position basis).
Equivalence requirement: max |Δ(G,F)(t)| between A and B < 1e-10 across the sample grid.
Since the t=0 matrices are real, Θ_L acts trivially on the initial state (TFD is T-invariant);
the flip lives purely in the dynamics. Gate G3 verifies ρ_R(0) invariance explicitly.

## Variants & protocols
Orientation s ∈ {+1 (O+), -1 (O-)} × complement ∈ {mirror TFD, scrambled} × g-sweep.
- **Scrambled purification**: convert (G,F) → Majorana covariance Γ (4N×4N), apply a Haar-random
  `O ∈ O(2N)` to the L-Majorana rows/cols, convert back. Preserves ρ_R and global purity exactly
  (gate G5). Fixed RNG seed 20260720 (one draw, shared by all runs — pre-registered).
- **Coupling**: `H_g = g Σ_{i∈W} (c†_{L,i} c_{R,i} + h.c.)`, window W = 16 sites centred at
  c = N/2. g ∈ {0, 1e-3, 1e-2, 1e-1}.
Per variant, three exact runs (all report side-R data only to the battery):
- **main**: bare variant Hamiltonian; t ∈ linspace(0, 40, 81).
- **quench**: + `V n_q` on R, q = c, V ∈ {1, 3}; same t grid.
- **clock**: h_R with two cavities carved (boundary bonds cut): C1 ℓ=8 inside W, C2 ℓ=13
  diametrically opposite; t ∈ linspace(0, 300, 1200).

## Endogenous observer (side R only)
- **Rod**: RMS width of the bound state of `h_R - ε₀|q⟩⟨q|` (ε₀ = 1.5), via the 1D lattice
  Green's function — same static-binding construction as cut-sim. Built from side-R statics
  only; identical across variants by construction (it is the unit, not the signal).
- **Clock/tick**: measured per variant per run: coherence `z_m(t) = <a†_1 a_2>(t)` of the two
  lowest modes of cavity m (a_i = cavity eigenmode operators, R-local); tick τ̂_m = 2π/ω̂_m with
  ω̂_m from an unwrapped phase-slope fit of z_m(t). The wall-insertion quench itself supplies
  the initial two-mode coherence (no extra excitation needed).
All battery times in ticks of C1, lengths in rods, values dimensionless.

## Internal battery (pre-registered items; each computed per variant)
1. **clock-ratio**: scalar ω̂_1/ω̂_2; plus dimensionless coherence traces z_m(t/τ̂_1)/z_m(0).
2. **two-time correlator**: `C<(x,t) = <c†_x(t) c_{x0}(0)>` on R probes x0 = c, offsets
   {0,2,4,8,12,18,24,32} (reported in rods), t grid of main run (in ticks). Exact formula:
   `C< = conj(U G)` rows. Full complex array is the item value.
3. **KMS**: on-site C<, C> at x0; symmetrize C(-t)=C(t)*, Hann-windowed FFT → S<(ω), S>(ω);
   β̂ = LSQ slope of ln[S>(ω)/S<(ω)] over bins with weight > 1e-3·max. Item: β̂/τ̂_1.
4. **quench arrow**: S_A(t) for A = 24 sites centred at q, per V; item = curves S_A(t/τ̂_1).
5. **coherence floor**: purity_A(t) and top-8 entanglement spectrum λ(t) on the main run.
6. **D_internal** = max over items of d(X_v1, X_v2), with the pre-registered metric
   `d(X,Y) = ||X-Y||₂ / max(||X||₂, ||Y||₂, 1e-300)` (arrays flattened, scalars are 1-vectors).
Comparisons: P7.2a: (O+,mirror) vs (O-,mirror) at each g [also scrambled pair, reported];
P7.2b: (O+,mirror) vs (O+,scrambled) at each g.

## God's-eye discriminators (battery calibration; may use L data & bare units)
- **ge-MI**: I(L_w : R_w)(t), aligned 32-site windows at c; O+ vs O- distance d.
- **ge-cross-phase**: anomalous cross correlator `K(x,t) = <c_{L,x}(t) c_{R,c}(0)> = (U F) rows`
  (the number-conserving <c†_L c_R> vanishes identically for the TFD — noted per spec), O+ vs O-.
- **ge-complement**: d(G_LL(0) mirror, G_LL(0) scrambled) — the L-sector mirror/scrambled probe.
Fire threshold (pre-registered): **θ_fire = 1e-6** on d; expected magnitudes O(0.1–1).

## Pre-registered gates (ALL must pass; hard exit; run at N=128, β=1 unless stated)
G0 (extra): machinery vs dense Fock-space many-body computation at N=2, β=0.7: TFD (G,F),
    S_L, S_R, coupled+flipped evolution of ρ_R — max deviation < 1e-10.
G1  max|G_RR - Σ n_a φφᵀ| < 1e-12.        G2  |S_L - S_R| < 1e-10, global max λ(1-λ) < 1e-12.
G3  Θ_L (impl B map) leaves R blocks invariant < 1e-12; impl A/B trajectory agreement < 1e-10.
G4  g=0: max_t |G_RR(t) - G_RR(0)| < 1e-10 under O+ and O-, and vs single-sided e^{-ih_R t}.
G5  scrambled: |ΔG_RR|, |F_RR| < 1e-12 at t=0; global purity preserved < 1e-12.
G6  ω̂_1 (dynamics, g=0) vs analytic two-mode gap 2J[cos(π/(ℓ+1)) - cos(2π/(ℓ+1))]: rel < 1e-8.
G7  every god's-eye discriminator fires: d > θ_fire at g=0.
G8  every internal item fires at g=0.1: d > θ_fire on BOTH axes (orientation, purification).
G9  |Tr G(t) - Tr G(0)| and |Tr(H1 G(t)) - Tr(H1 G(0))| < 1e-10 (relative) on all runs.

## Verdict criteria (pre-registered, verbatim from spec)
- **P7.2a HOLDS** iff D_internal(O+ vs O-, g=0) < 1e-9 across the FULL sweep AND G7, G8 pass.
- **P7.2b HOLDS** iff D_internal(mirror vs scrambled, g=0) < 1e-9 AND ge-complement fires.
- **FALSIFIED** iff any internal item exceeds 1e-9 at g=0 with all gates green — report which
  item; do not tune it away.
- **INCONCLUSIVE** iff any gate fails or a positive control does not fire. Fix or report;
  never delete a battery item.
- Report the crossover: smallest sweep g at which each item fires + log-log D_internal(g)
  with fitted small-g slope (expected: slope 1 for amplitude-linear items, 2 for quadratic).
- P7.2b at g=0 is a theorem (all R-observables are functionals of ρ_R); the sim demonstrates
  the machinery realizes it — stated plainly in the write-up, not claimed as discovery.

## Sweep grid (runtime target: < 10 min laptop total)
- g-sweep {0, 1e-3, 1e-2, 1e-1} × β ∈ {1, 4} at N = 256.
- N-sweep {64, 128, 512} at β = 1, g ∈ {0, 0.1} (null + control at every size).
- β = 0.5 extra null point at N = 256, g = 0. Quench V ∈ {1, 3} everywhere.
Geometry scales with N: all centres at N/2; fixed device sizes (W=16, ℓ=8/13, A=24, MI=32).

## Files
- `src/tfd-gaussian-state-construction.py` — h, eigenbasis, TFD, Majorana ⇄ complex, scramble,
  Θ_L map, Nambu entropy/purity/spectrum
- `src/orientation-flip-evolution.py` — variant H1 assembly (s, g, cavity cuts, quench),
  propagator, (G,F) trajectories, two-time correlators, densities, conservation checks
- `src/internal-battery-side-r.py` — rod, clock fit, items 1–5, metric d, D_internal
- `src/gods-eye-discriminators.py` — ge-MI, ge-cross-phase, ge-complement
- `src/validate-orientation-gates.py` — G0–G9, exit 0 iff all pass
- `src/run-orientation-gauge-experiment.py` — gates → sweep → verdict → results/
  results-orientation.json + plots (plot code in `src/generate-orientation-plots.py`)
- `docs/results-writeup-orientation.md` — honest verdict, g-crossover, theorem-status caveat

## Amendments (logged before the experiment run)
- **A1 (gate G6 failure, 2026-07-20):** the bare two-mode cavity coherence z(0) vanishes
  exactly by a parity selection rule (thermal ring correlator is reflection-symmetric about
  the cavity centre; the two lowest cavity modes have opposite parity). Fix: the clock run
  now includes an R-local preparation kick e^{iθ n_x}, θ = 0.5, on the LEFT HALF of each
  cavity (the observer winds its clock). Gaussian, side-R only, applied identically to every
  variant. No battery item removed; thresholds unchanged.

## Risks
- Item 1 scalar ratio may be resolution-limited at small g (phase fit is exact at g=0, so the
  null is safe); the trace-distance part of item 1 covers the positive control if the fitted
  ratio alone under-fires. Pre-registered as one item with two components (max of the two d's).
- Cavity C1 must overlap W or items 1/3 will not feel g — geometry above guarantees overlap.
- At g=0 the O± propagators are different matrices (different eigh calls): distances land at
  float noise ~1e-13, not exactly 0 — this is the honest version of the null and stays 4
  decades under tolerance.

## Out of scope (restated for the write-up)
No cosmological claim (eternal-TFD idealization only); Gaussian states — no pointer basis,
Born rule, or branching; P7.2b g=0 is a theorem being demonstrated; Θ_L implementation
ambiguity handled by running both A and B.
