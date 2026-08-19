"""WCAG 2.2 A/AA criteria and axe-core tag mapping."""

from __future__ import annotations

# (id, level, name)
WCAG22_CRITERIA = [
    ("1.1.1", "A", "Non-text Content"),
    ("1.2.1", "A", "Audio-only and Video-only (Prerecorded)"),
    ("1.2.2", "A", "Captions (Prerecorded)"),
    ("1.2.3", "A", "Audio Description or Media Alternative (Prerecorded)"),
    ("1.2.4", "AA", "Captions (Live)"),
    ("1.2.5", "AA", "Audio Description (Prerecorded)"),
    ("1.3.1", "A", "Info and Relationships"),
    ("1.3.2", "A", "Meaningful Sequence"),
    ("1.3.3", "A", "Sensory Characteristics"),
    ("1.3.4", "AA", "Orientation"),
    ("1.3.5", "AA", "Identify Input Purpose"),
    ("1.4.1", "A", "Use of Color"),
    ("1.4.2", "A", "Audio Control"),
    ("1.4.3", "AA", "Contrast (Minimum)"),
    ("1.4.4", "AA", "Resize Text"),
    ("1.4.5", "AA", "Images of Text"),
    ("1.4.10", "AA", "Reflow"),
    ("1.4.11", "AA", "Non-text Contrast"),
    ("1.4.12", "AA", "Text Spacing"),
    ("1.4.13", "AA", "Content on Hover or Focus"),
    ("2.1.1", "A", "Keyboard"),
    ("2.1.2", "A", "No Keyboard Trap"),
    ("2.1.4", "A", "Character Key Shortcuts"),
    ("2.2.1", "A", "Timing Adjustable"),
    ("2.2.2", "A", "Pause, Stop, Hide"),
    ("2.3.1", "A", "Three Flashes or Below Threshold"),
    ("2.4.1", "A", "Bypass Blocks"),
    ("2.4.2", "A", "Page Titled"),
    ("2.4.3", "A", "Focus Order"),
    ("2.4.4", "A", "Link Purpose (In Context)"),
    ("2.4.5", "AA", "Multiple Ways"),
    ("2.4.6", "AA", "Headings and Labels"),
    ("2.4.7", "AA", "Focus Visible"),
    ("2.4.11", "AA", "Focus Not Obscured (Minimum)"),
    ("2.5.1", "A", "Pointer Gestures"),
    ("2.5.2", "A", "Pointer Cancellation"),
    ("2.5.3", "A", "Label in Name"),
    ("2.5.4", "A", "Motion Actuation"),
    ("2.5.7", "AA", "Dragging Movements"),
    ("2.5.8", "AA", "Target Size (Minimum)"),
    ("3.1.1", "A", "Language of Page"),
    ("3.1.2", "AA", "Language of Parts"),
    ("3.2.1", "A", "On Focus"),
    ("3.2.2", "A", "On Input"),
    ("3.2.3", "AA", "Consistent Navigation"),
    ("3.2.4", "AA", "Consistent Identification"),
    ("3.2.6", "A", "Consistent Help"),
    ("3.3.1", "A", "Error Identification"),
    ("3.3.2", "A", "Labels or Instructions"),
    ("3.3.3", "AA", "Error Suggestion"),
    ("3.3.4", "AA", "Error Prevention (Legal, Financial, Data)"),
    ("3.3.7", "A", "Redundant Entry"),
    ("3.3.8", "AA", "Accessible Authentication (Minimum)"),
    ("4.1.2", "A", "Name, Role, Value"),
    ("4.1.3", "AA", "Status Messages"),
]

CRITERIA_BY_ID = {cid: (level, name) for cid, level, name in WCAG22_CRITERIA}

