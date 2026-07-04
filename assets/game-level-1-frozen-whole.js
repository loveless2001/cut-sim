// Level 1 — "The frozen whole": god's-eye shows the universe as a static block
// (no "now" marker anywhere); the player's first cut CREATES a clock, an
// information deficit, and an energy leak. Exact dynamics via ChainEntropySim.
(() => {
  const N = 32, TBLOCK = 14, ROWS = 84;
  let sim, blockOcc = null;          // ROWS x N occupation history (the block)
  let cutL = 0, t = 0, S = 0, frameCount = 0, checkedBack = false;
  let hoverL = 0;                    // ghost cut line under the mouse (gods view)

  const $ = id => document.getElementById(id);
  const css = k => CutGame.css(k);
  const WHEN_ANSWERS = [
    "The state is one vector. “When” presupposes a clock, and no subsystem is keeping one — there is no subsystem.",
    "You can point at a parameter value in the block, but that names a place in a picture, not a happening. Nothing is “at” it.",
    "S_U = 0 at every slice: nothing has been registered by anything, ever. No registration, no event, no when.",
    "The whole will keep not answering. (Hint: the second task.)",
  ];
  let whenIdx = 0;

  function init() {
    sim = new ChainEntropySim(N);
    // the block: global occupations over the internal parameter (cut-independent)
    blockOcc = new Float64Array(ROWS * N);
    for (let r = 0; r < ROWS; r++) {
      const { Cr } = sim.correlationMatrix(TBLOCK * r / (ROWS - 1));
      for (let i = 0; i < N; i++) blockOcc[r * N + i] = Cr[i * N + i];
    }
    $("l1-e").textContent = "0.000 — constant";
    $("l1-n").textContent = "16 — constant";
    $("l1-when").addEventListener("click", () => {
      $("l1-whenOut").textContent = WHEN_ANSWERS[whenIdx++ % WHEN_ANSWERS.length];
    });
    const cv = $("l1-block");
    cv.style.cursor = "crosshair";
    cv.addEventListener("mousemove", e => { hoverL = siteFromEvent(cv, e); drawBlock(); });
    cv.addEventListener("mouseleave", () => { hoverL = 0; drawBlock(); });
    cv.addEventListener("click", e => { const l = siteFromEvent(cv, e); if (l) makeCut(l); });
    drawBlock();
  }

  function siteFromEvent(cv, e) {
    const rect = cv.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (cv.width / rect.width);
    const l = Math.round((x - 20) / ((cv.width - 40) / N));
    return (l >= 2 && l <= N - 2) ? l : 0;
  }

  function makeCut(l) {
    if (cutL) return;                                // one first-cut moment per visit
    cutL = l; t = 0; S = 0;
    $("l1-cuthint").innerHTML = "<strong>Cut drawn at ℓ = " + l +
      ".</strong> Toggle to the <strong>Cut</strong> view — you live there now.";
    $("l1-nocut").style.display = "none";
    $("l1-cutui").style.display = "block";
    CutGame.setView("cut");
    // the single most important moment: co-products emerge FROM the act of cutting
    ["l1-cp-time", "l1-cp-info", "l1-cp-energy"].forEach((id, i) =>
      setTimeout(() => $(id).classList.add("reveal"), 450 + 380 * i));
    drawBlock();
  }

  function drawBlock() {
    const cv = $("l1-block"), ctx = cv.getContext("2d");
    const W = cv.width, H = cv.height, padX = 20, padY = 14;
    const cw = (W - 2 * padX) / N, rh = (H - 2 * padY) / ROWS;
    ctx.clearRect(0, 0, W, H);
    for (let r = 0; r < ROWS; r++) for (let i = 0; i < N; i++) {
      const occ = blockOcc[r * N + i];
      ctx.fillStyle = css("--accent");
      ctx.globalAlpha = 0.06 + 0.8 * Math.min(1, Math.max(0, occ));
      ctx.fillRect(padX + i * cw + 0.5, H - padY - (r + 1) * rh, cw - 1, rh + 0.4);
    }
    ctx.globalAlpha = 1;
    ctx.font = "11px Verdana"; ctx.fillStyle = css("--muted");
    ctx.fillText("32 sites →", padX, H - 2);
    ctx.save(); ctx.translate(10, H / 2); ctx.rotate(-Math.PI / 2);
    ctx.textAlign = "center"; ctx.fillText("internal parameter (a direction, not a flow)", 0, 0);
    ctx.restore();
    const line = (l, color, dash) => {
      ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.setLineDash(dash);
      ctx.beginPath(); ctx.moveTo(padX + l * cw, padY); ctx.lineTo(padX + l * cw, H - padY);
      ctx.stroke(); ctx.setLineDash([]);
    };
    if (hoverL && !cutL) line(hoverL, css("--conj"), [5, 4]);
    if (cutL) {
      line(cutL, css("--gapc"), []);
      ctx.fillStyle = css("--gapc"); ctx.font = "bold 11px Verdana";
      ctx.fillText("your cut — note: the block did not change", padX + cutL * cw + 6, padY + 12);
    }
  }

  function drawCutView() {
    const cv = $("l1-chain"), ctx = cv.getContext("2d");
    const W = cv.width, H = cv.height, pad = 20, w = (W - 2 * pad) / N;
    ctx.clearRect(0, 0, W, H);
    const { Cr } = sim.correlationMatrix(t);
    for (let i = 0; i < cutL; i++) {                 // A: what you are
      ctx.fillStyle = css("--accent");
      ctx.globalAlpha = 0.15 + 0.85 * Math.min(1, Math.max(0, Cr[i * N + i]));
      ctx.beginPath(); ctx.arc(pad + (i + .5) * w, H / 2, Math.min(w * .38, 11), 0, 7); ctx.fill();
    }
    ctx.globalAlpha = .25; ctx.fillStyle = css("--muted");  // B: fog
    ctx.fillRect(pad + cutL * w, 12, (N - cutL) * w, H - 24);
    ctx.globalAlpha = 1; ctx.font = "11px Verdana"; ctx.fillStyle = css("--muted");
    ctx.fillText("A (you)", pad, 10);
    ctx.fillText("B — fog: not yours to see", pad + cutL * w + 8, 10);
    ctx.strokeStyle = css("--gapc"); ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(pad + cutL * w, 6); ctx.lineTo(pad + cutL * w, H - 6); ctx.stroke();
    // clock dial: the needle IS S_A, no hidden gears
    const ck = $("l1-clock"), c2 = ck.getContext("2d"), R = 48, cx = 60, cy = 62;
    c2.clearRect(0, 0, 120, 120);
    c2.strokeStyle = css("--line"); c2.lineWidth = 2;
    c2.beginPath(); c2.arc(cx, cy, R, 0, 7); c2.stroke();
    const smax = Math.min(cutL, N - cutL) * Math.LN2;
    const ang = -Math.PI / 2 + (S / smax) * Math.PI * 1.7;
    c2.strokeStyle = css("--accent2"); c2.lineWidth = 3;
    c2.beginPath(); c2.moveTo(cx, cy);
    c2.lineTo(cx + R * .82 * Math.cos(ang), cy + R * .82 * Math.sin(ang)); c2.stroke();
    c2.fillStyle = css("--muted"); c2.font = "10px Verdana"; c2.textAlign = "center";
    c2.fillText("S_A = " + S.toFixed(2), cx, cy + R + 9);
  }

  function tick(dt) {
    if (!cutL || CutGame.view !== "cut") return;
    t += dt * 2;                                     // time exists for A now — only for A
    if (frameCount++ % 2 === 0) {
      S = sim.entropy(t, cutL);
      const smax = Math.min(cutL, N - cutL) * Math.LN2;
      $("l1-bits").textContent = (S / Math.LN2).toFixed(2);
      $("l1-infobar").style.width = (100 * S / smax).toFixed(1) + "%";
      const { Ci } = sim.correlationMatrix(t);
      const I = 2 * Ci[(cutL - 1) * N + cutL];       // particle current across the cut bond
      $("l1-cur").textContent = (I >= 0 ? "→ " : "← ") + Math.abs(I).toFixed(3);
      $("l1-leakbar").style.width = Math.min(100, 160 * Math.abs(I)).toFixed(1) + "%";
    }
    drawCutView();
  }

  function onView(v) {
    if (v === "gods") {
      drawBlock();
      if (cutL && !checkedBack) {
        checkedBack = true;
        $("l1-checked").textContent = "✓ You checked: the whole is still frozen. Badge earned: “time is a co-product”.";
        CutGame.complete(1, "time is a co-product");
      }
    }
  }

  CutGame.register(1, { init, tick, onView, enter() { drawBlock(); } });
})();
