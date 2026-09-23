# cut-sim — The Cut framework and realization tests

## Framework map

| Layer | Repository authority | Scope |
|---|---|---|
| Operational core | [`docs/operational-core.md`](docs/operational-core.md) · [public module](web/operational-core.html) | Distinguishability, records, procedure composition, inference scope, and causal accessibility/identifiability |
| Physical realization | [`docs/cut_spec.tex`](docs/cut_spec.tex) | The current chosen tensor factorization, pure-state/unitary quantum model, Hamiltonian split, and declared apparatus assumptions |
| Phenomena and interpretations | Spec sections, labs, game, and result write-ups | Conditional studies of clocks, arrows, records, Lorentz behaviour, and shareability within specified realizations |

The layers are related by adding assumptions and testing consequences, not by automatic
deduction. The operational core is a proposed basis for this research programme; it is
not a new definition of time, a uniquely minimal axiom system, or evidence that
operational fit uniquely fixes ontology. For a first reading, start with the operational
core, then the working spec, then the two experiment write-ups. Causal accessibility supplies model-relative reachability; calibrated clocks supply duration. Entropy and “forgetting” are candidate models of arrow and record asymmetry, not the foundational ordering primitive.

## Bend 2 formal slice

[`formal/bend2-zero-coupling/`](formal/bend2-zero-coupling/README.md) contains a
checked proof of access-scoped transcript equivalence in a finite classical
zero-coupling model, including adaptive R-only procedures. It records the
assumptions and the boundary to the quantum simulation. From that directory,
`bend PROOF.bend` checks the laws with Bend 2.0.16.

The first simulation tests one falsifiable claim from the quantum realization in "the
Cut spec" (Prop 7.1): *an observer
built from the same anisotropic couplings it measures with cannot detect the
substrate's anisotropy through any dimensionless internal experiment.* The framework
spec is `docs/cut_spec.tex` (§9 states the claim and this experiment's result); the
verdict rules and outcome are in `docs/results-writeup.md`.

**Second experiment (Prop 7.2 candidate):** historically named orientation-gauge test on a two-sided
fermion TFD — can an observer inside side R detect a flip of side L's time direction,
or a swap of its mirror partner for a scrambled purification, at zero cross-cut
coupling? Spec: `orientation-test.md`; pre-registration:
`plans/260720-2257-orientation-gauge-sim/plan.md`; verdict (both claims HOLD at float
precision, crossover law D ∝ g² / g found): `docs/results-writeup-orientation.md`.
The null is scoped to the declared zero-coupling setup and side-R access class; it is not
an ontological identity or a universal gauge redundancy.

**Targeted follow-up (2026-09-22):** a denser sweep retains the original battery's
quadratic orientation response; adding a declared local pair reference gives a linear
response. Finite-trial detection, scramble/window sensitivity, and larger-lattice
spreading checks are reported separately in
[`docs/results-writeup-followup.md`](docs/results-writeup-followup.md).
The original result files and embedded web data are preserved.

```bash
.venv/bin/python3 src/validate-orientation-gates.py        # gates G0–G9 must ALL pass
.venv/bin/python3 src/run-orientation-gauge-experiment.py  # → results/results-orientation.json + plots
.venv/bin/python3 src/validate-orientation-artifacts.py    # result/doc/web consistency checks
.venv/bin/python3 src/export-web-orientation-data.py       # → web/assets/orientation-experiment-data.js
```

## Model

2D anisotropic tight-binding free fermions (`Jx ≠ Jy`), periodic boundaries.
All dynamics are **exact** (single-particle propagator via FFT — no Trotter error).

- **Model-level control** (historically called “god's-eye”): Lieb-Robinson cone
  velocities in bare lattice units → `A_god = vx/vy`.
- **Endogenous observer**: rod = impurity bound-state width per axis (static binding
  length, not site counting, not signal-defined); clock = beat period of a small
  cavity's two lowest modes. Speeds measured only in rods-per-tick → `A_endo`.
- **Dimensionless battery**: front-speed ratio, endogenous wavepacket ratio, spreading
  (birefringence) anisotropy — each calibrated on model-level data where it must fire.
- **Tuning sweep**: impurity strength ε sets rod size ξ; ξ→∞ = approach to the
  continuum (Gaussian RG fixed point).

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-lock.txt
.venv/bin/python3 src/validate-physics-sanity-checks.py   # gates must ALL pass first
.venv/bin/python3 src/run-ruler-cancellation-experiment.py # → results/ (JSON + plots)
```

The ruler driver now enforces its preflight gates and aborts on failed calibration.
Both original drivers include source hashes, dependency versions, and gate logs in
newly generated result files. The dependency lock records the follow-up environment
(Python 3.14.6); it does not retroactively specify the original July environment.

To inspect or reproduce the follow-up:

```bash
.venv/bin/python3 src/validate-followup-gates.py
.venv/bin/python3 src/validate-followup-artifacts.py
# A new output directory is required; existing results are never overwritten.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python3 \
  src/run-targeted-followups.py --output results/followup-reproduction
.venv/bin/python3 src/validate-followup-artifacts.py --output results/followup-reproduction
```

The [study plan](docs/followup-study-plan.md) fixes the access assumptions, grids,
error model, and stop conditions. The
[manifest](results/followup-20260922/manifest.json) and
[figure](results/followup-20260922/followup-summary.png) accompany the raw JSON data.

## Interactive web bundle

`web/` is a self-contained static site for exploring the framework and the experiment —
no build step, no external dependencies, works from disk or any static host
(e.g. GitHub Pages: serve the `web/` directory). Light/dark theme aware.

- `index.html` — overview: three-layer map, status-tag legend, and experiment links
- `operational-core.html` — the public operational-core module, including OC-A1–A4,
  OC-R1–R3, time-task split, examples, and assumption ledger
- `the-cut-game.html` — an interactive guide (`game-spec.md`): six levels with a Model
  view ⇄ Observer view toggle; Levels 1–4 run the live exact simulations, Level 5
  replays measured data, and the guide states the unresolved inputs and falsified claim
- `framework-explorer.html` — the full spec as claim cards, filterable by epistemic tag
- `time-as-forgetting-lab.html` — live 1D fermion chain: entanglement dynamics and a
  candidate entropic orientation variable after a quench (exact)
- `lieb-robinson-cone-lab.html` — live 2D anisotropic lattice: the elliptical cone (exact)
- `ruler-cancellation-verdict-lab.html` — the experiment's measured data, interactive
- `orientation-gauge-lab.html` — scoped orientation null and crossover data, interactive
- `followup-study.html` — measurement access, finite-trial detection, and convergence results

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
- `src/validate-orientation-artifacts.py` — fast result/doc/web consistency checks
- `src/generate-orientation-plots.py` — result plots

Kebab-case module files are loaded via an importlib bootstrap in the driver scripts.
