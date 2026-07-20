# cut-sim — Ruler Cancellation / Universal Co-Dispersion Test

Simulation testing one falsifiable claim from "the Cut spec" (Prop 7.1): *an observer
built from the same anisotropic couplings it measures with cannot detect the
substrate's anisotropy through any dimensionless internal experiment.* The framework
spec is `docs/cut_spec.tex` (§9 states the claim and this experiment's result); the
verdict rules and outcome are in `docs/results-writeup.md`.

**Second experiment (Prop 7.2 candidate):** orientation-gauge test on a two-sided
fermion TFD — can an observer inside side R detect a flip of side L's time direction,
or a swap of its mirror partner for a scrambled purification, at zero cross-cut
coupling? Spec: `orientation-test.md`; pre-registration:
`plans/260720-2257-orientation-gauge-sim/plan.md`; verdict (both claims HOLD at float
precision, crossover law D ∝ g² / g found): `docs/results-writeup-orientation.md`.

```bash
.venv/bin/python3 src/validate-orientation-gates.py        # gates G0–G9 must ALL pass
.venv/bin/python3 src/run-orientation-gauge-experiment.py  # → results/results-orientation.json + plots
```

## Model

2D anisotropic tight-binding free fermions (`Jx ≠ Jy`), periodic boundaries.
All dynamics are **exact** (single-particle propagator via FFT — no Trotter error).

- **God's-eye control**: Lieb-Robinson cone velocities in bare lattice units → `A_god = vx/vy`.
- **Endogenous observer**: rod = impurity bound-state width per axis (static binding
  length, not site counting, not signal-defined); clock = beat period of a small
  cavity's two lowest modes. Speeds measured only in rods-per-tick → `A_endo`.
- **Dimensionless battery**: front-speed ratio, endogenous wavepacket ratio, spreading
  (birefringence) anisotropy — each calibrated on god's-eye data where it must fire.
- **Tuning sweep**: impurity strength ε sets rod size ξ; ξ→∞ = approach to the
  continuum (Gaussian RG fixed point).

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install numpy scipy matplotlib
.venv/bin/python3 src/validate-physics-sanity-checks.py   # gates must ALL pass first
.venv/bin/python3 src/run-ruler-cancellation-experiment.py # → results/ (JSON + plots)
```

## Interactive web bundle

`web/` is a self-contained static site for exploring the framework and the experiment —
no build step, no external dependencies, works from disk or any static host
(e.g. GitHub Pages: serve the `web/` directory). Light/dark theme aware.

- `index.html` — overview: thesis, status-tag legend, the two turtles
- `the-cut-game.html` — **the game** (`game-spec.md`): six levels behind a God's-eye ⇄ Cut
  toggle; Levels 1–4 run the live exact sims, Level 5 replays the real measured data,
  and the framework's gaps (the two turtles, the falsified claim) are playable
- `framework-explorer.html` — the full spec as claim cards, filterable by epistemic tag
- `time-as-forgetting-lab.html` — live 1D fermion chain: S_A(t) after a quench (exact)
- `lieb-robinson-cone-lab.html` — live 2D anisotropic lattice: the elliptical cone (exact)
- `ruler-cancellation-verdict-lab.html` — the experiment's measured data, interactive

The in-browser simulations run the same exact free-fermion methods as the python code
(FFT propagator, correlation-matrix entropy); the Verdict Lab embeds real data generated
from `results/results.json`.

## Layout

- `src/lattice-model-exact-fft-evolution.py` — dispersion, exact evolution, impurity
  bound state (lattice Green's function), cavity clock
- `src/gods-eye-cone-velocity-measurement.py` — LR front tracking, Airy-corrected fits
- `src/endogenous-observer-rods-clock.py` — rods, tick, wavepacket experiments
- `src/dimensionless-anisotropy-detection-battery.py` — the adversarial battery
- `src/run-ruler-cancellation-experiment.py` — full sweep driver
- `src/validate-physics-sanity-checks.py` — pre-registered sanity gates
- `plans/260703-1555-ruler-cancellation-sim/plan.md` — design + pre-registered verdict criteria
- `docs/results-writeup.md` — honest verdict write-up (deliverable 5)

Orientation-gauge experiment (two-sided TFD):

- `src/tfd-gaussian-state-construction.py` — TFD + scrambled purification, Majorana ⇄
  Nambu correlation machinery, Θ_L, entropies
- `src/orientation-flip-evolution.py` — exact O+/O- evolution, coupling window, two-time
  correlators, Impl-B Θ_L path
- `src/internal-battery-side-r.py` — rod, cavity clock, the six dimensionless items
- `src/gods-eye-discriminators.py` — MI, cross-phase, complement discriminators
- `src/validate-orientation-gates.py` — gates G0–G9 (incl. dense Fock-space cross-check)
- `src/run-orientation-gauge-experiment.py` — sweep driver → `results/results-orientation.json`
- `src/generate-orientation-plots.py` — result plots

Kebab-case module files are loaded via an importlib bootstrap in the driver scripts.
