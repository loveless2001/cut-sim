// Level 5 — "The observer that can't see straight" (the centerpiece): god's-eye shows
// the live exact anisotropic cone; in cut view the player measures with rods+clock made
// of the substrate. Every measured number is log-interpolated REAL data from
// results/results.json (via experiment-data.js) — the one level that must not be faked.
(() => {
  const L = 128, SCALE = 3;
  const byR = {}; CUT_EXPERIMENT_DATA.ratios.forEach(d => { byR[d.r] = d; });
  let cone, coneT = 0, d = byR[2];
  let frac = 0.4, measuring = false, tickPhase = 0;
  const flags = { front: false, wpHigh: false, compared: false, batt: false };
  const notes = [];                                  // {xi, kind, A}
  const $ = id => document.getElementById(id);
  const css = k => CutGame.css(k);

  // log-xi interpolation between measured points (same rule as the Verdict Lab)
  function interp(arr) {
    const lx = d.xi.map(Math.log);
    const x = lx[0] + frac * (lx[lx.length - 1] - lx[0]);
    let i = 0; while (i < lx.length - 2 && lx[i + 1] < x) i++;
    const u = (x - lx[i]) / (lx[i + 1] - lx[i]);
    return { v: arr[i] + u * (arr[i + 1] - arr[i]), xi: Math.exp(x), i: u < .5 ? i : i + 1 };
  }

  function init() {
    cone = new ConeQuenchSim(L, 2, 1);
    $("l5-r").addEventListener("change", () => {
      d = byR[+$("l5-r").value];
      cone.setCouplings(d.r, 1); coneT = 0;
      notes.length = 0; renderNotebook(); refresh();
    });
    $("l5-xi").addEventListener("input", () => { frac = $("l5-xi").value / 100; refresh(); });
    $("l5-front").addEventListener("click", () => measure("front"));
    $("l5-wp").addEventListener("click", () => measure("wavepacket"));
    $("l5-batt").addEventListener("click", battery);
    refresh();
  }

  function measure(kind) {
    if (measuring) return;
    measuring = true;
    $("l5-out").textContent = kind === "front"
      ? "Timing your fastest signal along both axes, in rods per tick…"
      : "Preparing a slow wavepacket with wavelength set by your own rods… timing…";
    setTimeout(() => {
      measuring = false;
      const m = interp(kind === "front" ? d.Afront : d.Awp);
      notes.push({ xi: m.xi, kind, A: m.v });
      const sees = Math.abs(m.v - 1) > 0.02;
      $("l5-out").textContent = `Result: anisotropy you measure A = ${m.v.toFixed(4)} — ` +
        (sees ? "your world has a direction in it. But is that the substrate itself, or the substrate through your rulers? You can't tell from in here — compare in god's-eye."
              : "isotropic within your 2% rule. On this instrument, your world looks the same in every direction.");
      if (kind === "front") flags.front = true;
      if (kind === "wavepacket" && frac >= 0.85 && Math.abs(m.v - 1) < 0.005) flags.wpHigh = true;
      renderNotebook(); refresh(); quest();
    }, 900);
  }

  function battery() {
    const i = interp(d.Afront).i;
    flags.batt = true;
    $("l5-out").textContent = d.batteryDetected[i]
      ? "BATTERY (backend, pre-registered rule |R−1| > max(2%, 5σ)): DETECTS the substrate axis at the nearest measured point — driven by the front-ratio test. Even where your slow instruments read perfect isotropy, your own light-front betrays the axis. You cannot hide it."
      : "BATTERY: null at the nearest measured point — no dimensionless test fires here. Slide ξ and try again; the verdict is scale-dependent.";
    quest(); refresh();
  }

  function quest() {
    const q = $("l5-quest");
    if (!flags.front && !notes.length) return;
    if (!flags.compared) q.innerHTML = "You have a reading. Is it the substrate's true shape? That comparison needs the substrate's true shape — toggle to <strong>god's-eye</strong>. (No endogenous observer gets this step.)";
    else if (!flags.wpHigh) q.innerHTML = "The √ law: your rods ate half the anisotropy. Now try to <strong>hide it completely</strong>: push ξ to the far right (the fixed point) and measure with the slow wavepacket.";
    else if (!flags.batt) q.innerHTML = "Perfect isotropy on slow instruments! So is your world Lorentz-invariant, full stop? Ask your sharpest probe: <strong>run the battery</strong> (or re-measure the front) at this same ξ.";
    else verdict();
  }

  function verdict() {
    const n = d.xi.length - 1, v = $("l5-verdict");
    v.style.display = "block";
    v.innerHTML = `<p><strong>No clean win — the measured verdict at r = ${d.r}:</strong> ` +
      `(1) The naive claim ("no internal experiment detects the substrate") is <strong>falsified</strong>: your fastest signal plateaus at A = ${d.Afront[n].toFixed(4)} ≈ √A_god = ${Math.sqrt(d.A_god).toFixed(4)} — the substrate, square-rooted, at every scale. ` +
      `(2) The corrected claim <strong>survives IR-only</strong>: your slow instruments read ${d.Awp[n].toFixed(4)} at ξ = ${d.xi[n]} — emergent Lorentz invariance is real, but only for observables that flow to the fixed point. ` +
      `(3) You can neither fully see the substrate (your rods absorb half of it) nor fully hide it (your own light-front leaks it back). ` +
      `(4) Open: whether interactions make the front itself co-disperse — undecidable in this free theory. You partly see it, partly don't. That is the result.</p>`;
    CutGame.complete(5, "the √ law");
  }

  function renderNotebook() {
    const tbl = $("l5-notebook");
    while (tbl.rows.length > 1) tbl.deleteRow(1);
    for (const m of notes) {
      const row = tbl.insertRow();
      [m.xi.toFixed(2), m.kind, m.A.toFixed(4),
       Math.abs(m.A - 1) > 0.02 ? "sees an axis" : "isotropic (2% rule)"]
        .forEach(t => { row.insertCell().textContent = t; });
    }
  }

  function drawRods() {
    const cv = $("l5-rods"), ctx = cv.getContext("2d");
    const W = cv.width, H = cv.height, cx = W / 2, cy = H / 2;
    const rho = interp(d.rodRatio).v, ax = 42 * Math.sqrt(rho), ay = 42 / Math.sqrt(rho);
    ctx.clearRect(0, 0, W, H);
    ctx.strokeStyle = css("--rod"); ctx.lineWidth = 5; ctx.lineCap = "round";
    ctx.beginPath(); ctx.moveTo(cx - ax, cy); ctx.lineTo(cx + ax, cy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx, cy - ay); ctx.lineTo(cx, cy + ay); ctx.stroke();
    ctx.fillStyle = css("--muted"); ctx.font = "10px Verdana"; ctx.textAlign = "center";
    ctx.fillText("rod_x / rod_y = " + rho.toFixed(3), cx, H - 4);
  }

  function drawMyChart() {
    const cv = $("l5-mychart"), ctx = cv.getContext("2d");
    const W = cv.width, H = cv.height, padL = 46, padR = 12, padT = 12, padB = 30;
    ctx.clearRect(0, 0, W, H);
    const x0 = Math.log(d.xi[0]), x1 = Math.log(d.xi[d.xi.length - 1]);
    const ymax = Math.max(1.1, ...notes.map(m => m.A)) * 1.05;
    const X = xi => padL + (W - padL - padR) * (Math.log(xi) - x0) / (x1 - x0);
    const Y = y => H - padB - (H - padB - padT) * (y - 0.93) / (ymax - 0.93);
    ctx.font = "11px Verdana"; ctx.fillStyle = css("--muted");
    ctx.strokeStyle = css("--line"); ctx.setLineDash([3, 4]);
    ctx.beginPath(); ctx.moveTo(padL, Y(1)); ctx.lineTo(W - padR, Y(1)); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillText("1 — the only reference you own", padL + 4, Y(1) - 4);
    ctx.fillText("your rod scale ξ (log)", W / 2 - 50, H - 8);
    for (const m of notes) {
      ctx.fillStyle = m.kind === "front" ? css("--cone") : css("--rod");
      ctx.beginPath(); ctx.arc(X(m.xi), Y(m.A), 4.5, 0, 7); ctx.fill();
    }
    // marker for the current instrument scale
    ctx.strokeStyle = css("--seen"); ctx.setLineDash([2, 3]);
    const xm = X(interp(d.Afront).xi);
    ctx.beginPath(); ctx.moveTo(xm, padT); ctx.lineTo(xm, H - padB); ctx.stroke(); ctx.setLineDash([]);
  }

  function drawSweep() {                             // god's-eye comparison chart
    const cv = $("l5-sweep"), ctx = cv.getContext("2d");
    const W = cv.width, H = cv.height, padL = 50, padR = 14, padT = 14, padB = 36;
    ctx.clearRect(0, 0, W, H);
    const lx = d.xi.map(Math.log), x0 = lx[0], x1 = lx[lx.length - 1];
    const ymax = Math.max(d.A_god * 1.1, ...d.Afront, ...d.Awp) * 1.04, ymin = 0.93;
    const X = xi => padL + (W - padL - padR) * (Math.log(xi) - x0) / (x1 - x0);
    const Y = y => H - padB - (H - padB - padT) * (y - ymin) / (ymax - ymin);
    ctx.font = "11px Verdana";
    for (const [v, lab] of [[1, "1 (full cancellation)"], [Math.sqrt(d.A_god), "√A_god — the √ law"], [d.A_god, "A_god — the substrate"]]) {
      ctx.strokeStyle = css("--line"); ctx.setLineDash([3, 4]);
      ctx.beginPath(); ctx.moveTo(padL, Y(v)); ctx.lineTo(W - padR, Y(v)); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = css("--muted"); ctx.fillText(lab, padL + 4, Y(v) - 4);
    }
    ctx.fillStyle = css("--muted");
    ctx.fillText("rod size ξ (log) — right = continuum fixed point", W / 2 - 130, H - 8);
    for (const [arr, color] of [[d.Afront, css("--cone")], [d.Awp, css("--rod")]]) {
      ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.beginPath();
      arr.forEach((v, i) => i ? ctx.lineTo(X(d.xi[i]), Y(v)) : ctx.moveTo(X(d.xi[i]), Y(v)));
      ctx.stroke(); ctx.fillStyle = color;
      arr.forEach((v, i) => { ctx.beginPath(); ctx.arc(X(d.xi[i]), Y(v), 3.2, 0, 7); ctx.fill(); });
    }
    ctx.fillStyle = css("--seen");                   // the player's own points, overlaid
    for (const m of notes) { ctx.beginPath(); ctx.arc(X(m.xi), Y(m.A), 5, 0, 7); ctx.stroke(); ctx.fill(); }
  }

  function drawCone() {
    const cv = $("l5-cone"), ctx = cv.getContext("2d");
    const tmax = (L / 2 - 4) / (2 * Math.max(cone.Jx, cone.Jy));
    coneT = coneT >= tmax ? 0 : coneT + tmax / 240;
    const P = cone.probability(coneT);
    const img = ctx.createImageData(L, L);
    for (let x = 0; x < L; x++) for (let y = 0; y < L; y++) {
      const v = Math.max(0, Math.min(1, (Math.log10(P[((x + L / 2) % L) * L + (y + L / 2) % L] + 1e-30) + 12) / 10));
      const o = 4 * (y * L + x);
      img.data[o] = 255 * Math.min(1, 2.6 * v * v + 0.15 * v);
      img.data[o + 1] = 255 * Math.max(0, 1.6 * v - 0.45) * 1.4;
      img.data[o + 2] = 255 * (v < .5 ? .35 + 1.2 * v : 1.6 - 1.35 * v);
      img.data[o + 3] = 255;
    }
    const off = drawCone.off || (drawCone.off = Object.assign(document.createElement("canvas"), { width: L, height: L }));
    off.getContext("2d").putImageData(img, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(off, 0, 0, L * SCALE, L * SCALE);
    ctx.strokeStyle = "rgba(255,255,255,.5)"; ctx.lineWidth = 1;  // the preferred frame
    ctx.beginPath(); ctx.moveTo(0, L * SCALE / 2); ctx.lineTo(L * SCALE, L * SCALE / 2);
    ctx.moveTo(L * SCALE / 2, 0); ctx.lineTo(L * SCALE / 2, L * SCALE); ctx.stroke();
  }

  function refresh() {
    const m = interp(d.Afront);
    $("l5-xiv").value = m.xi.toFixed(m.xi < 3 ? 2 : 1);
    $("l5-agod").textContent = d.A_god.toFixed(4);
    drawRods(); drawMyChart();
    if (notes.length) { $("l5-compare").style.display = "block"; drawSweep(); }
  }

  function onView(v) {
    if (v === "gods" && notes.length) {
      flags.compared = true;
      drawSweep();
      const f = notes.filter(m => m.kind === "front").pop();
      const sq = Math.sqrt(d.A_god);
      $("l5-comparemsg").textContent = (f
        ? `Your front reading A = ${f.A.toFixed(4)} vs the substrate's A_god = ${d.A_god.toFixed(4)}: ` +
          (Math.abs(f.A - sq) < 0.02
            ? `it sits on the √A_god = ${sq.toFixed(4)} line — your rods absorbed exactly half the substrate's anisotropy. You saw it, square-rooted. `
            : `at this rod scale it is flowing toward the √A_god = ${sq.toFixed(4)} plateau, and nowhere near A_god itself. Push ξ right and re-measure to watch it land on the √ law. `)
        : "") + "Remember: this panel is the view from nowhere. The observer below never gets it.";
      quest();
    }
  }

  function tick() {
    tickPhase += 0.06;
    $("l5-tick").textContent = "◐◓◑◒"[Math.floor(tickPhase) % 4];
    if (CutGame.view === "gods") drawCone();
  }

  CutGame.register(5, { init, tick, onView, enter: refresh });
})();
