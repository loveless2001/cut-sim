"""Independent measurement checks and abort-before-write regressions."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.linalg import expm
from scipy.stats import binom

SRC = Path(__file__).parent


def load(file, name):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SRC / file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


driver = load("run-orientation-gauge-experiment.py", "orientation_driver")
measure = load("followup-measurements.py", "followup_measurements")
lm = load("lattice-model-exact-fft-evolution.py", "lattice_model")


class FollowupGates(unittest.TestCase):
    def test_pair_reference_povm_against_fock_space(self):
        gates = load("validate-orientation-gates.py", "orientation_gates")
        N = 3
        st = driver.ts.build_tfd(N, 0.7)
        C = gates.fock_operators(2*N)
        psi = np.eye(2**(2*N))[:, 0]
        for a in range(N):
            cl = sum(st["phi"][x, a]*C[x].conj().T for x in range(N))
            cr = sum(st["phi"][x, a]*C[N+x].conj().T for x in range(N))
            psi = np.sqrt(1-st["n"][a])*psi + np.sqrt(st["n"][a])*(cr @ cl @ psi)
        A = C[N] @ C[N+2]
        b = np.array([[0., 1.], [0., 0.]])
        Y = np.kron(A, b.T) + np.kron(A.conj().T, b)
        Eplus = (np.eye(Y.shape[0])+Y)/2
        self.assertGreaterEqual(np.linalg.eigvalsh(Eplus).min(), -1e-14)
        self.assertLessEqual(np.linalg.eigvalsh(Eplus).max(), 1+1e-14)
        # Pair exchange preserves particle number of sample plus local reference.
        number = sum(c.conj().T @ c for c in C)
        total = np.kron(number, np.eye(2)) + np.kron(np.eye(len(psi)), np.diag([0., 2.]))
        np.testing.assert_allclose(total @ Y, Y @ total, atol=1e-13)
        for s in (-1, 1):
            H = driver.oe.build_variant_h1(N, s, 0.2, w=2)
            Hmb = sum(H[i,j]*(C[i].conj().T @ C[j]) for i in range(2*N) for j in range(2*N))
            psit = expm(-1j*Hmb*1.3) @ psi
            F = driver.oe.VariantEvolution(H, st["G"], st["F"]).f_block(1.3, [N, N+2])[0,1]
            for phase in (0., np.pi/2):
                for v in (0., 0.5, 1.):
                    ref = np.array([[1., v*np.exp(-1j*phase)], [v*np.exp(1j*phase), 1.]])/2
                    rho = np.kron(np.outer(psit, psit.conj()), ref)
                    p = float(np.real(np.trace(rho @ Eplus)))
                    self.assertAlmostEqual(p, measure.reference_probability(F, phase, v), places=12)
                    self.assertAlmostEqual(0.05+0.9*p,
                        measure.reference_probability(F, phase, v, 0.05), places=12)

    def test_binomial_rule_against_exhaustive_counts(self):
        for n in (1, 2, 17):
            for p0, p1 in ((0.2, 0.7), (0.7, 0.2), (0.5, 0.5), (0., 0.6), (0.4, 1.), (0., 1.)):
                k = np.arange(n+1)
                exact = 0.5*np.minimum(binom.pmf(k,n,p0), binom.pmf(k,n,p1)).sum()
                self.assertAlmostEqual(exact, measure.binomial_discrimination(p0,p1,n)["exact_error"], places=12)
        self.assertEqual(measure.reference_probability(0.1j, visibility=0), 0.5)

    def test_separable_packet_against_2d_fft(self):
        L, Jx, Jy, wx, wy = 128, 2., 1., 3.2, 5.1
        packet = measure.packet_axes(L,Jx,Jy,wx,wy)
        psi = lm.gaussian_packet(L,0,0,wx,wy)
        E = lm.dispersion(L,Jx,Jy)
        for t in (0., 5., 20.):
            reference = lm.rms_widths(np.abs(lm.evolve(psi,E,t))**2)
            np.testing.assert_allclose(measure.packet_moments(packet,t), reference, atol=1e-12)

    def test_chunked_rods_against_2d_green_function(self):
        for Jx, Jy in ((1.,1.), (3.,1.)):
            psi, _, binding = lm.impurity_bound_state(64,Jx,Jy,4.)
            rx, ry, tail = lm.rms_widths(psi**2)
            result = measure.bound_state_rods(64,Jx,Jy,4.,chunk=13)
            np.testing.assert_allclose([result[k] for k in ("rod_x","rod_y","tail_mass","binding_energy")],
                                       [rx,ry,tail,binding], rtol=1e-10, atol=1e-12)

    def test_refined_stop_hits_measured_growth(self):
        result = measure.spreading_measurement(256,2.,1.,4.,3.,refine=True)
        growth = max(a/b for a,b in zip(result["final_widths"],result["initial_widths"]))
        self.assertAlmostEqual(growth,np.sqrt(2),places=10)

    def test_ruler_calibration_failure_stops_before_sweep(self):
        # Legacy drivers use the same 'gods_eye' module name for different files.
        with patch.dict(sys.modules):
            sys.modules.pop("gods_eye", None)
            ruler = load("run-ruler-cancellation-experiment.py", "ruler_for_test")
            with patch.object(ruler.ge,"measure_cone",return_value={"vx":4.,"vy":2.,"sigma_vx":.01,"sigma_vy":.01}), \
                 patch.object(ruler.eo,"wavepacket_com_velocity",return_value=(1.,.01)), \
                 patch.object(ruler.bt,"calibrate_battery",return_value={"calibration_pass":False}), \
                 patch.object(ruler.eo,"make_observer") as observer:
                with self.assertRaisesRegex(RuntimeError,"calibration failed"):
                    ruler.run_ratio(2.,False)
                observer.assert_not_called()

    def test_failed_preflight_cannot_write_experiment_outputs(self):
        with patch.dict(sys.modules):
            sys.modules.pop("gods_eye", None)
            ruler = load("run-ruler-cancellation-experiment.py", "ruler_for_preflight")
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory)/"must-not-exist"
                for target in (ruler, driver):
                    with patch.object(target,"RESULTS",output), \
                         patch.object(target.support,"provenance",return_value={}), \
                         patch.object(target.support,"run_gate",side_effect=RuntimeError("gate failed")):
                        with self.assertRaisesRegex(RuntimeError,"gate failed"):
                            target.main()
                        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
