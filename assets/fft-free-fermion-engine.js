// Exact free-fermion dynamics in the browser — same physics as the python code in src/.
// No approximations: 2D quench uses the exact FFT propagator psi(t)=IFFT[e^{-iE(k)t}];
// the 1D chain uses the analytic open-boundary eigenmodes and correlation-matrix
// evolution, with entanglement entropy from the reduced correlation spectrum.

// ---------- radix-2 complex FFT (in place, n = power of 2) ----------
function fftRadix2(re, im, invert) {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) {           // bit reversal
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
  }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = (invert ? 2 : -2) * Math.PI / len;
    const wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) {
      let cwr = 1, cwi = 0;
      for (let k = 0; k < len / 2; k++) {
        const a = i + k, b = i + k + len / 2;
        const tr = re[b] * cwr - im[b] * cwi, ti = re[b] * cwi + im[b] * cwr;
        re[b] = re[a] - tr; im[b] = im[a] - ti;
        re[a] += tr; im[a] += ti;
        const nwr = cwr * wr - cwi * wi; cwi = cwr * wi + cwi * wr; cwr = nwr;
      }
    }
  }
  if (invert) for (let i = 0; i < n; i++) { re[i] /= n; im[i] /= n; }
}

// 2D FFT on flattened L*L arrays (row-major)
function fft2d(re, im, L, invert) {
  const rr = new Float64Array(L), ri = new Float64Array(L);
  for (let y = 0; y < L; y++) {                   // rows
    const off = y * L;
    fftRadix2(re.subarray(off, off + L), im.subarray(off, off + L), invert);
  }
  for (let x = 0; x < L; x++) {                   // columns
    for (let y = 0; y < L; y++) { rr[y] = re[y * L + x]; ri[y] = im[y * L + x]; }
    fftRadix2(rr, ri, invert);
    for (let y = 0; y < L; y++) { re[y * L + x] = rr[y]; im[y * L + x] = ri[y]; }
  }
}

// ---------- 2D anisotropic quench (delta source at origin, PBC) ----------
// E(k) = -2Jx cos kx - 2Jy cos ky ; FFT of a delta is 1, so psi(t) = IFFT[e^{-iEt}].
class ConeQuenchSim {
  constructor(L, Jx, Jy) {
    this.L = L; this.setCouplings(Jx, Jy);
    this.re = new Float64Array(L * L); this.im = new Float64Array(L * L);
  }
  setCouplings(Jx, Jy) {
    this.Jx = Jx; this.Jy = Jy;
    const L = this.L, E = new Float64Array(L * L);
    for (let x = 0; x < L; x++) {
      const cx = -2 * Jx * Math.cos(2 * Math.PI * x / L);
      for (let y = 0; y < L; y++) E[x * L + y] = cx - 2 * Jy * Math.cos(2 * Math.PI * y / L);
    }
    this.E = E;
  }
  // exact |psi(x,t)|^2, recomputed from t directly (no error accumulation)
  probability(t) {
    const { L, E, re, im } = this;
    for (let i = 0; i < L * L; i++) { re[i] = Math.cos(E[i] * t); im[i] = -Math.sin(E[i] * t); }
    fft2d(re, im, L, true);
    const P = new Float64Array(L * L);
    for (let i = 0; i < L * L; i++) P[i] = re[i] * re[i] + im[i] * im[i];
    return P;
  }
}

