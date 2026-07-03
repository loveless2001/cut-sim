# cut-sim — Ruler Cancellation / Universal Co-Dispersion Test

Simulation testing one falsifiable claim from "the Cut spec" (Prop 7.1): *an observer
built from the same anisotropic couplings it measures with cannot detect the
substrate's anisotropy through any dimensionless internal experiment.* The framework
spec is `docs/cut_spec.tex` (§9 states the claim and this experiment's result); the
verdict rules and outcome are in `docs/results-writeup.md`.

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

Kebab-case module files are loaded via an importlib bootstrap in the driver scripts.
