"""Measurements and inference for the access/convergence follow-up.

All pair probabilities refer to the additional local pair reference specified in
docs/followup-study-plan.md. They are not measurements in the original access class.
"""
import numpy as np
from scipy.optimize import brentq
from scipy.stats import binom


def reference_probability(pair_correlation, phase=np.pi / 2, visibility=1.0,
                          readout_flip=0.0):
    """POVM (I +/- Y)/2, Y=c_i c_j b† + h.c., <b†>=v exp(-i phase)/2."""
    if not 0 <= visibility <= 1 or not 0 <= readout_flip <= 0.5:
        raise ValueError("Invalid reference visibility or readout flip probability")
    mean = visibility * np.real(np.exp(-1j * phase) * pair_correlation)
    probability = 0.5 * (1.0 + mean)
    if not np.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("Unphysical measurement probability")
    return float(readout_flip + (1.0 - 2.0 * readout_flip) * probability)


def binomial_discrimination(p0, p1, trials, rng=None, replicates=4096):
    """Equal-prior minimum error for two known Bernoulli hypotheses.

    The sufficient recorded transcript is the count of '+' outcomes. The classifier
    is fixed from calibrated probabilities, never trained on its evaluation records.
    """
    if not all(np.isfinite(p) and 0 <= p <= 1 for p in (p0, p1)) or trials < 1:
        raise ValueError("Invalid Bernoulli experiment")
    if int(trials) != trials:
        raise ValueError("The trial count must be integral")
    trials = int(trials)
    lo, hi = sorted((p0, p1))
    if lo == hi:
        return {"exact_error": 0.5, "simulated_error": 0.5 if rng is not None else None,
                "simulation_se": 0.0 if rng is not None else None,
                "decision": "tie: always choose hypothesis 0", "cut_count": None}
    if lo == 0:
        cut = 0
    elif hi == 1:
        cut = trials - 1
    else:
        delta = hi - lo
        log_plus = np.log1p(delta / lo)
        log_minus = np.log1p(-delta / (1.0 - lo))
        cut = int(np.floor(-trials * log_minus / (log_plus - log_minus)))
    false_high = float(binom.sf(cut, trials, lo))
    false_low = float(binom.cdf(cut, trials, hi))
    exact = 0.5 * (false_high + false_low)
    observed = se = None
    if rng is not None:
        k_lo = rng.binomial(trials, lo, size=replicates)
        k_hi = rng.binomial(trials, hi, size=replicates)
        observed = float(0.5 * (np.mean(k_lo > cut) + np.mean(k_hi <= cut)))
        se = float(0.5 * np.sqrt((false_high * (1 - false_high)
                                 + false_low * (1 - false_low)) / replicates))
    return {"exact_error": exact, "simulated_error": observed, "simulation_se": se,
            "decision": "choose higher-p hypothesis iff count > cut_count",
            "higher_p_hypothesis": 0 if p0 > p1 else 1, "cut_count": cut}


def power_fit(x, y, floor=1e-10):
    """Descriptive log-log fits with explicit numerical censoring and window checks."""
    points = sorted((float(a), float(b)) for a, b in zip(x, y) if a > 0)
    kept = [(a, b) for a, b in points if np.isfinite(b) and b > floor]
    out = {"floor": floor, "points": points, "resolved_points": kept,
           "excluded_points": [(a, b) for a, b in points if not np.isfinite(b) or b <= floor]}
    if len(kept) < 4:
        return out | {"status": "INSUFFICIENT_RESOLVED_POINTS", "windows": {}}
    selections = {"all": kept, "omit_smallest": kept[1:], "omit_largest": kept[:-1],
                  "low_four": kept[:4], "high_four": kept[-4:]}
    fits = {}
    for name, window in selections.items():
        xx, yy = np.log(np.array(window).T)
        slope, intercept = np.polyfit(xx, yy, 1)
        fits[name] = {"slope": float(slope), "intercept": float(intercept),
                      "n": len(window), "x_range": [window[0][0], window[-1][0]],
                      "log_residual_rms": float(np.sqrt(np.mean((yy-slope*xx-intercept)**2)))}
    spread = max(f["slope"] for f in fits.values()) - min(f["slope"] for f in fits.values())
    return out | {"windows": fits, "slope_window_spread": spread,
                  "status": "STABLE" if spread <= 0.1 else "WINDOW_SENSITIVE"}


