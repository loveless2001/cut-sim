// Level 2 — classify boundary flows and persistent structures for a chosen cut.
(() => {
  const N = 24, BOND = 12;           // spotlight bond between sites 11 and 12
  let sim, t = 0, cutL = 12, frameCount = 0;
  let selected = null, placed = 0, statusesSeen = new Set(), done = false;

  const $ = id => document.getElementById(id);
  const css = k => CutGame.css(k);
  const RIGHT = {
    flow: "Correct: this is a boundary-flow quantity for the declared cut.",
    keep: "Correct: this is treated as a persistent quantity in this model.",
  };

  function init() {
    sim = new ChainEntropySim(N);
    const slider = $("l2-cut");
    slider.addEventListener("input", () => {
      cutL = +slider.value; $("l2-cutv").value = cutL; bondStatus();
    });
    document.querySelectorAll("#l2-chips .chip").forEach(ch => {
      ch.addEventListener("click", () => {
        if (ch.classList.contains("placed")) return;
        document.querySelectorAll("#l2-chips .chip").forEach(c => c.classList.remove("sel"));
        ch.classList.add("sel"); selected = ch;
      });
    });
    [["l2-binflow", "flow"], ["l2-binkeep", "keep"]].forEach(([id, kind]) => {
      $(id).addEventListener("click", () => {
        if (!selected) { $("l2-feedback").textContent = "Select a quantity first."; return; }
        if (selected.dataset.kind === kind) {
          selected.classList.remove("sel"); selected.classList.add("placed");
          $(id).appendChild(selected);
          $("l2-feedback").textContent = RIGHT[kind];
          selected = null; placed++;
          checkDone();
        } else {
          $("l2-feedback").textContent = kind === "flow"
            ? "Not this category: the model treats that quantity as persistent rather than boundary flux."
            : "Not this category: this quantity is defined as change across the declared boundary.";
        }
      });
    });
    bondStatus();
  }

  function bondStatus() {
    let status, msg;
    if (cutL === BOND) {
      status = "boundary";
      msg = "The highlighted bond is the current boundary, so its current is cross-cut flux.";
    } else if (cutL > BOND) {
      status = "insideA";
      msg = "The same bond and current now lie inside A, so they are no longer cross-cut flux. The partition changed; the microscopic dynamics did not.";
    } else {
      status = "insideB";
      msg = "The same bond now lies inside B and is outside A's declared readout channels.";
    }
    statusesSeen.add(status);
    $("l2-bond").textContent = msg;
    checkDone();
  }

  function checkDone() {
    if (!done && placed === 6 && statusesSeen.size >= 2) {
      done = true;
      $("l2-feedback").textContent = "Classification complete. Moving the cut changed which current counted as cross-cut flux.";
      CutGame.complete(2, "cut-relative classification");
    }
  }

  function draw(Cr, Ci) {
    const cv = $("l2-chain"), ctx = cv.getContext("2d");
    const W = cv.width, H = cv.height, pad = 24, w = (W - 2 * pad) / N, cy = H / 2 + 8;
    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < N - 1; i++) {                // bonds; spotlight BOND
      ctx.strokeStyle = i === BOND - 1 ? css("--conj") : css("--line");
      ctx.lineWidth = i === BOND - 1 ? 3.5 : 1.5;
      ctx.beginPath(); ctx.moveTo(pad + (i + .5) * w, cy); ctx.lineTo(pad + (i + 1.5) * w, cy); ctx.stroke();
    }
    for (let i = 0; i < N; i++) {
      ctx.fillStyle = css("--accent");
      ctx.globalAlpha = 0.15 + 0.85 * Math.min(1, Math.max(0, Cr[i * N + i]));
      ctx.beginPath(); ctx.arc(pad + (i + .5) * w, cy, Math.min(w * .36, 10), 0, 7); ctx.fill();
    }
    ctx.globalAlpha = 1;
    ctx.strokeStyle = css("--gapc"); ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(pad + cutL * w, 10); ctx.lineTo(pad + cutL * w, H - 10); ctx.stroke();
    ctx.fillStyle = css("--muted"); ctx.font = "11px Verdana";
    ctx.fillText("A", pad, 12); ctx.fillText("B", pad + cutL * w + 8, 12);
    ctx.fillStyle = css("--conj");
    ctx.fillText("watched bond", pad + (BOND - 3) * w, H - 4);
  }

  function tick(dt) {
    if (CutGame.view !== "cut") return;
    t += dt * 2; frameCount++;
    const { Cr, Ci } = sim.correlationMatrix(t);
    draw(Cr, Ci);
    if (frameCount % 3 === 0) {
      const I = 2 * Ci[(cutL - 1) * N + cutL];
      let ntot = 0, etot = 0;
      for (let i = 0; i < N; i++) ntot += Cr[i * N + i];
      for (let i = 0; i < N - 1; i++) etot += -2 * Cr[i * N + i + 1];
      $("l2-leak").textContent = (I >= 0 ? "→ " : "← ") + Math.abs(I).toFixed(3);
      $("l2-ntot").textContent = ntot.toFixed(3) + " ✓";
      $("l2-etot").textContent = etot.toFixed(3) + " ✓";
    }
    if (frameCount % 6 === 0) $("l2-sa").textContent = sim.entropy(t, cutL).toFixed(3);
  }

  CutGame.register(2, { init, tick, enter() { CutGame.setView("cut", true); } });
})();
