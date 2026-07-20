# Results: Orientation-Gauge Test (Prop 7.2 candidate) — two-sided fermion TFD

**Date:** 2026-07-20 · **Spec:** `orientation-test.md` · **Verdict criteria pre-registered in:**
`plans/260720-2257-orientation-gauge-sim/plan.md` (committed before experiment code)

## TL;DR — which verdict rule fired

**P7.2a (orientation gauge) HOLDS.** Across the full sweep (N ∈ {64, 128, 256, 512},
β ∈ {0.5, 1, 4}, quench V ∈ {1, 3}), the maximum internal battery distance between O+ and
O− at g = 0 is **D_internal = 2.0×10⁻¹⁵** — float noise, six decades under the
pre-registered 10⁻⁹ tolerance — while every god's-eye discriminator fires (d = 0.4–1.4)
on the same data and every internal item fires at g = 0.1 (d = 0.02–1.1). The relative
time-orientation of the two sides is gauge for internal observers in this construction.

**P7.2b (purification indistinguishability) HOLDS — as a theorem demonstrated, not a
discovery.** Max internal distance mirror vs scrambled at g = 0: **1.4×10⁻¹⁴**; the
god's-eye complement discriminator sees the swap at d = 0.61 on the same states. All
R-observables are functionals of ρ_R, so this null is mathematically guaranteed; the run
confirms the machinery realizes the theorem to machine precision and that the battery
that fails to see the swap at g = 0 sees it immediately at g > 0.

**The physical content is the crossover law.** Opening the cut makes both distinctions
physical at parametrically different rates:

```
D_internal(O+ vs O−)          ∝ g²    (measured slope 1.98 between g = 10⁻³ and 10⁻²)
D_internal(mirror vs scrambled) ∝ g   (measured slope 1.02, same interval)
```

Mechanism: the leading O(g) correction to any number-conserving R-correlator multiplies
the number-conserving cross-correlation ⟨c†_L c_R⟩, which vanishes identically for the
TFD — so orientation becomes visible only at second order (a round trip through the cut),
while the scrambled complement has ⟨c†_L c_R⟩ ≠ 0 and is detected at first order. Every
battery item already fires at g = 10⁻³ (θ_fire = 10⁻⁶): the "gauge" property is exact at
g = 0 and degrades quadratically, not exponentially — there is no protective gap.

## Setup (details in plan / code)

1D tight-binding free fermions, N sites per side, PBC; global state = fermionic TFD(β)
over L ⊗ R as a complex Nambu correlation pair (G, F); all evolution is exact
single-particle propagation (eigh — no Trotter error). Orientation flip Θ_L = evolve
under −H_L + H_R, run through two independent implementations (flipped generator;
conjugation sandwich) that must and do agree. Scrambled purification = Haar-random
O(2N) rotation of the L Majorana sector (fixed seed 20260720), preserving ρ_R exactly.
Coupling H_g = g Σ_{i∈W} (c†_{L,i} c_{R,i} + h.c.) on a 16-site window.

Endogenous side-R observer: rod = impurity bound-state RMS width (0.943 sites at
ε₀ = 1.5); tick = measured beat period of the two lowest modes of a carved 8-site cavity
(τ̂ = 18.09 at J = 1, matching the analytic two-mode gap to 2×10⁻¹⁶). Battery (all
dimensionless, side-R data only): clock-ratio + coherence traces, two-time correlator
C<(x,t) in rods/ticks, KMS-extracted β̂/tick, quench entropy arrow S_A(t), coherence
floor (purity + entanglement spectrum). D_internal = max item distance,
d(X,Y) = ‖X−Y‖/max(‖X‖,‖Y‖).

**Validation gates G0–G9 all passed**, including the extra G0: the entire
correlation-matrix machinery (TFD construction, entropies, coupled orientation-flipped
evolution) reproduces a dense Fock-space many-body computation at N = 3 to 1.6×10⁻¹⁵.
Purity defect 4×10⁻¹⁵; S_L = S_R exactly; ρ_R thermal to 0; scrambled ρ_R identical to
3×10⁻¹⁷; conservation drift 7×10⁻¹⁵.

## Results

Nulls at g = 0 (D_internal; tolerance 10⁻⁹) and traversable controls at g = 0.1:

| N   | β   | D(O+ vs O−) g=0 | D(mir vs scr) g=0 | D(O±) g=0.1 | D(purif) g=0.1 | ge fires (g=0) |
|-----|-----|------------------|-------------------|-------------|----------------|----------------|
| 256 | 1.0 | 3.4e−16          | 3.7e−16           | 1.23        | 1.13           | 0.83 / 1.4 / 0.61 |
| 256 | 4.0 | 2.0e−15          | 1.2e−14           | 1.08        | 1.00           | 0.92 / 1.3 / 0.83 |
| 256 | 0.5 | 1.5e−15          | 2.4e−15           | —           | —              | 0.81 / 1.4 / 0.39 |
| 64  | 1.0 | 2.5e−16          | 9.8e−15           | 0.80        | 1.21           | 0.51 / 1.4 / 0.61 |
| 128 | 1.0 | 3.2e−16          | 3.8e−16           | 1.13        | 0.89           | 0.73 / 1.4 / 0.61 |
| 512 | 1.0 | 3.8e−16          | 1.4e−14           | 1.20        | 1.22           | 0.83 / 1.4 / 0.61 |

