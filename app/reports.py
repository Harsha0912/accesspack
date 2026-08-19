"""VPAT 2.5-shaped markdown/PDF and EAA statement HTML/PDF."""
from __future__ import annotations
import io
from xml.sax.saxutils import escape as xml_escape
from fpdf import FPDF
from app.config import DISCLAIMER, EN301549_NOTE, TOOL_NAME, TOOL_VERSION
from app.wcag import conformance_table
Q = chr(34)

def _latin(text):
    if text is None:
        return ""
    return str(text).encode("latin-1", "replace").decode("latin-1")

def generate_vpat_markdown(scan, company=None):
    org = company or "[Organization name]"
    url = scan.get("final_url") or scan.get("requested_url") or ""
    summary = scan.get("summary") or {}
    impact = scan.get("impact_counts") or {}
    rows = conformance_table(scan.get("violations") or [])
    out = []
    out.append("# VPAT 2.5 draft - " + TOOL_NAME)
    out.append("")
    out.append("> " + DISCLAIMER)
    out.append("")
    out.append("**Not a certified VPAT. Not a legal determination. Not a human WCAG/EAA audit.**")
    out.append("")
    out.append("## Product")
    out.append("")
    out.append("- Organization: " + org)
    out.append("- Product / URL: " + url)
    out.append("- Report date (UTC): " + str(scan.get("scanned_at") or ""))
    out.append("- Evaluation methods: Automated HTML snapshot (" + str(scan.get("engine") or "unknown") + " " + str(scan.get("engine_version") or "") + ")")
    out.append("- Tool: " + TOOL_NAME + " " + TOOL_VERSION)
    out.append("- User-Agent: " + str(scan.get("user_agent") or ""))
    out.append("- Applicable standards: WCAG 2.2 Level A and AA; EN 301 549 (mapped note only)")
    out.append("")
    out.append("## " + EN301549_NOTE)
    out.append("")
    out.append("EN 301 549 is the harmonised European standard used under the European Accessibility Act.")
    out.append("This pack maps automated WCAG 2.2 findings as evidence. It is not a conformity assessment,")
    out.append("does not address non-web ICT clauses, and does not establish presumption of conformity.")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append("- Violations: " + str(summary.get("violations", 0)))
    out.append("- Incomplete / needs review: " + str(summary.get("incomplete", 0)))
    out.append("- Passes: " + str(summary.get("passes", 0)))
    out.append("- Inapplicable: " + str(summary.get("inapplicable", 0)))
    out.append("- Automated issue score: " + str(scan.get("score")) + " (not a conformance level)")
    out.append("- By impact: critical=" + str(impact.get("critical", 0)) + ", serious=" + str(impact.get("serious", 0)) + ", moderate=" + str(impact.get("moderate", 0)) + ", minor=" + str(impact.get("minor", 0)))
    if scan.get("fallback_note"):
        out.append("")
        out.append("Note: " + scan["fallback_note"])
    out.append("")
    out.append("## WCAG 2.2 criteria (automated mapping)")
    out.append("")
    out.append("| Criterion | Level | Name | Status | Remarks |")
    out.append("|---|---|---|---|---|")
    for row in rows:
        out.append("| " + row["id"] + " | " + row["level"] + " | " + row["name"] + " | " + row["status"] + " | " + row["remarks"].replace("|", "/") + " |")
    out.append("")
    out.append("## Findings")
    out.append("")
    viols = scan.get("violations") or []
    if not viols:
        out.append("No automated violations were reported. This does not mean the page is conformant.")
    for v in viols:
        wcag = ", ".join(v.get("wcag") or []) or "(see tags)"
        out.append("### " + str(v.get("id")) + " (" + str(v.get("impact") or "?") + ")")
        out.append("")
        out.append("- Help: " + str(v.get("help") or ""))
        out.append("- WCAG 2.2: " + wcag)
        if v.get("helpUrl"):
            out.append("- Reference: " + v["helpUrl"])
        out.append("- Nodes: " + str(len(v.get("nodes") or [])))
        out.append("")
        for n in (v.get("nodes") or [])[:15]:
            sel = ", ".join(n.get("target") or [])
            snippet = (n.get("html") or "").replace(chr(10), " ")
            out.append("  - selector: " + sel)
            out.append("    snippet: " + snippet)
        out.append("")
    out.append("## Disclaimer")
    out.append("")
    out.append(DISCLAIMER)
    out.append("")
    return chr(10).join(out) + chr(10)