// ---------- 1D open chain: correlation-matrix dynamics + entanglement entropy ----
// Modes: phi_m(n) = sqrt(2/(N+1)) sin(pi m n/(N+1)), E_m = -2J cos(pi m/(N+1)).
class ChainEntropySim {
  constructor(N) {
    this.N = N;
    const phi = new Float64Array(N * N), E = new Float64Array(N);
    const norm = Math.sqrt(2 / (N + 1));
    for (let m = 0; m < N; m++) {
      E[m] = -2 * Math.cos(Math.PI * (m + 1) / (N + 1));
      for (let n = 0; n < N; n++) phi[m * N + n] = norm * Math.sin(Math.PI * (m + 1) * (n + 1) / (N + 1));
    }
    this.phi = phi; this.E = E;
    // Neel-type quench: occupy every second site. A = phi C0 phi^T (real, N x N)
    const A = new Float64Array(N * N);
    for (let m = 0; m < N; m++) for (let l = 0; l < N; l++) {
      let s = 0;
      for (let n = 0; n < N; n += 2) s += phi[m * N + n] * phi[l * N + n];
      A[m * N + l] = s;
    }
    this.A = A;
  }
  // C(t) = phi^T . (A_{ml} e^{-i(E_m-E_l)t}) . phi   — exact at any t
  correlationMatrix(t) {
    const { N, phi, E, A } = this;
    const Mr = new Float64Array(N * N), Mi = new Float64Array(N * N);
    for (let m = 0; m < N; m++) for (let l = 0; l < N; l++) {
      const th = -(E[m] - E[l]) * t, a = A[m * N + l];
      Mr[m * N + l] = a * Math.cos(th); Mi[m * N + l] = a * Math.sin(th);
    }
    // T = M . phi  (N x N complex), then C = phi^T . T
    const Tr = new Float64Array(N * N), Ti = new Float64Array(N * N);
    for (let m = 0; m < N; m++) for (let j = 0; j < N; j++) {
      let sr = 0, si = 0;
      for (let l = 0; l < N; l++) { sr += Mr[m * N + l] * phi[l * N + j]; si += Mi[m * N + l] * phi[l * N + j]; }
      Tr[m * N + j] = sr; Ti[m * N + j] = si;
    }
    const Cr = new Float64Array(N * N), Ci = new Float64Array(N * N);
    for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
      let sr = 0, si = 0;
      for (let m = 0; m < N; m++) { sr += phi[m * N + i] * Tr[m * N + j]; si += phi[m * N + i] * Ti[m * N + j]; }
      Cr[i * N + j] = sr; Ci[i * N + j] = si;
    }
    return { Cr, Ci };
  }
  // Entanglement entropy of sites [0, len) — eigenvalues of the reduced correlation
  // block via real-symmetric embedding [[X,-Y],[Y,X]] (eigenvalues come in pairs).
  entropy(t, len) {
    const { Cr, Ci } = this.correlationMatrix(t);
    const N = this.N, n = 2 * len, S = new Float64Array(n * n);
    for (let i = 0; i < len; i++) for (let j = 0; j < len; j++) {
      const x = Cr[i * N + j], y = Ci[i * N + j];
      S[i * n + j] = x; S[(i + len) * n + (j + len)] = x;
      S[i * n + (j + len)] = -y; S[(i + len) * n + j] = y;
    }
    const ev = jacobiEigenvaluesSymmetric(S, n);
    let s = 0;
    for (const lRaw of ev) {
      const l = Math.min(1 - 1e-12, Math.max(1e-12, lRaw));
      s += -(l * Math.log(l) + (1 - l) * Math.log(1 - l));
    }
    return s / 2;                                  // embedding doubles each eigenvalue
  }
}

// cyclic Jacobi eigenvalue algorithm for a real symmetric matrix (values only)
function jacobiEigenvaluesSymmetric(M, n) {
  const a = Float64Array.from(M);
  for (let sweep = 0; sweep < 30; sweep++) {
    let off = 0;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += a[p * n + q] ** 2;
    if (off < 1e-22) break;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
      const apq = a[p * n + q];
      if (Math.abs(apq) < 1e-14) continue;
      const theta = (a[q * n + q] - a[p * n + p]) / (2 * apq);
      const tSign = theta >= 0 ? 1 : -1;
      const tVal = tSign / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
      const c = 1 / Math.sqrt(tVal * tVal + 1), s = tVal * c;
      for (let k = 0; k < n; k++) {
        const akp = a[k * n + p], akq = a[k * n + q];
        a[k * n + p] = c * akp - s * akq; a[k * n + q] = s * akp + c * akq;
      }
      for (let k = 0; k < n; k++) {
        const apk = a[p * n + k], aqk = a[q * n + k];
        a[p * n + k] = c * apk - s * aqk; a[q * n + k] = s * apk + c * aqk;
      }
    }
  }
  const ev = [];
  for (let i = 0; i < n; i++) ev.push(a[i * n + i]);
  return ev;
}
