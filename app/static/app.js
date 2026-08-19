(function () {
  var params = new URLSearchParams(window.location.search);
  var url = params.get("url") || "";
  var key = params.get("key") || "";
  var status = document.getElementById("status");
  var meta = document.getElementById("meta");
  var err = document.getElementById("error");
  var results = document.getElementById("results");
  var preview = document.getElementById("preview");
  if (preview) {
    preview.href = "/scan?url=" + encodeURIComponent(url || "https://example.com") + "&key=demo";
  }
  if (!url) {
    if (status) status.textContent = "No URL";
    if (err) { err.style.display = "block"; err.textContent = "Add ?url=https://example.com"; }
    return;
  }
  if (meta) meta.textContent = url;
  var headers = { "Content-Type": "application/json" };
  if (key) headers["X-Unlock-Key"] = key;
  fetch("/api/scan", { method: "POST", headers: headers, body: JSON.stringify({ url: url }) })
    .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, status: r.status, body: j }; }); })
    .then(function (res) {
      if (!res.ok) {
        if (status) status.textContent = "Failed";
        if (err) { err.style.display = "block"; err.textContent = (res.body && (res.body.detail || res.body.error)) || "Scan failed"; }
        return;
      }
      var d = res.body;
      if (status) status.textContent = d.unlocked ? "Unlocked pack" : "Free score";
      document.getElementById("page-title").textContent = d.url || url;
      var s = d.summary || {};
      document.getElementById("score").textContent = d.score == null ? "—" : String(d.score);
      document.getElementById("viol").textContent = s.violations == null ? "—" : s.violations;
      document.getElementById("inc").textContent = s.incomplete == null ? "—" : s.incomplete;
      document.getElementById("pas").textContent = s.passes == null ? "—" : s.passes;
      if (meta) {
        meta.textContent = (d.scanned_at || "") + " UTC  ·  " + (d.engine || "") + " " + (d.engine_version || "") + (d.fallback_note ? "  ·  fallback" : "");
      }
      var box = document.getElementById("issues");
      box.innerHTML = "";
      (d.top_issues || []).forEach(function (iss) {
        var el = document.createElement("div");
        el.className = "issue";
        var wcag = (iss.wcag && iss.wcag.length) ? iss.wcag.join(", ") : "";
        var cls = "impact " + (iss.impact || "");
        el.innerHTML = "<div class=id>" + escapeHtml(iss.id || "") + "</div><div><strong>" + escapeHtml(iss.help || "") + "</strong></div><div class=" + JSON.stringify(cls) + ">" + escapeHtml(iss.impact || "") + (iss.count ? " · " + iss.count + " nodes" : "") + (wcag ? " · WCAG " + escapeHtml(wcag) : "") + "</div>";
      });
      if (!(d.top_issues || []).length) {
        box.innerHTML = "<p class=muted>No automated violations in the top list. That is not a conformance claim.</p>";
      }
      results.style.display = "block";
      var paid = document.getElementById("paid");
      var locked = document.getElementById("locked");
      if (d.unlocked) {
        paid.style.display = "block";
        locked.style.display = "none";
        var q = "url=" + encodeURIComponent(url) + (key ? "&key=" + encodeURIComponent(key) : "");
        document.getElementById("dl-vpat-pdf").href = "/api/vpat.pdf?" + q;
        document.getElementById("dl-vpat-md").href = "/api/vpat.md?" + q;
        document.getElementById("dl-stmt-pdf").href = "/api/statement.pdf?" + q;
        document.getElementById("dl-stmt-html").href = "/api/statement.html?" + q;
      } else {
        paid.style.display = "none";
        locked.style.display = "block";
      }
    })
    .catch(function (e) {
      if (status) status.textContent = "Failed";
      if (err) { err.style.display = "block"; err.textContent = String(e); }
    });

  function escapeHtml(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
})();