def generate_statement_html(scan, company=None, email=None, date=None):
    org = company or "[Company name]"
    mail = email or "[accessibility@example.com]"
    when = date or scan.get("scanned_at") or "[date]"
    url = scan.get("final_url") or scan.get("requested_url") or "[URL]"
    summary = scan.get("summary") or {}
    items = []
    for v in (scan.get("violations") or [])[:12]:
        items.append("<li><strong>" + xml_escape(str(v.get("id"))) + "</strong> - " + xml_escape(str(v.get("help") or "")) + " (" + xml_escape(str(v.get("impact") or "")) + ")</li>")
    if not items:
        items.append("<li>No automated violations were reported. This does not mean the site is conformant.</li>")
    H = []
    H.append("<!DOCTYPE html>")
    H.append("<html lang=" + Q + "en" + Q + ">")
    H.append("<head>")
    H.append("  <meta charset=" + Q + "utf-8" + Q + ">")
    H.append("  <title>Accessibility statement (draft) - " + xml_escape(org) + "</title>")
    H.append("  <style>body{font-family:Georgia,serif;max-width:42rem;margin:2rem auto;padding:0 1.25rem;color:#1a1a1a;line-height:1.5}.banner{background:#fff3cd;border:1px solid #c9a227;padding:.75rem 1rem}h1{font-size:1.6rem}footer{margin-top:2.5rem;font-size:.9rem;color:#444}</style>")
    H.append("</head><body>")
    H.append("  <p class=" + Q + "banner" + Q + "><strong>Draft. Informational only.</strong> " + xml_escape(DISCLAIMER) + "</p>")
    H.append("  <h1>Accessibility statement</h1>")
    H.append("  <p>This is a <em>draft</em> accessibility statement generated by " + xml_escape(TOOL_NAME) + " " + xml_escape(TOOL_VERSION) + " from an automated scan of <a href=" + Q + xml_escape(url) + Q + ">" + xml_escape(url) + "</a> on " + xml_escape(str(when)) + " (UTC). It is a starting point for " + xml_escape(org) + ". It is not a legal determination, not a certified VPAT, and not a substitute for a human WCAG/EAA audit.</p>")
    H.append("  <h2>Measures to support accessibility</h2>")
    H.append("  <p>" + xml_escape(org) + " intends to provide a website that can be used by as many people as possible, including people with disabilities. This draft should be reviewed, completed, and published by the organisation.</p>")
    H.append("  <h2>Conformance status</h2>")
    H.append("  <p>The Web Content Accessibility Guidelines (WCAG) 2.2 define requirements for designers and developers. This automated scan is <strong>not</strong> a claim of conformance. Status after automated review of one HTML snapshot:</p>")
    H.append("  <ul><li>Violations: " + str(summary.get("violations", 0)) + "</li><li>Incomplete / needs review: " + str(summary.get("incomplete", 0)) + "</li><li>Passes: " + str(summary.get("passes", 0)) + "</li></ul>")
    H.append("  <h2>Findings summary</h2>")
    H.append("  <ul>" + "".join(items) + "</ul>")
    H.append("  <h2>European Accessibility Act / EN 301 549</h2>")
    H.append("  <p>" + xml_escape(EN301549_NOTE) + "</p>")
    H.append("  <p>If you are preparing an EAA statement, replace this section with your organisation official assessment, known limitations, and alternatives.</p>")
    H.append("  <h2>Feedback</h2>")
    H.append("  <p>Contact: <a href=" + Q + "mailto:" + xml_escape(mail) + Q + ">" + xml_escape(mail) + "</a></p>")
    H.append("  <p>We welcome feedback on the accessibility of this website. Please replace these placeholders before publishing.</p>")
    H.append("  <h2>Technical specifications</h2>")
    H.append("  <p>Evaluation relied on an HTML snapshot (no authenticated sessions, no JavaScript-rendered DOM). Tool: " + xml_escape(TOOL_NAME) + " " + xml_escape(TOOL_VERSION) + ". Engine: " + xml_escape(str(scan.get("engine") or "unknown")) + ".</p>")
    H.append("  <footer><p>" + xml_escape(DISCLAIMER) + "</p></footer>")
    H.append("</body></html>")
    return chr(10).join(H) + chr(10)

class _ReportPDF(FPDF):
    def __init__(self, subtitle):
        super().__init__(format="A4")
        self.subtitle = subtitle
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(30, 30, 30)
        self.cell(0, 6, _latin(TOOL_NAME.upper() + "  |  " + self.subtitle), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 40, 20)
        self.multi_cell(0, 4, _latin("INFORMATIONAL ONLY. Not a legal determination. Not a certified VPAT. Not a substitute for a human WCAG/EAA audit."))
        self.ln(2)

    def footer(self):
        self.set_y(-14)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(90, 90, 90)
        self.cell(0, 4, "Page " + str(self.page_no()) + "  |  " + TOOL_NAME + " " + TOOL_VERSION + "  |  Informational only.", align="C")

    def heading(self, text, size=13):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", size)
        self.set_text_color(20, 20, 20)
        self.ln(3)
        self.multi_cell(0, 6, _latin(text))
        self.ln(1)

    def para(self, text, size=10):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", size)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, _latin(text))
        self.ln(1)

    def kv(self, key, val):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 9)
        self.cell(40, 5, _latin(key), new_x="END", new_y="TOP")
        self.set_font("Helvetica", "", 9)
        self.multi_cell(0, 5, _latin(val))
        self.set_x(self.l_margin)

