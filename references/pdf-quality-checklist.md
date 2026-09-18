# PDF Quality Checklist

## Overview
Comprehensive checklist for validating the generated study guide PDF before delivery.

## Pre-Generation Checks

### Environment
- [ ] All required dependencies installed (Playwright, Chromium, PyMuPDF, etc.)
- [ ] Node.js ≥ 18, Python ≥ 3.10
- [ ] MathJax available (local or CDN)
- [ ] Fonts installed (Inter, JetBrains Mono, Georgia)
- [ ] Sufficient disk space for output

### Input Data
- [ ] Content model (`study-guide-content.json`) exists and valid
- [ ] HTML template loads without errors
- [ ] CSS files accessible
- [ ] Diagram generators load without errors
- [ ] Source index complete

## Generation Process Checks

### HTML Rendering
- [ ] Page loads without console errors
- [ ] MathJax renders all equations (check `MathJax.startup.promise`)
- [ ] All diagrams generated and inserted
- [ ] All images loaded
- [ ] Fonts loaded (no fallback flashes)
- [ ] Custom event `study-guide-ready` fires
- [ ] No layout shift after ready

### PDF Generation (Playwright)
- [ ] Chromium launches successfully
- [ ] Page navigates to HTML file
- [ ] Waits for network idle
- [ ] Waits for MathJax ready
- [ ] Waits for study-guide-ready event
- [ ] PDF generated with correct options:
  - [ ] Format: A4
  - [ ] Margins: 20mm top/bottom, 18mm left/right
  - [ ] Print backgrounds: true
  - [ ] Prefer CSS page size: true
  - [ ] Display header/footer: true
  - [ ] Header template includes title/section
  - [ ] Footer template includes page numbers
- [ ] PDF saved to correct path
- [ ] Browser closes cleanly

## Post-Generation Automated Checks

### File Validation
- [ ] PDF file exists
- [ ] PDF file size > 100KB (reasonable for content)
- [ ] PDF readable by PyMuPDF/pdfinfo
- [ ] Page count ≥ 5 (cover + TOC + content)
- [ ] Page count ≤ 200 (sanity check)

### Text Extraction
- [ ] Full text extractable (> 1000 characters)
- [ ] No garbled/encoding issues
- [ ] Unicode characters preserved

### Content Presence (Automated)
Run `validate_pdf.py` and verify:

**Required Sections:**
- [ ] Course name appears
- [ ] Syllabus coverage stated
- [ ] All unit titles present
- [ ] All HIGH/VERY HIGH priority topic titles present
- [ ] PYQ analysis section (if PYQs available)
- [ ] Source index present
- [ ] Revision sections (formulas, definitions, algorithms)

**No Missing Critical Content:**
- [ ] No unit completely missing
- [ ] No VERY HIGH priority topic missing
- [ ] Question bank present (if PYQs)
- [ ] Disclaimer present (if no PYQs)

## Visual QA Checks (Page-by-Page)

Render pages as PNG (300 DPI) and inspect:

### Layout Issues
- [ ] **No clipped content** - Nothing cut off at page edges
- [ ] **No overflow** - Content within margins
- [ ] **No excessive whitespace** - No half-empty pages without reason
- [ ] **Consistent margins** - All pages same margins

### Page Break Quality
- [ ] **No orphan headings** - Heading not last line of page
- [ ] **No widow lines** - Paragraph not split with single line on next page
- [ ] **Tables not awkwardly split** - Header repeats, logical breaks
- [ ] **Diagrams not split** - Entire diagram on one page
- [ ] **Callout boxes not split** - Entire callout on one page
- [ ] **Question items not split** - Entire question on one page
- [ ] **Topic cards not split** - Entire topic card on one page

### Typography
- [ ] **Readable font sizes** - Minimum 8pt equivalent
- [ ] **Consistent heading sizes** - H1-H4 consistent across pages
- [ ] **Good contrast** - Text clearly readable
- [ ] **No font fallback issues** - Correct fonts rendering
- [ ] **Math equations readable** - Not pixelated, correct symbols

### Diagrams & Figures
- [ ] **SVG diagrams sharp** - No pixelation at 300 DPI
- [ ] **Diagrams fully visible** - Not clipped at edges
- [ ] **Labels readable** - All text in diagrams legible
- [ ] **Arrows visible** - Arrowheads clear
- [ ] **Legends present** - On all diagrams
- [ ] **Captions present** - Below each figure

### Tables
- [ ] **Headers repeat** on multi-page tables
- [ ] **Cells not overlapping** - Content fits in cells
- [ ] **Readable font** - Minimum 9pt
- [ ] **Borders visible** - Grid clear
- [ ] **No awkward splits** - Prefer page break before table if needed

