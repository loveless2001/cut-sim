// Level 3 — "You cannot find the true cut" (Turtle 2, playable): a quest that is
// unwinnable BY DESIGN. Every candidate selector is evaluated on the real system
// and fails honestly: unstable in time, degenerate, circular, or god's-eye-smuggling.
(() => {
  const N = 24, T1 = 4, T2 = 8, TLEAK = 6;
  let sim, cutL = 12;
  let S1 = [], S2 = [], leak = [];     // per-cut survey, indexed by l (1..N-1)
  let surveyL = 1, surveyed = false;
  let tried = new Set(), needle = 0, needleTarget = 0, revealed = false;

  const $ = id => document.getElementById(id);
  const css = k => CutGame.css(k);

  function init() {
    sim = new ChainEntropySim(N);
    $("l3-cut").addEventListener("input", e => { cutL = +e.target.value; $("l3-cutv").value = cutL; readouts(); });
    document.querySelectorAll(".l3-sel").forEach(b => b.addEventListener("click", () => fire(b.dataset.sel)));
    $("l3-accept").addEventListener("click", () => {
      CutGame.complete(3, "Turtle 2 witnessed");
      $("l3-result").textContent = "Badge: “Turtle 2 witnessed”. You didn't find the true cut; you found that the question has no answer inside the theory. That's the win this level had to offer.";
    });
  }

  function readouts() {
    if (!surveyed) return;
    $("l3-sa").textContent = S2[cutL].toFixed(3);
    $("l3-rate").textContent = ((S2[cutL] - S1[cutL]) / (T2 - T1)).toFixed(3);
    $("l3-leak").textContent = Math.abs(leak[cutL]).toFixed(3);
  }

  function argmax(f) { let best = 1; for (let l = 2; l < N; l++) if (f(l) > f(best)) best = l; return best; }

  function fire(sel) {
    if (!surveyed) { $("l3-result").textContent = "Survey still running — one moment."; return; }
    tried.add(sel);
    needleTarget = 0.25 + Math.random() * 0.2;       // the needle stirs... and settles
    setTimeout(() => { needleTarget = 0.02; }, 900);
    let msg;
    if (sel === "rate") {
      const early = argmax(l => S1[l] / T1), late = argmax(l => (S2[l] - S1[l]) / (T2 - T1));
      msg = early === late
        ? `Fastest clock: ℓ = ${early} right now. But a rate is an instantaneous fact — re-run the election at another moment and the winner changes as cuts saturate. A selector that needs re-electing every instant selects nothing.`
        : `Fastest clock early on: ℓ = ${early}. Fastest clock later: ℓ = ${late}. The “true cut” moved while you watched. Unstable — a selector that changes its answer with the state it was meant to ground.`;
    } else if (sel === "leak") {
      const lmin = (() => { let b = 1; for (let l = 2; l < N; l++) if (Math.abs(leak[l]) < Math.abs(leak[b])) b = l; return b; })();
      const ties = [];
      for (let l = 1; l < N; l++) if (l !== lmin && Math.abs(leak[l]) < Math.abs(leak[lmin]) + 0.05) ties.push(l);
      msg = `Smallest leak: ℓ = ${lmin} (|I| = ${Math.abs(leak[lmin]).toFixed(3)})` +
        (ties.length ? `, with ${ties.length} more cut${ties.length > 1 ? "s" : ""} within 0.05 — degenerate. ` : ". ") +
        `And the criterion is gameable: it systematically favors cuts that isolate almost nothing, because near-empty subsystems have little to leak. Optimizing triviality is not selecting a partition.`;
    } else if (sel === "sym") {
      msg = `Symmetry picks the mirror cut ℓ = ${N / 2}. But “the lattice is mirror-symmetric” is a fact about the whole, read from outside every cut. To use this selector, A would already need the god's-eye view — the very thing having a cut denies it. Smuggled.`;
    } else {
      msg = `Counting records requires deciding what counts as a record-bearing system — which is a choice of cut. The selector presupposes the answer it was supposed to produce. Circular.`;
    }
    $("l3-result").textContent = msg;
    if (tried.size >= 3 && !revealed) {
      revealed = true;
      setTimeout(() => { $("l3-reveal").style.display = "block"; }, 1200);
    }
  }

  function drawGauge() {
    const cv = $("l3-gauge"), ctx = cv.getContext("2d");
    const W = cv.width, H = cv.height, cx = W / 2, cy = H - 14, R = 88;
    ctx.clearRect(0, 0, W, H);
    ctx.lineWidth = 10;
    ctx.strokeStyle = css("--line");
    ctx.beginPath(); ctx.arc(cx, cy, R, Math.PI, Math.PI * 1.8); ctx.stroke();
    ctx.strokeStyle = css("--gapc");
    ctx.beginPath(); ctx.arc(cx, cy, R, Math.PI * 1.8, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = css("--gapc"); ctx.font = "bold 9px Verdana"; ctx.textAlign = "center";
    ctx.fillText("CANONICAL", cx + R - 8, cy - R * 0.28);
    const ang = Math.PI * (1 + needle);
    ctx.strokeStyle = css("--ink"); ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.moveTo(cx, cy);
    ctx.lineTo(cx + (R - 16) * Math.cos(ang), cy + (R - 16) * Math.sin(ang)); ctx.stroke();
  }

  function tick(dt) {
    if (!surveyed && surveyL < N) {                  // chunked survey: one cut per frame
      S1[surveyL] = sim.entropy(T1, surveyL);
      S2[surveyL] = sim.entropy(T2, surveyL);
      leak[surveyL] = 2 * sim.correlationMatrix(TLEAK).Ci[(surveyL - 1) * N + surveyL];
      $("l3-survey").textContent = `surveying cuts… ${surveyL}/${N - 1}`;
      surveyL++;
      if (surveyL === N) { surveyed = true; $("l3-survey").textContent = `${N - 1} cuts surveyed — every one yields valid co-products.`; readouts(); }
    }
    needle += (needleTarget - needle) * Math.min(1, dt * 4) + (Math.random() - 0.5) * 0.006;
    needle = Math.max(0, Math.min(0.75, needle));    // the needle can stir, never certify
    drawGauge();
  }

  CutGame.register(3, { init, tick });
})();
