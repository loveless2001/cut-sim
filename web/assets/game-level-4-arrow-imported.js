// Level 4 — "Which way is forward?": for one Hamiltonian, preparation, cut, and
// entropy transcript, the player stands at an entropy minimum. Both halves of S_A(s)
// are computed independently (no mirroring trick); agreement limits this supplied
// procedure and does not establish a universal orientation theorem.
(() => {
  const N = 16, LEN = 8, SMAX = 12, NPTS = 61;
  let sim, S = [], sVals = [];
  let marker = 0, markerTarget = 0, computed = 0;
  let flipTried = false, leverSet = false, lever = "center";

  const $ = id => document.getElementById(id);
  const css = k => CutGame.css(k);

  function init() {
    sim = new ChainEntropySim(N);
    for (let i = 0; i < NPTS; i++) sVals.push(-SMAX + 2 * SMAX * i / (NPTS - 1));
    $("l4-fwd").addEventListener("click", () => pointArrow(1));
    $("l4-bwd").addEventListener("click", () => pointArrow(-1));
    document.querySelectorAll(".l4-probe").forEach(b => b.addEventListener("click", () => {
      $("l4-msg").textContent = b.dataset.p === "dyn"
        ? "Probe result: unitarity makes the evolution reversible. For this Hamiltonian and symmetric preparation, the tested transcript is also symmetric; time-reversal symmetry is not implied by unitarity alone."
        : "Probe result: both halves were computed independently, and S_A(−s) = S_A(s) to plotting precision. This entropy transcript does not pick a side; other procedures are not covered.";
    }));
    document.querySelectorAll('input[name="l4lever"]').forEach(r => r.addEventListener("change", () => {
      lever = r.value; leverSet = true;
      $("l4-godsmsg").textContent = lever === "center"
        ? "The chosen low-entropy preparation sits mid-block: this model's entropy grows away from it in both directions. The curve alone does not establish a universal arrow."
        : `The chosen low-entropy preparation now sits at the ${lever} end. The modeled entropy gradient points away from it; environmental, coarse-graining, and record conditions would still be needed for a macroscopic arrow.`;
      if (flipTried) CutGame.complete(4, "arrow input identified");
      draw();
    }));
  }

  function pointArrow(dir) {
    markerTarget = Math.max(-SMAX, Math.min(SMAX, markerTarget + dir * 5));
    if ($("l4-fwd").dataset.hit && $("l4-bwd").dataset.hit) flipTried = true;
    (dir > 0 ? $("l4-fwd") : $("l4-bwd")).dataset.hit = "1";
    if ($("l4-fwd").dataset.hit && $("l4-bwd").dataset.hit) {
      flipTried = true;
      $("l4-msg").textContent = "Along this symmetric entropy transcript, S rises in both directions from the minimum. This procedure does not select one direction as the future. Switch to Model view to change the preparation condition.";
      if (leverSet) CutGame.complete(4, "arrow input identified");
    } else {
      $("l4-msg").textContent = "Along that branch S rises. That observation alone does not define duration or a universal future; test the other branch too.";
    }
  }

  function domain() {
    if (lever === "left") return [0, SMAX];          // conditioned: block starts at the condition
    if (lever === "right") return [-SMAX, 0];
    return [-SMAX, SMAX];
  }

  function draw() {
    const cv = $("l4-plot"), ctx = cv.getContext("2d");
    const W = cv.width, H = cv.height, padL = 50, padR = 20, padT = 34, padB = 30;
    ctx.clearRect(0, 0, W, H);
    const [s0, s1] = domain();
    const ymax = Math.max(...S.slice(0, computed), 0.1) * 1.15;
    const X = s => padL + (W - padL - padR) * (s - s0) / (s1 - s0);
    const Y = y => H - padB - (H - padB - padT) * y / ymax;
    ctx.strokeStyle = css("--line"); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(padL, Y(0)); ctx.lineTo(W - padR, Y(0)); ctx.stroke();
    ctx.fillStyle = css("--muted"); ctx.font = "11px Verdana";
    ctx.fillText("S_A", 12, padT + 10);
    ctx.fillText("internal parameter s (which side is the future?)", W / 2 - 120, H - 8);
    ctx.strokeStyle = css("--accent"); ctx.lineWidth = 2; ctx.beginPath();
    let started = false;
    for (let i = 0; i < computed; i++) {
      if (sVals[i] < s0 - 1e-9 || sVals[i] > s1 + 1e-9) continue;
      const x = X(sVals[i]), y = Y(S[i]);
      started ? ctx.lineTo(x, y) : ctx.moveTo(x, y); started = true;
    }
    ctx.stroke();
    if (computed < NPTS) { ctx.fillText("computing both directions exactly… " + computed + "/" + NPTS, padL + 10, padT + 10); }
    // the player's marker ("you are here"), only meaningful on the full block
    if (marker >= s0 && marker <= s1 && computed === NPTS) {
      const i = Math.round((marker + SMAX) / (2 * SMAX) * (NPTS - 1));
      ctx.fillStyle = css("--gapc");
      ctx.beginPath(); ctx.arc(X(marker), Y(S[i]), 5, 0, 7); ctx.fill();
      ctx.font = "bold 11px Verdana";
      ctx.fillText("you · S = " + S[i].toFixed(2), X(marker) + 8, Y(S[i]) - 8);
    }
    // arrows appear only once a past condition exists
    if (leverSet) {
      ctx.strokeStyle = css("--accent2"); ctx.fillStyle = css("--accent2"); ctx.lineWidth = 3;
      const yA = padT - 14;
      const arrow = (xa, xb) => {
        ctx.beginPath(); ctx.moveTo(xa, yA + 8); ctx.lineTo(xb, yA + 8); ctx.stroke();
        const d = Math.sign(xb - xa) * 7;
        ctx.beginPath(); ctx.moveTo(xb, yA + 8); ctx.lineTo(xb - d, yA + 3); ctx.lineTo(xb - d, yA + 13); ctx.fill();
      };
      if (lever === "left") arrow(X(s0) + 4, X(s1) - 4);
      else if (lever === "right") arrow(X(s1) - 4, X(s0) + 4);
      else { arrow(X(0), X(SMAX) - 4); arrow(X(0), X(-SMAX) + 4); }
    }
  }

  function tick(dt) {
    if (computed < NPTS) {                           // chunked: both signs computed for real
      S[computed] = sim.entropy(sVals[computed], LEN);
      computed++; draw(); return;
    }
    if (Math.abs(marker - markerTarget) > 0.02) {
      marker += Math.sign(markerTarget - marker) * Math.min(Math.abs(markerTarget - marker), dt * 4);
      draw();
    }
  }

  CutGame.register(4, { init, tick, enter: draw, onView: draw });
})();