### Headers/Footers
- [ ] **Page numbers correct** - Sequential, centered
- [ ] **Header content appropriate** - Title left, section right
- [ ] **No header/footer collision** - Not overlapping body text
- [ ] **Cover page clean** - No headers/footers on cover

### Special Pages
- [ ] **Cover page** - Full bleed, centered, no page number
- [ ] **TOC** - Page numbers placeholder (filled by PDF generator)
- [ ] **Unit starts** - Clean page break before each unit
- [ ] **Last page** - No trailing blank pages

## Content Accuracy Checks

### Source Traceability
- [ ] Every topic has source references
- [ ] PYQ appearances link to specific papers
- [ ] Diagrams have source attribution
- [ ] Source index matches classifications

### Priority Consistency
- [ ] Priority badges match calculated priorities
- [ ] Evidence summaries accurate
- [ ] Historical evidence matches PYQ analysis
- [ ] Material evidence matches lecture analysis

### No Hallucination
- [ ] No invented questions
- [ ] No invented marks
- [ ] No invented statistics
- [ ] "Not established" statements where appropriate
- [ ] Disclaimer visible if no PYQs

### Cross-References
- [ ] TOC entries match actual sections
- [ ] Internal links work (HTML version)
- [ ] Question bank references match topic content

## Regression Checks

### Comparison with Content Model
- [ ] Unit count matches
- [ ] Topic count matches
- [ ] All priority levels represented
- [ ] PYQ family count matches

### Previous Version Comparison (if applicable)
- [ ] Page count similar (±20%)
- [ ] No missing sections
- [ ] No new visual defects

## Edge Case Checks

### Minimal Content
- [ ] Works with 1 PYQ paper
- [ ] Works with 0 PYQ papers (no-PYQ mode)
- [ ] Works with minimal lecture materials
- [ ] Works with only course handout

### Large Content
- [ ] Handles 10+ units
- [ ] Handles 50+ topics
- [ ] Handles 100+ questions
- [ ] Page count scales reasonably

### Special Content
- [ ] Heavy mathematical content renders
- [ ] Many diagrams render
- [ ] Large tables paginate
- [ ] Long code blocks format

## Automated Validation Script

Run `python scripts/validate_pdf.py study-guide-output/study-guide.pdf study-guide-output/study-guide-content.json`

**Must Pass:**
- `summary.passed == true`
- `summary.critical == 0`
- `summary.major == 0`
- `automated_checks.pdf_readable == true`
- `automated_checks.text_extractable == true`
- `automated_checks.page_count_reasonable == true`
- All `sections_present` values `true`

**Acceptable:**
- `summary.minor ≤ 5`
- `summary.cosmetic ≤ 10`

**Must Fix:**
- Any `critical` or `major` issues
- Any `sections_present` false for required sections

## Repair Loop

If issues found:
1. **Categorize** by type (layout, content, visual, typography)
2. **Prioritize** critical → major → minor → cosmetic
3. **Fix** in HTML/CSS/SVG generation:
   - Layout: Adjust CSS (max-width, break-inside, margins)
   - Content: Fix data model or template
   - Visual: Adjust SVG specs or container sizing
   - Typography: Adjust font sizes in print.css
4. **Regenerate** PDF
5. **Re-validate** (max 3 iterations)

## Common Fixes

| Issue | Fix |
|-------|-----|
| Clipped SVG | Add `max-width: 100%` to `.diagram-container` |
| Orphan heading | Add `break-after: avoid-page` to heading CSS |
| Table split | Add `break-before: page` before large tables |
| Tiny math | Increase MathJax scale in print.css |
| Header collision | Increase `@page` margins |
| Blank page | Remove forced break or add content |
| Missing section | Check template conditional rendering |

## Sign-Off Criteria

**Ready for Delivery When:**
- [ ] All automated checks pass
- [ ] No critical/major visual issues
- [ ] Content complete per content model
- [ ] Source traceability verified
- [ ] Disclaimer correct for PYQ availability
- [ ] HTML source also delivered
- [ ] Generation log saved

**Delivery Package:**
```
study-guide-output/
├── study-guide.pdf          ✓ Primary deliverable
├── study-guide.html         ✓ Editable source
├── styles.css               ✓ Styling
├── print.css                ✓ Print styling
├── study-guide-content.json ✓ Content model
├── analysis-report.md       ✓ Full analysis
├── pyq-analysis.md          ✓ PYQ details
├── question-bank.md         ✓ Question bank
├── topic-priority.md        ✓ Priorities with evidence
├── source-index.md          ✓ Source provenance
├── validation-report.json   ✓ QA report
├── generation-log.txt       ✓ Full log
└── diagrams/                ✓ SVG sources
```

## Continuous Improvement

Track and document:
- False positive/negative rates in validation
- Common issue patterns
- Time per generation
- User feedback on output quality
- Edge cases encountered