def generate_vpat_pdf(scan, company=None):
    org = company or "[Organization name]"
    url = scan.get("final_url") or scan.get("requested_url") or ""
    summary = scan.get("summary") or {}
    impact = scan.get("impact_counts") or {}
    rows = conformance_table(scan.get("violations") or [])
    pdf = _ReportPDF("VPAT 2.5 draft")
    pdf.add_page()
    pdf.heading("Voluntary Product Accessibility Template (VPAT) 2.5 - Draft", 16)
    pdf.para("This document is VPAT-shaped evidence from an automated HTML scan. It is not a certified VPAT.")
    pdf.heading("Product")
    pdf.kv("Organization", org)
    pdf.kv("Product / URL", url)
    pdf.kv("Report date (UTC)", str(scan.get("scanned_at") or ""))
    pdf.kv("Tool", TOOL_NAME + " " + TOOL_VERSION)
    pdf.kv("Engine", str(scan.get("engine") or "") + " " + str(scan.get("engine_version") or ""))
    pdf.kv("User-Agent", str(scan.get("user_agent") or ""))
    pdf.kv("Standards", "WCAG 2.2 Level A and AA; EN 301 549 (mapped note)")
    pdf.heading(EN301549_NOTE, 12)
    pdf.para("EN 301 549 is the harmonised European standard used under the European Accessibility Act. This pack maps automated WCAG 2.2 findings as evidence. It is not a conformity assessment and does not establish presumption of conformity.")
    pdf.heading("Summary")
    pdf.para("Violations: " + str(summary.get("violations", 0)) + "  |  Incomplete: " + str(summary.get("incomplete", 0)) + "  |  Passes: " + str(summary.get("passes", 0)) + "  |  Inapplicable: " + str(summary.get("inapplicable", 0)))
    pdf.para("Impact: critical=" + str(impact.get("critical", 0)) + " serious=" + str(impact.get("serious", 0)) + " moderate=" + str(impact.get("moderate", 0)) + " minor=" + str(impact.get("minor", 0)) + "  |  Automated issue score: " + str(scan.get("score")))
    if scan.get("fallback_note"):
        pdf.para(scan["fallback_note"])
    pdf.heading("WCAG 2.2 criteria")
    for row in rows:
        pdf.para(row["id"] + " " + row["level"] + "  " + row["name"] + "  -  " + row["status"], 8)
        if row["status"] != "Not Evaluated":
            pdf.para("    " + row["remarks"], 8)
    pdf.add_page()
    pdf.heading("Findings")
    viols = scan.get("violations") or []
    if not viols:
        pdf.para("No automated violations were reported. This does not mean the page is conformant.")
    for v in viols:
        wcag = ", ".join(v.get("wcag") or []) or "(see tags)"
        pdf.heading(str(v.get("id")) + "  (" + str(v.get("impact") or "?") + ")", 12)
        pdf.para(str(v.get("help") or ""))
        pdf.para("WCAG 2.2: " + wcag)
        if v.get("helpUrl"):
            pdf.para(str(v.get("helpUrl")))
        for n in (v.get("nodes") or [])[:12]:
            sel = ", ".join(n.get("target") or [])
            snippet = (n.get("html") or "").replace(chr(10), " ")
            pdf.para(sel + "  |  " + snippet, 8)
    pdf.heading("Disclaimer")
    pdf.para(DISCLAIMER)
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()

def generate_statement_pdf(scan, company=None, email=None, date=None):
    org = company or "[Company name]"
    mail = email or "[accessibility@example.com]"
    when = date or scan.get("scanned_at") or "[date]"
    url = scan.get("final_url") or scan.get("requested_url") or "[URL]"
    summary = scan.get("summary") or {}
    pdf = _ReportPDF("EAA accessibility statement draft")
    pdf.add_page()
    pdf.heading("Accessibility statement (draft)", 16)
    pdf.para("Generated by " + TOOL_NAME + " " + TOOL_VERSION + " from an automated scan of " + url + " on " + str(when) + " UTC.")
    pdf.para(DISCLAIMER)
    pdf.heading("Organisation")
    pdf.kv("Name", org)
    pdf.kv("Contact", mail)
    pdf.kv("URL", url)
    pdf.heading("Conformance status")
    pdf.para("WCAG 2.2 defines requirements for designers and developers. This automated scan is not a claim of conformance.")
    pdf.para("Violations: " + str(summary.get("violations", 0)) + "  |  Incomplete: " + str(summary.get("incomplete", 0)) + "  |  Passes: " + str(summary.get("passes", 0)))
    pdf.heading("Findings summary")
    viols = scan.get("violations") or []
    if not viols:
        pdf.para("No automated violations were reported. This does not mean the site is conformant.")
    for v in viols[:20]:
        pdf.para("- " + str(v.get("id")) + ": " + str(v.get("help") or "") + " (" + str(v.get("impact") or "") + ")")
    pdf.heading("European Accessibility Act / EN 301 549")
    pdf.para(EN301549_NOTE)
    pdf.para("If you are preparing an EAA statement, replace this section with your organisation official assessment, known limitations, and alternatives.")
    pdf.heading("Feedback")
    pdf.para("Contact " + mail + " and replace placeholders before publishing.")
    pdf.heading("Disclaimer")
    pdf.para(DISCLAIMER)
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
