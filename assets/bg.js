/* Faint animated science background. Motif is chosen per page by
   <meta name="bg-motif" content="formulas|dna|network">. */
(function () {
  var meta = document.querySelector('meta[name="bg-motif"]');
  if (!meta) return;
  var motif = meta.content;
  var mq = function (q) { return window.matchMedia(q).matches; };
  if (mq("(prefers-reduced-motion: reduce)") || mq("(max-width: 640px)")) return;

  var cv = document.createElement("canvas");
  cv.id = "bg-canvas";
  cv.setAttribute("aria-hidden", "true");
  document.body.insertBefore(cv, document.body.firstChild);
  var ctx = cv.getContext("2d");
  var W = 0, H = 0, dpr = 1, color = [140, 47, 57], gold = [176, 141, 74], t = 0;

  function rgb(v, fallback) {
    var m = /#([0-9a-f]{6})/i.exec((v || "").trim());
    if (!m) return fallback;
    var n = parseInt(m[1], 16);
    return [n >> 16, (n >> 8) & 255, n & 255];
  }
  function readColors() {
    var s = getComputedStyle(document.documentElement);
    color = rgb(s.getPropertyValue("--accent"), color);
    gold = rgb(s.getPropertyValue("--gold"), gold);
  }
  var BOOST = 0.05;
  var rgba = function (c, a) { return "rgba(" + c[0] + "," + c[1] + "," + c[2] + "," + (a > 0.01 ? a + BOOST : 0) + ")"; };
  var rnd = function (a, b) { return a + Math.random() * (b - a); };

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth; H = window.innerHeight;
    cv.width = W * dpr; cv.height = H * dpr;
    cv.style.width = W + "px"; cv.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    init();
  }

  /* ---------- formulas ---------- */
  var FORMULAS = [
    "softmax(z)ᵢ = e^{zᵢ} / Σⱼ e^{zⱼ}",
    "P(θ | D) = P(D | θ) P(θ) / P(D)",
    "𝒩(x | μ, σ²) = (2πσ²)⁻¹ᐟ² exp(−(x−μ)² / 2σ²)",
    "L = −Σ yᵢ log ŷᵢ",
    "θ ← θ − η ∇L(θ)",
    "p² + 2pq + q² = 1",
    "β̂ = (XᵀX)⁻¹ Xᵀy",
    "Attn(Q,K,V) = softmax(QKᵀ / √d) V",
    "H(X) = −Σ p(x) log p(x)",
    "y = Xβ + g + ε",
    "KL(p ‖ q) = Σ p log(p / q)",
    "σ(x) = 1 / (1 + e⁻ˣ)"
  ];
  var SNIPPETS = [
    "library(tidyverse)", "hits <- df |> filter(p < 5e-8)", "fit <- lm(y ~ x, data = d)",
    "def forward(x): return softmax(W @ x)", "for epoch in range(100):", "nextflow run nf-core/rnaseq",
    "set.seed(42)", "ggplot(df, aes(x, y)) + geom_point()", "opt = torch.optim.Adam(params)",
    "samtools view -b in.bam | head", "R6Class(\"Individual\", public = list(...))", "git commit -m \"fix\""
  ];
  var items = [], textList = FORMULAS, textFont = 'italic {s}px Newsreader, Georgia, serif', textSize = [17, 30];
  function initFormulas() { textList = FORMULAS; textFont = "italic {s}px Newsreader, Georgia, serif"; textSize = [17, 30]; initText(); }
  function initCode() { textList = SNIPPETS; textFont = "{s}px ui-monospace, Menlo, monospace"; textSize = [13, 19]; initText(); }
  /* All items drift with one shared velocity, so a non-overlapping layout stays
     non-overlapping; placement and respawn use box tests against existing items. */
  var DRIFT = -3.5, PAD = 16;
  function box(it) { return [it.x, it.y - it.size, it.x + it.w, it.y + it.size * 0.35]; }
  function hits(it) {
    var a = box(it);
    for (var i = 0; i < items.length; i++) {
      if (items[i] === it) continue;
      var b = box(items[i]);
      if (a[0] < b[2] + PAD && a[2] + PAD > b[0] && a[1] < b[3] + PAD && a[3] + PAD > b[1]) return true;
    }
    return false;
  }
  function place(it, yMin, yMax) {
    ctx.font = textFont.replace("{s}", it.size);
    it.w = ctx.measureText(it.s).width;
    for (var k = 0; k < 40; k++) {
      it.x = rnd(0, Math.max(0, W - it.w)); it.y = rnd(yMin, yMax);
      if (!hits(it)) return true;
    }
    return false;
  }
  function initText() {
    items = [];
    var n = Math.max(8, Math.round(W * H / (textList === SNIPPETS ? 150000 : 90000)));
    for (var i = 0; i < n; i++) {
      var it = {
        s: textList[i % textList.length], size: rnd(textSize[0], textSize[1]),
        rot: rnd(-0.12, 0.12), a: rnd(0.10, 0.17), ph: rnd(0, 6.28), x: 0, y: 0, w: 0
      };
      if (place(it, 0, H)) items.push(it);
    }
  }
  function drawFormulas(dt) {
    items.forEach(function (it) {
      it.y += DRIFT * dt;
      if (it.y < -40) {
        /* respawn below the viewport; if no free slot, wait a little further down */
        if (!place(it, H + 40, H + 120)) { it.y = H + 120; it.x = rnd(0, Math.max(0, W - it.w)); }
      }
      ctx.font = textFont.replace("{s}", it.size);
      ctx.save();
      ctx.translate(it.x, it.y); ctx.rotate(it.rot);
      ctx.fillStyle = rgba(color, it.a * (0.75 + 0.25 * Math.sin(t / 3 + it.ph)));
      ctx.fillText(it.s, 0, 0);
      ctx.restore();
    });
  }

  /* ---------- DNA ---------- */
  var cols = [];
  function initDNA() {
    cols = [];
    var n = Math.round(W / 55);
    for (var i = 0; i < n; i++) {
      var len = Math.round(rnd(12, 26)), str = "";
      for (var k = 0; k < len; k++) str += "ACGT"[Math.floor(Math.random() * 4)];
      cols.push({ x: (i + 0.5) * (W / n), y: rnd(0, H), s: str, v: rnd(5, 11), a: rnd(0.05, 0.1) });
    }
  }
  function drawDNA(dt) {
    ctx.font = "15px 'Inter', ui-monospace, monospace";
    cols.forEach(function (c) {
      c.y += c.v * dt;
      if (c.y > H + c.s.length * 20) c.y = -20;
      for (var i = 0; i < c.s.length; i++) {
        ctx.fillStyle = rgba(i % 2 ? color : gold, c.a * (1 - i / c.s.length));
        ctx.fillText(c.s[i], c.x, c.y - i * 20);
      }
    });
  }

  /* ---------- network ---------- */
  var nodes = [], pulses = [];
  function initNet() {
    nodes = []; pulses = [];
    var n = Math.max(18, Math.round(W * H / 38000));
    for (var i = 0; i < n; i++)
      nodes.push({ x: rnd(0, W), y: rnd(0, H), vx: rnd(-3, 3), vy: rnd(-3, 3) });
  }
  function drawNet(dt) {
    var R = 190, i, j;
    nodes.forEach(function (n) {
      n.x += n.vx * dt; n.y += n.vy * dt;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    });
    for (i = 0; i < nodes.length; i++) {
      for (j = i + 1; j < nodes.length; j++) {
        var d = Math.hypot(nodes[i].x - nodes[j].x, nodes[i].y - nodes[j].y);
        if (d < R) {
          ctx.strokeStyle = rgba(color, 0.2 * (1 - d / R));
          ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(nodes[i].x, nodes[i].y); ctx.lineTo(nodes[j].x, nodes[j].y); ctx.stroke();
          if (pulses.length < 14 && Math.random() < 0.0007 * dt * 30)
            pulses.push({ a: nodes[i], b: nodes[j], p: 0 });
        }
      }
    }
    nodes.forEach(function (n) {
      ctx.fillStyle = rgba(color, 0.28);
      ctx.beginPath(); ctx.arc(n.x, n.y, 2.6, 0, 6.28); ctx.fill();
    });
    pulses = pulses.filter(function (q) {
      q.p += dt * 0.45;
      if (q.p >= 1) return false;
      ctx.fillStyle = rgba(gold, 0.45 * Math.sin(q.p * Math.PI));
      ctx.beginPath();
      ctx.arc(q.a.x + (q.b.x - q.a.x) * q.p, q.a.y + (q.b.y - q.a.y) * q.p, 3.2, 0, 6.28);
      ctx.fill();
      return true;
    });
  }

  /* ---------- Manhattan plot ---------- */
  var pts = [], base = 0;
  function initManhattan() {
    pts = []; base = H * 0.92;
    var step = 7, n = Math.ceil((W + 80) / step), i, k;
    for (i = 0; i < n; i++) {
      var x = i * step, chrom = Math.floor(i / (n / 12)) % 2;
      pts.push({ x: x, h: Math.pow(Math.random(), 3) * 70 + 2, c: chrom });
      if (Math.random() < 0.025) {
        var top = rnd(110, 260);
        for (k = 0; k < 7; k++) pts.push({ x: x + rnd(-6, 6), h: top * Math.pow(0.8, k) + rnd(0, 12), c: chrom });
      }
    }
    pts.span = n * step;
  }
  function drawManhattan(dt) {
    ctx.strokeStyle = rgba(gold, 0.18); ctx.lineWidth = 1; ctx.setLineDash([4, 6]);
    ctx.beginPath(); ctx.moveTo(0, base - 150); ctx.lineTo(W, base - 150); ctx.stroke();
    ctx.setLineDash([]);
    ctx.strokeStyle = rgba(color, 0.14);
    ctx.beginPath(); ctx.moveTo(0, base + 6); ctx.lineTo(W, base + 6); ctx.stroke();
    pts.forEach(function (p) {
      p.x -= 6 * dt;
      if (p.x < -10) p.x += pts.span;
      ctx.fillStyle = rgba(p.c ? gold : color, p.h > 150 ? 0.34 : 0.22);
      ctx.beginPath(); ctx.arc(p.x, base - p.h, p.h > 150 ? 2.6 : 2, 0, 6.28); ctx.fill();
    });
  }

  var drawers = { formulas: [initFormulas, drawFormulas], dna: [initDNA, drawDNA], network: [initNet, drawNet],
    code: [initCode, drawFormulas], manhattan: [initManhattan, drawManhattan] };
  var cfg = drawers[motif];
  if (!cfg) { cv.remove(); return; }
  function init() { cfg[0](); }

  var last = 0, frame = 0, running = true;
  function loop(ts) {
    if (!running) return;
    requestAnimationFrame(loop);
    if (ts - last < 33) return;
    var dt = Math.min((ts - last) / 1000, 0.1); last = ts; t += dt;
    if (++frame % 60 === 0) readColors();
    ctx.clearRect(0, 0, W, H);
    cfg[1](dt);
  }
  document.addEventListener("visibilitychange", function () {
    running = !document.hidden;
    if (running) { last = performance.now(); requestAnimationFrame(loop); }
  });
  var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(resize, 150); });
  readColors(); resize(); requestAnimationFrame(loop);
})();