AXE_RULE_CRITERIA = {
    "image-alt": ["1.1.1"],
    "input-image-alt": ["1.1.1"],
    "object-alt": ["1.1.1"],
    "area-alt": ["1.1.1"],
    "role-img-alt": ["1.1.1"],
    "svg-img-alt": ["1.1.1"],
    "image-redundant-alt": ["1.1.1"],
    "video-caption": ["1.2.2"],
    "definition-list": ["1.3.1"],
    "dlitem": ["1.3.1"],
    "list": ["1.3.1"],
    "listitem": ["1.3.1"],
    "td-headers-attr": ["1.3.1"],
    "th-has-data-cells": ["1.3.1"],
    "nested-interactive": ["1.3.1", "4.1.2"],
    "autocomplete-valid": ["1.3.5"],
    "color-contrast": ["1.4.3"],
    "color-contrast-enhanced": ["1.4.3"],
    "link-in-text-block": ["1.4.1"],
    "meta-viewport": ["1.4.4"],
    "blink": ["2.2.2"],
    "meta-refresh": ["2.2.1"],
    "bypass": ["2.4.1"],
    "skip-link": ["2.4.1"],
    "frame-title": ["2.4.1", "4.1.2"],
    "frame-title-unique": ["2.4.1"],
    "document-title": ["2.4.2"],
    "link-name": ["2.4.4", "4.1.2"],
    "label-content-name-mismatch": ["2.5.3"],
    "html-has-lang": ["3.1.1"],
    "html-lang-valid": ["3.1.1"],
    "html-xml-lang-mismatch": ["3.1.2"],
    "valid-lang": ["3.1.2"],
    "label": ["1.3.1", "3.3.2", "4.1.2"],
    "label-title-only": ["3.3.2"],
    "form-field-multiple-labels": ["3.3.2"],
    "select-name": ["4.1.2", "3.3.2"],
    "button-name": ["4.1.2"],
    "input-button-name": ["4.1.2"],
    "input-image-alt": ["1.1.1", "4.1.2"],
    "aria-allowed-attr": ["4.1.2"],
    "aria-command-name": ["4.1.2"],
    "aria-hidden-body": ["4.1.2"],
    "aria-hidden-focus": ["4.1.2"],
    "aria-input-field-name": ["4.1.2"],
    "aria-required-attr": ["4.1.2"],
    "aria-required-children": ["1.3.1", "4.1.2"],
    "aria-required-parent": ["1.3.1", "4.1.2"],
    "aria-roles": ["4.1.2"],
    "aria-toggle-field-name": ["4.1.2"],
    "aria-valid-attr": ["4.1.2"],
    "aria-valid-attr-value": ["4.1.2"],
    "duplicate-id-active": ["4.1.2"],
    "duplicate-id-aria": ["4.1.2"],
    "empty-heading": ["1.3.1", "2.4.6"],
    "heading-order": ["1.3.1", "2.4.6"],
    "page-has-heading-one": ["1.3.1", "2.4.6"],
    "scrollable-region-focusable": ["2.1.1"],
    "accesskeys": ["2.1.1"],
    "tabindex": ["2.1.1", "2.4.3"],
}

def parse_wcag_tag(tag):
    if not tag or not tag.startswith("wcag"):
        return None
    rest = tag[4:]
    if not rest.isdigit() or len(rest) < 3:
        return None
    if len(rest) == 3:
        return rest[0] + "." + rest[1] + "." + rest[2]
    if len(rest) == 4:
        return rest[0] + "." + rest[1] + "." + rest[2:]
    return None

def criteria_for_rule(rule_id, tags=None):
    found = []
    for cid in AXE_RULE_CRITERIA.get(rule_id, []):
        if cid not in found:
            found.append(cid)
    for tag in tags or []:
        cid = parse_wcag_tag(tag)
        if cid and cid in CRITERIA_BY_ID and cid not in found:
            found.append(cid)
    return found

def conformance_table(violations):
    hit = {}
    for v in violations or []:
        for cid in criteria_for_rule(v.get("id"), v.get("tags")):
            hit.setdefault(cid, []).append(v)
    rows = []
    for cid, level, name in WCAG22_CRITERIA:
        items = hit.get(cid, [])
        if items:
            status = "Does Not Support" if len(items) >= 2 else "Partially Supports"
            remarks = "; ".join(sorted({i.get("id", "?") for i in items}))
        else:
            status = "Not Evaluated"
            remarks = "No automated rule mapped to this criterion in this scan."
        rows.append({
            "id": cid,
            "level": level,
            "name": name,
            "status": status,
            "remarks": remarks,
            "violation_count": len(items),
        })
    return rows