def packet_axes(L, Jx, Jy, wx, wy):
    """Exact factorization of the existing separable Gaussian and lattice Hamiltonian."""
    x = np.fft.fftfreq(L, d=1.0 / L)
    k = 2 * np.pi * np.fft.fftfreq(L)
    axes = []
    for J, width in ((Jx, wx), (Jy, wy)):
        psi = np.exp(-x*x / (4*width*width))
        psi /= np.linalg.norm(psi)
        axes.append((np.fft.fft(psi), -2*J*np.cos(k)))
    return x, axes


def packet_moments(packet, t):
    x, axes = packet
    widths, tails = [], []
    for amplitude, energy in axes:
        probability = np.abs(np.fft.ifft(amplitude * np.exp(-1j*energy*t)))**2
        probability /= probability.sum()
        mean = np.dot(probability, x)
        widths.append(float(np.sqrt(max(np.dot(probability, x*x)-mean*mean, 0))))
        tails.append(float(probability[np.abs(x) >= len(x)/4].sum()))
    return widths[0], widths[1], max(tails)


def spreading_measurement(L, Jx, Jy, rod_x, rod_y, *, samples=40, refine=False):
    wx, wy = 3*rod_x, 3*rod_y
    packet = packet_axes(L, Jx, Jy, wx, wy)
    sx0, sy0, _ = packet_moments(packet, 0)
    horizon = 8*max(wx, wy)*min(wx, wy)/min(Jx, Jy)
    # The old grid uses nominal initial widths. The refined procedure uses the
    # measured initial widths, whose finite-volume discrepancy is also recorded.
    target_x, target_y = (sx0, sy0) if refine else (wx, wy)

    def crossing(t):
        sx, sy, _ = packet_moments(packet, t)
        return max(sx/target_x, sy/target_y) - np.sqrt(2)

    lower = 0.0
    for upper in np.linspace(horizon/samples, horizon, samples):
        if crossing(upper) >= 0:
            t = brentq(crossing, lower, upper, xtol=1e-8) if refine else upper
            break
        lower = upper
    else:
        raise RuntimeError("Packet did not reach the declared growth within the horizon")
    sx, sy, tail = packet_moments(packet, t)
    return {"L": L, "samples": samples, "refined": refine, "rod_x": rod_x, "rod_y": rod_y,
            "R": (sx/rod_x)/(sy/rod_y), "stopped_at_t": float(t), "tail_mass": tail,
            "initial_widths": [sx0, sy0], "nominal_widths": [wx, wy],
            "final_widths": [sx, sy]}


def bound_state_rods(L, Jx, Jy, eps, chunk=128):
    """Same finite-lattice Green function as the 2D engine, with bounded memory.

    Parseval along the unobserved axis yields each marginal from one-axis FFTs.
    This avoids storing a full 4096-square complex wavefunction.
    """
    k = 2*np.pi*np.fft.fftfreq(L)
    dx, dy = 2*Jx*(1-np.cos(k)), 2*Jy*(1-np.cos(k))

    def condition(binding):
        total = 0.0
        for start in range(0, L, chunk):
            total += np.sum(1/(dx[:, None] + dy[None, start:start+chunk] + binding))
        return 1 - eps*total/(L*L)

    binding = brentq(condition, 1e-12, eps+1, xtol=1e-14, rtol=1e-15)
    marginals = []
    for first, second in ((dx, dy), (dy, dx)):
        marginal = np.zeros(L)
        for start in range(0, L, chunk):
            kernel = 1/(first[:, None] + second[None, start:start+chunk] + binding)
            marginal += np.sum(np.abs(np.fft.ifft(kernel, axis=0))**2, axis=1)
        marginals.append(marginal/marginal.sum())
    x = np.fft.fftfreq(L, d=1.0/L)
    widths = [float(np.sqrt(np.dot(p, x*x)-np.dot(p, x)**2)) for p in marginals]
    tail = max(float(p[np.abs(x) >= L/4].sum()) for p in marginals)
    return {"L": L, "rod_x": widths[0], "rod_y": widths[1],
            "binding_energy": float(binding), "tail_mass": tail}
