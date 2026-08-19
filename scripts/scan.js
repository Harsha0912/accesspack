#!/usr/bin/env node
"use strict";

const fs = require("fs");
const { JSDOM } = require("jsdom");
const axeCore = require("axe-core");

function slim(rules) {
  return (rules || []).map((r) => ({
    id: r.id,
    impact: r.impact,
    help: r.help,
    helpUrl: r.helpUrl,
    description: r.description,
    tags: r.tags,
    nodes: (r.nodes || []).slice(0, 25).map((n) => ({
      target: n.target,
      html: String(n.html || "").slice(0, 240),
      failureSummary: n.failureSummary,
    })),
  }));
}

async function main() {
  const url = process.argv[2] || "https://scanned.invalid/";
  const html = fs.readFileSync(0, "utf8");
  if (!String(html).trim()) {
    process.stderr.write(JSON.stringify({ error: "empty html" }));
    process.exit(2);
  }
  const dom = new JSDOM(html, {
    url,
    pretendToBeVisual: true,
    runScripts: "outside-only",
    resources: "usable",
  });
  const { window } = dom;
  window.eval(axeCore.source);
  const results = await window.axe.run(window.document, {
    resultTypes: ["violations", "incomplete", "passes", "inapplicable"],
    runOnly: {
      type: "tag",
      values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"],
    },
  });
  const out = {
    engine: "axe-core",
    engineVersion: axeCore.version,
    url: results.url,
    timestamp: results.timestamp,
    violations: slim(results.violations),
    incomplete: slim(results.incomplete),
    passes: (results.passes || []).map((r) => ({ id: r.id, help: r.help, tags: r.tags })),
    inapplicable: (results.inapplicable || []).map((r) => r.id),
  };
  process.stdout.write(JSON.stringify(out));
}

main().catch((err) => {
  process.stderr.write(JSON.stringify({ error: String(err && err.message ? err.message : err) }));
  process.exit(1);
});
