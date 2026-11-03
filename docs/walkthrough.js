/* Live demo page for policy-assistant.
   Built AI-assisted under Henfred Pietersen's direction.
   Embed:  <div id="pa-walkthrough"></div>
           <script defer src="https://cdn.jsdelivr.net/gh/henfredpietersen/policy-assistant@<commit>/docs/walkthrough.js"></script>
   The "Try it" box calls the public API below. Everything else on the page is static and
   matches the README (numbers from scripts/evaluate_retrieval.py and scripts/train_intent.py). */
(function () {
  "use strict";
  var host = document.getElementById("pa-walkthrough");
  if (!host || host.shadowRoot) return;
  var API = host.getAttribute("data-api") || "https://policy-assistant-3mfz.onrender.com";
  var REPO = "https://github.com/henfredpietersen/policy-assistant";
  var root = host.attachShadow({ mode: "open" });
  host.style.minHeight = "";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function $(sel) { return root.querySelector(sel); }
  function $$(sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); }

  var CSS = [
    ":host{all:initial;display:block}",
    "*{box-sizing:border-box}",
    ".wt{--bg:#05070d;--panel:rgba(255,255,255,.045);--panel2:rgba(255,255,255,.075);--line:rgba(255,255,255,.09);",
    "--text:#eef0f6;--dim:#9aa1b4;--orange:#ff7a45;--orange2:#e85a2a;--cyan:#4fd1ff;--ok:#34d399;--bad:#f87171;--warn:#fbbf24;",
    "background:var(--bg);color:var(--text);font:16px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;",
    "padding:clamp(28px,6vw,64px) 16px 48px;-webkit-font-smoothing:antialiased}",
    ".wrap{max-width:880px;margin:0 auto}",
    "h1{font-size:clamp(1.8rem,5.2vw,2.7rem);line-height:1.12;font-weight:800;letter-spacing:-.02em;margin:0 0 14px}",
    "h2{font-size:clamp(1.25rem,3.4vw,1.6rem);line-height:1.2;font-weight:800;margin:0 0 8px;letter-spacing:-.01em}",
    "h3{font-size:1rem;margin:0 0 10px;font-weight:700}",
    "p{margin:0 0 12px;color:var(--dim)}",
    "a{color:var(--cyan)}",
    "strong{color:var(--text)}",
    "code{font:.86em ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--panel2);padding:1px 6px;border-radius:6px;color:var(--text)}",
    ".grad{background:linear-gradient(90deg,#fff 0%,var(--orange) 50%,var(--cyan) 100%);-webkit-background-clip:text;background-clip:text;color:transparent}",
    ".eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--orange);margin:0 0 12px}",
    ".lede{font-size:1.06rem;max-width:640px}",
    ".tags{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0}",
    ".tag{font-size:.8rem;padding:5px 11px;border-radius:99px;border:1px solid var(--line);background:var(--panel);color:var(--text)}",
    ".tag b{color:var(--orange)}",
    "section.step{padding:44px 0 8px}",
    ".num{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;",
    "background:linear-gradient(135deg,var(--orange),#ffb27a);color:#0a0e1a;font-weight:800;font-size:.85rem;margin-bottom:12px}",
    ".card{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:clamp(14px,3vw,22px);margin-top:16px}",
    ".row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}",
    "button{font:inherit;cursor:pointer}",
    ".btn{border:0;border-radius:11px;padding:11px 18px;font-weight:700;color:#0a0e1a;",
    "background:linear-gradient(135deg,var(--orange) 0%,#ffb27a 100%);box-shadow:0 8px 26px -8px rgba(232,90,42,.6)}",
    ".btn:disabled{opacity:.5;cursor:default}",
    ".ghost{border:1px solid var(--line);background:var(--panel2);color:var(--text);border-radius:11px;padding:8px 12px;font-weight:600;font-size:.86rem;text-align:left}",
    ".ghost:hover{border-color:var(--orange)}",
    ".ghost.miss{border-style:dashed}",
    ".ask{display:flex;gap:8px;margin-top:12px}",
    "input{flex:1;min-width:0;font:inherit;color:var(--text);background:#0b0f19;border:1px solid var(--line);border-radius:11px;padding:11px 14px}",
    "input:focus{outline:2px solid var(--orange);outline-offset:1px}",
    ".status{font-size:.82rem;color:var(--dim);margin-top:10px;display:flex;align-items:center;gap:8px}",
    ".dot{width:8px;height:8px;border-radius:50%;background:var(--warn);flex:none}",
    ".dot.ok{background:var(--ok)}.dot.bad{background:var(--bad)}",
    ".answer{font-size:1.02rem;color:var(--text);margin:0 0 14px;white-space:pre-wrap}",
    ".pill{display:inline-block;font-size:.72rem;font-weight:700;padding:2px 8px;border-radius:99px;border:1px solid currentColor;white-space:nowrap}",
    ".ok{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}.dimc{color:var(--dim)}",
    ".meta{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;font-size:.84rem;color:var(--dim)}",
    ".tbl{overflow:auto;border:1px solid var(--line);border-radius:12px;margin-top:12px;-webkit-overflow-scrolling:touch}",
    "table{border-collapse:collapse;width:100%;font-size:.86rem}",
    "th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line)}",
    "tr:last-child td{border-bottom:0}",
    "th{background:#0d111b;color:var(--dim);font-weight:600;font-size:.72rem;text-transform:uppercase;letter-spacing:.04em}",
    "td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}",
    ".bar{height:6px;border-radius:3px;background:linear-gradient(90deg,var(--orange),#ffb27a);min-width:2px}",
    "ol.flow{margin:12px 0 0;padding:0;list-style:none;counter-reset:f}",
    "ol.flow li{counter-increment:f;position:relative;padding:12px 0 12px 44px;border-bottom:1px solid var(--line);color:var(--dim)}",
    "ol.flow li:last-child{border-bottom:0}",
    "ol.flow li::before{content:counter(f);position:absolute;left:0;top:12px;width:28px;height:28px;border-radius:8px;",
    "background:var(--panel2);border:1px solid var(--line);color:var(--orange);font-weight:800;display:flex;align-items:center;justify-content:center;font-size:.85rem}",
    "ol.flow b{color:var(--text)}",
    "ul.plain{margin:8px 0 0;padding-left:18px;color:var(--dim)}ul.plain li{margin:6px 0}",
    ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:12px}",
    ".stat{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px}",
    ".stat .v{font-size:1.6rem;font-weight:800;color:var(--text);font-variant-numeric:tabular-nums}",
    ".stat .k{font-size:.8rem;color:var(--dim)}",
    ".foot{margin-top:44px;padding-top:20px;border-top:1px solid var(--line);font-size:.86rem}",
    "@media (max-width:520px){.ask{flex-direction:column}.btn{width:100%}}"
  ].join("");

  var SAMPLES = [
    "How long does a claim take?",
    "What happens if I miss a premium?",
    "Can my child be a beneficiary?",
    "How do I cancel my policy?"
  ];
  var MISSES = [
    "Who gets the money if I never named anyone?",
    "Can I split the payout between my two kids?"
  ];

  root.innerHTML =
    "<style>" + CSS + "</style>" +
    "<div class='wt'><div class='wrap'>" +
    "<p class='eyebrow'>Case study · Policy Assistant</p>" +
    "<h1>An insurance FAQ bot that <span class='grad'>shows where every answer came from</span></h1>" +
    "<p class='lede'>Ask a life-insurance question. The service works out what the question is about, finds the matching sections in a small policy knowledge base, and answers only from them, with the sources and scores on screen.</p>" +
    "<div class='tags'><span class='tag'>Python · scikit-learn</span><span class='tag'>FastAPI · Docker</span><span class='tag'>GitHub Actions CI</span>" +
    "<span class='tag'>Retrieval Hit@1 <b>0.80</b></span><span class='tag'>Built AI-assisted</span></div>" +

    "<section class='step'><div class='num'>1</div><h2>Try it</h2>" +
    "<p>Pick a sample or type your own question about claims, premiums, beneficiaries or cancellations.</p>" +
    "<div class='card'>" +
    "<div class='row' id='samples'></div>" +
    "<form class='ask' id='form'><input id='q' maxlength='500' placeholder='e.g. Is there a grace period for late premiums?' aria-label='Your question'>" +
    "<button class='btn' id='go' type='submit'>Ask</button></form>" +
    "<div class='status' id='status'><span class='dot' id='dot'></span><span id='stext'>Checking the server…</span></div>" +
    "</div>" +
    "<div class='card' id='result' hidden></div>" +
    "<p style='margin-top:14px;font-size:.88rem'>Want to see it fail? These two are the retrieval misses from the evaluation:</p>" +
    "<div class='row' id='misses'></div>" +
    "</section>" +

    "<section class='step'><div class='num'>2</div><h2>How it works</h2>" +
    "<p>Three small steps, each one testable on its own.</p>" +
    "<div class='card'><ol class='flow'>" +
    "<li><b>Classify the intent.</b> A TF-IDF + logistic regression model, tuned with a grid search, labels the question as claims, premiums, beneficiaries or cancellations, with a confidence score.</li>" +
    "<li><b>Retrieve the sections.</b> Character n-gram TF-IDF with cosine similarity ranks every section of the knowledge base and keeps the top three. Character n-grams mean \"beneficiary\" still matches \"beneficiaries\".</li>" +
    "<li><b>Answer from the best match.</b> On this page the answer is extractive: the text of the best-scoring section, so it can't make anything up and costs nothing to run. The repo also has a Gemini path that writes the answer from the retrieved sections and falls back to extractive if the model fails. It isn't switched on here.</li>" +
    "</ol></div></section>" +

    "<section class='step'><div class='num'>3</div><h2>How well it works</h2>" +
    "<p>Retrieval is scored on 15 labelled questions; the intent classifier on 60, with a 75/25 split.</p>" +
    "<div class='grid'>" +
    "<div class='stat'><div class='v'>0.80</div><div class='k'>Hit@1: right section ranked first</div></div>" +
    "<div class='stat'><div class='v'>0.87</div><div class='k'>Hit@3: right section in the top three</div></div>" +
    "<div class='stat'><div class='v'>0.83</div><div class='k'>MRR across the 15 questions</div></div>" +
    "<div class='stat'><div class='v'>0.73</div><div class='k'>Intent accuracy on 15 held-out questions</div></div>" +
    "</div>" +
    "<div class='card'><h3>Guard rails in the pipeline</h3><ul class='plain'>" +
    "<li>22 automated tests, including one that fails the build if Hit@3 drops below 0.8.</li>" +
    "<li>Every push lints, tests, builds the Docker image and smoke-tests the running container.</li>" +
    "<li>This public instance only accepts calls from outview.co.za and limits each visitor to 20 questions per 10 minutes.</li>" +
    "</ul></div></section>" +

    "<section class='step'><div class='num'>4</div><h2>What it can't do</h2>" +
    "<div class='card'><ul class='plain'>" +
    "<li><b>It matches words, not meaning.</b> The two misses above share almost no words with the right section. Dense embeddings would catch them; the retriever is built so one can be swapped in.</li>" +
    "<li><b>The evaluation is small.</b> 15 retrieval questions and a 15-question classifier test set make the scores noisy. More labelled data would help more than more tuning.</li>" +
    "<li><b>The knowledge base is invented.</b> It's a generic, fictional example written for this project, not any insurer's real policy wording.</li>" +
    "<li><b>The free server sleeps.</b> If nobody has asked anything for a while, the first question can take up to a minute.</li>" +
    "</ul></div></section>" +

    "<div class='foot'><p><strong>How this was built.</strong> AI-assisted, under my direction: I specified the system and the evaluation, Claude generated the code, and I reviewed it, ran the tests and checked the numbers.</p>" +
    "<p>Code, tests and evaluation scripts: <a href='" + REPO + "' target='_blank' rel='noopener'>github.com/henfredpietersen/policy-assistant</a></p></div>" +
    "</div></div>";

  function setStatus(state, text) {
    $("#dot").className = "dot" + (state === "ok" ? " ok" : state === "bad" ? " bad" : "");
    $("#stext").textContent = text;
  }

  function timeout(ms) {
    if (typeof AbortController === "undefined") return undefined;
    var c = new AbortController();
    setTimeout(function () { c.abort(); }, ms);
    return c.signal;
  }

  var ready = false;
  function wake() {
    setStatus("wait", "Checking the server…");
    var slow = setTimeout(function () {
      if (!ready) setStatus("wait", "Waking the server. The free tier sleeps when idle, so this can take up to a minute.");
    }, 3000);
    fetch(API + "/health", { signal: timeout(90000) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function () { ready = true; clearTimeout(slow); setStatus("ok", "Server ready."); })
      .catch(function () { clearTimeout(slow); setStatus("bad", "Couldn't reach the server. Try asking anyway; it may still be waking up."); });
  }

  function renderResult(d) {
    var maxScore = 0;
    (d.sources || []).forEach(function (s) { if (s.score > maxScore) maxScore = s.score; });
    var rows = (d.sources || []).map(function (s, i) {
      var w = maxScore ? Math.round((s.score / maxScore) * 100) : 0;
      return "<tr><td class='n'>" + (i + 1) + "</td><td>" + esc(s.title) + "</td><td class='n'>" + esc(s.score.toFixed(3)) +
        "</td><td style='width:30%'><div class='bar' style='width:" + w + "%'></div></td></tr>";
    }).join("");
    var conf = d.intent_confidence == null ? "" : " · confidence " + esc(d.intent_confidence.toFixed(2));
    $("#result").innerHTML =
      "<h3>Answer</h3><p class='answer'>" + esc(d.answer) + "</p>" +
      "<div class='meta'><span class='pill warn'>intent: " + esc(d.intent || "n/a") + conf + "</span>" +
      "<span class='pill dimc'>answer: " + esc(d.generator) + "</span></div>" +
      "<h3>Sources it used</h3><div class='tbl'><table><thead><tr><th>#</th><th>Section</th><th>Score</th><th></th></tr></thead><tbody>" +
      rows + "</tbody></table></div>";
    $("#result").hidden = false;
  }

  function renderError(text) {
    $("#result").innerHTML = "<p class='bad' style='margin:0'>" + esc(text) + "</p>";
    $("#result").hidden = false;
  }

  var busy = false;
  function ask(question) {
    question = (question || "").trim();
    if (busy) return;
    if (question.length < 3) { renderError("Please type a question of at least a few words."); return; }
    busy = true;
    $("#go").disabled = true;
    $("#q").value = question;
    setStatus("wait", ready ? "Thinking…" : "Waking the server. The first question can take up to a minute.");
    fetch(API + "/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question }),
      signal: timeout(90000)
    })
      .then(function (r) {
        if (r.status === 429) throw new Error("You've asked a lot in a short time. Please wait a few minutes and try again.");
        if (r.status === 422) throw new Error("Questions need 3 to 500 characters.");
        if (!r.ok) throw new Error("The server returned an error (" + r.status + ").");
        return r.json();
      })
      .then(function (d) { ready = true; setStatus("ok", "Server ready."); renderResult(d); })
      .catch(function (e) {
        var msg = e && e.name === "AbortError" ? "The server took too long to answer. Please try again." :
          (e && e.message && e.message.indexOf("Failed to fetch") === -1 ? e.message : "Couldn't reach the server. Please try again in a moment.");
        setStatus("bad", "Something went wrong.");
        renderError(msg);
      })
      .then(function () { busy = false; $("#go").disabled = false; });
  }

  function chips(id, list, cls) {
    $(id).innerHTML = list.map(function (q, i) {
      return "<button type='button' class='ghost" + (cls ? " " + cls : "") + "' data-i='" + i + "'>" + esc(q) + "</button>";
    }).join("");
    $$(id + " button").forEach(function (b) {
      b.addEventListener("click", function () { ask(list[+b.getAttribute("data-i")]); });
    });
  }

  chips("#samples", SAMPLES, "");
  chips("#misses", MISSES, "miss");
  $("#form").addEventListener("submit", function (e) { e.preventDefault(); ask($("#q").value); });
  wake();
})();
