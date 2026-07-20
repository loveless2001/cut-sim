"""God's-eye discriminators — battery calibration; may use L data and bare units.

ge-MI          : I(L_w : R_w)(t) for aligned 32-site windows — must differ O+ vs O-.
ge-cross-phase : anomalous cross correlator K(x,t) = <c_{L,x}(t) c_{R,c}(0)>.
                 (The number-conserving <c+_L c_R> two-time correlator vanishes
                 identically for the TFD — G_LR(0) = 0 — so the phase structure the
                 spec asks for lives in the anomalous channel; documented in plan.)
ge-complement  : distance between G_LL(0) of mirror vs scrambled purification.
Fire threshold theta_fire = 1e-6 (pre-registered; expected magnitudes O(0.1-1)).
"""
import numpy as np
import sys

ts = sys.modules["tfd_state"]
bt = sys.modules["internal_battery"]

THETA_FIRE = 1e-6
GE_TIMES = np.linspace(0.0, 40.0, 81)
MI_HALF = 16                 # 32-site windows


def mi_windows(N):
    c = N // 2
    w = (c + np.arange(-MI_HALF, MI_HALF)) % N
    return w, N + w


def mutual_information_curve(evo, N, times=GE_TIMES):
    """I(L_w : R_w)(t) from the union (G, F) blocks (includes cross F)."""
    Lw, Rw = mi_windows(N)
    union = np.concatenate([Lw, Rw])
    nL = len(Lw)
    out = []
    for t in times:
        GU, FU = evo.g_block(t, union), evo.f_block(t, union)
        allix = np.arange(len(union))
        S_L = ts.entropy(GU, FU, allix[:nL])
        S_R = ts.entropy(GU, FU, allix[nL:])
        S_U = ts.entropy(GU, FU, allix)
        out.append(S_L + S_R - S_U)
    return np.array(out)


def cross_phase_correlator(evo, N, times=GE_TIMES):
    """K(x, t) on the L window rows against the R window centre."""
    Lw, _ = mi_windows(N)
    _, _, K = evo.two_time(times, Lw, N + N // 2)
    return K


def orientation_discriminators(evo_plus, evo_minus, N):
    """G7 pair: both must fire on O+ vs O- at g = 0."""
    d_mi = bt.distance(mutual_information_curve(evo_plus, N),
                       mutual_information_curve(evo_minus, N))
    d_xp = bt.distance(cross_phase_correlator(evo_plus, N),
                       cross_phase_correlator(evo_minus, N))
    return {"ge-mi": {"d": d_mi, "fires": d_mi > THETA_FIRE},
            "ge-cross-phase": {"d": d_xp, "fires": d_xp > THETA_FIRE}}


def complement_discriminator(state_mirror, state_scrambled):
    """Any L-sector observable separating mirror from scrambled: use G_LL(0)."""
    N = state_mirror["N"]
    d = bt.distance(state_mirror["G"][:N, :N], state_scrambled["G"][:N, :N])
    return {"d": d, "fires": d > THETA_FIRE}
