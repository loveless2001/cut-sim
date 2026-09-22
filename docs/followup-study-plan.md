# Targeted follow-up study — 2026-09-22

This is a prospective specification for the follow-up runs, informed by the original
results and the exploratory review. It is not an independent or blinded
preregistration. The pair location was suggested by an exploratory N=64 calculation;
the follow-up freezes it and does not optimize it separately for each coupling.
The original result files, thresholds, and verdicts remain historical artifacts.

## Questions and fixed design

1. **Access dependence.** Compare the existing orientation battery with a pair-sensitive
   side-R detector. Use mirror TFD states, N=64/128/256, beta=1/4, g=0 and
   {1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2}. Measure the pair at offsets
   {0,-13} rods, rounded to {0,-12} sites, at {0.25,0.5,1} reference ticks.
   The reference tick is calibrated at g=0 with the existing prepared cavity clock;
   it is fixed across compared variants. Both pair quadratures are retained, with
   phase pi/2 fixed for the finite-trial experiment. N=64 is a finite-size stress
   case, not a thermodynamic-limit claim. Signed-g checks at +/-1e-4 test odd/even
   response; g=0 remains the null control.
2. **Crossover robustness.** Recompute every original battery item on the seven
   positive couplings and g=0 for (N,beta)=(256,1),(128,1),(128,4), with the original
   scramble seed 20260720. At (128,1), also use seeds 20260721 and 20260722.
   Compare clock calibration horizons 100/200/300 at (128,1), g=0,1e-3,1e-2,
   retaining the original sampling interval. No battery item is removed.
   Fit each item and the maximum separately; retain full-window, low-four,
   high-four, and leave-one-endpoint-out fits. Exclude distances <=1e-10 explicitly
   as numerically unresolved. Report slope-window spread; <=0.1 is the declared
   stability criterion, not a statistical confidence interval.
3. **Finite-trial detector.** Each trial uses a fresh preparation and a fresh local
   reference with levels |0>,|2>, coherence <b†>=v exp(-i phi)/2, v=0,0.5,1.
   It shares a preparation phase with the TFD. This is additional apparatus/access,
   not something derivable from the original number-conserving local controls.
   With A=c_i c_j, Y=A b† + A† b conserves total particle number and has norm 1.
   The binary POVM E_±=(I±Y)/2 gives p(+)=1/2+v Re(exp(-i phi) F_ij)/2.
   Readout flips the recorded bit independently with probability eta=0 or 0.05.
   Compare orientations with equal priors, known calibrated probabilities, and
   budgets 10^3,10^5,10^7,10^8 independent trials. Compute the exact binomial
   likelihood-test error and simulate 4096 count records per hypothesis using seed
   20260922. This is an ideal apparatus benchmark: phase preparation, resetting,
   and unknown-parameter calibration costs are not included in the trial count.
   Use (N,beta)=(128,1), g=0,1e-4,1e-3,1e-2 and all three durations.
   No-reference (v=0) and g=0 controls must give error 1/2.
4. **Spreading convergence.** Revisit the largest retained r=2 and r=3 packets at
   the original lattice size, twice that size, and four times that size. Keep rods
   and initial packets fixed. Compare the old 40-point stopping grid with a bracketed
   first crossing of sqrt(2) growth in either measured initial RMS width. Use exact
   separable 1D FFT evolution, cross-checked against the existing 2D engine.
   Also recompute each bound-state rod on 1024/2048/4096 sites using separable
   dispersion sums, and repeat the refined packet with converged rods.
   Convergence requires |delta R|<1e-4, relative stop-time change<1e-4, and
   quarter-lattice tail mass<1e-4 on the larger of the final two sizes. Failure is
   reported without automatically enlarging the sweep.
5. **Existing-data scaling.** Fit |A_wp-1| versus xi for r>1, xi>=2 and no UV-capped
   packets. Store points and fit-window sensitivity. These fits describe existing
   data and are not independent new evidence or a proof of an RG exponent.

## Numerical gates, artifacts, and stop conditions

Run both existing numerical gate suites and the orientation artifact check before
the follow-up. Additional gates compare the pair/reference POVM with explicit small
Fock-space operators, the binomial test with exhaustive small-count enumeration,
and separable evolution/bound states with the existing 2D algorithms. They also
exercise abort-before-write behavior for failed ruler calibration and gate failures.

Write separate JSON results plus a manifest under a new output directory. Refuse to
overwrite an existing output directory. Record the UTC start/end times, Git revision
and dirty state, dependency versions, thread settings, source/input/plan SHA-256
hashes, gate logs, and output hashes. Hashes, not a clean Git assumption, identify the
executed source. Verify source/input hashes again before declaring completion.
Do not mutate either original result JSON. Numerical-gate failure stops the run;
an unstable exponent, finite-size discrepancy, or poor detection rate is a reportable
result, not a reason to tune the experiment. No interacting-model, GPU, or external
publication work is included.