(ge columns: two-sided mutual information I(L_w:R_w)(t) O+ vs O−; anomalous cross
correlator ⟨c_L(x,t) c_R(0,0)⟩ phase structure; mirror-vs-scrambled L-sector probe. The
number-conserving ⟨c†_L(x,t) c_R⟩ correlator vanishes identically for the TFD — the
phase structure lives in the anomalous channel, which is also why orientation onset is g².)

Crossover (N = 256, β = 1; plot `results/orientation-null-and-crossover.png`):

| g     | D(O+ vs O−) | D(mir vs scr) |
|-------|-------------|---------------|
| 0     | 3.4e−16     | 3.7e−16       |
| 10⁻³  | 6.1e−4      | 4.6e−2        |
| 10⁻²  | 5.8e−2      | 4.8e−1        |
| 10⁻¹  | 1.23        | 1.13          |

Smallest firing g for **every** individual battery item, both axes: 10⁻³ (the smallest
nonzero g in the sweep). β = 4 numbers are within 10% of the β = 1 numbers throughout.

Consistency numbers riding along: the internally extracted KMS temperature is
|β̂| = 0.993 at β = 1 and 3.98 at β = 4, identical across all four variants at g = 0
(the ~0.5–0.7% offset is finite-window bias of the FFT extraction, common mode by
construction). Clock coherences |z(0)| = 9.3×10⁻³ / 3.7×10⁻³ per cavity, identical
across variants. Impl A vs Impl B of Θ_L: identical trajectories to 7×10⁻¹⁵, identical
battery distances to 1×10⁻¹³, identical verdicts.

## Interpretation

1. **Falsification did not occur.** No internal item discriminates at g = 0 with all
   gates green; the pre-registered HOLDS rule fired for both claims, with live positive
   controls (a battery that demonstrably CAN see both distinctions when the cut opens).
2. **P7.2a is informative, P7.2b is a demonstration.** At g = 0 with no cross-cut
   interaction, ρ_R(t) is a functional of ρ_R(0) and H_R alone; the sim's value for
   7.2a is showing the *machinery* (including the clock, KMS thermometry, and quench
   arrow all defined operationally from inside R) closes at float precision — the arrow
   of R's own quench dynamics does not care which way L's modular time runs.
3. **"Orientation becomes physical" has a rate.** The g² vs g¹ split is the sharpest
   quantitative statement this sim adds: an internal observer gains access to the
   complement's time-orientation strictly slower (quadratically) than to its
   micro-state (linearly) as a traversable coupling switches on. At g = 10⁻³ J the
   orientation signal is already 6×10⁻⁴ — small but far above any reasonable noise
   floor for a physical detector; gauge-ness at g exactly 0 is a measure-zero idealization.

## Caveats / error budget

- The g = 0 nulls are float noise (10⁻¹⁶–10⁻¹⁴), not exact zeros, because O+ and O−
  propagators come from independent eigendecompositions — pre-registered as the honest
  version of the null (no shared code path that could fake it).
- **Amendment A1 (logged before the run):** the bare two-mode cavity coherence z(0)
  vanishes exactly by a parity selection rule (thermal ring correlator is
  reflection-symmetric about the cavity centre; the two lowest cavity modes have
  opposite parity). The clock run therefore includes an R-local preparation kick
  e^{iθn_x} (θ = 0.5) on the left half of each cavity, applied identically to every
  variant. Found at gate G6; no item removed, no threshold changed.
- The KMS β̂ carries a ~0.7% finite-window systematic (Hann/FFT extraction); it is
  common-mode across variants, and the *item* is the cross-variant distance, which is
  exactly zero at g = 0.
- The scrambled-complement axis at g = 0 shows slightly larger float noise (10⁻¹⁴) than
  the orientation axis — propagation of the 10⁻¹⁷ construction error of the scrambler
  through 10³-step trajectories; still five decades under tolerance.
- Fitted log-log slope over the whole g range (1.65 / 0.70) is compressed by saturation
  at g = 0.1 where D ~ O(1); the quoted 1.98 / 1.02 slopes use the two smallest nonzero
  g points, where the asymptotic power law is clean.

## Out of scope (restated from spec)

- No claim about our cosmological vacuum — this is the idealized eternal-TFD
  construction only.
- Gaussian states: no pointer-basis formation, no Born rule, no branch structure. This
  tests orientation gauge, not branching.
- P7.2b at g = 0 is a theorem; the sim demonstrates it and calibrates the battery — the
  non-trivial empirical content is the calibrated battery and the g-crossover.
- Anti-unitarity subtlety: a strictly L-local anti-unitary does not lift
  basis-independently to the tensor product; the operational content is the flipped
  generator. Both pre-registered implementations were run and agree.

## Unresolved questions

1. The g² orientation onset is argued from ⟨c†_L c_R⟩ = 0 killing the first-order term —
   a one-line perturbative proof for general R-observables (including entropies, which
   are nonlinear in the correlations) was not written down.
2. Does the g² law survive interactions (non-Gaussian TFD), where the cross-correlator
   structure is richer? Needs tensor-network machinery.
3. At β = 0.5 the ge-complement discriminator drops to 0.39 (hotter state → flatter
   spectrum → less L-structure to scramble); at what β does the scrambler become
   god's-eye-invisible (n_a → 1/2 for all a makes every purification unitarily
   equivalent on L)? The β → 0 limit was not probed.
