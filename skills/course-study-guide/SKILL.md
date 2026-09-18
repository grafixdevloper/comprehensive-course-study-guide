---
name: course-study-guide
description: Analyze an entire directory of academic course materials and produce an exam-focused, comprehensive, professionally designed study guide as a PDF
category: educational
tags:
  - study-guide
  - exam-preparation
  - academic-analysis
  - pyq-analysis
  - pdf-generation
  - course-materials
  - question-bank
version: "1.0.0"
---

# Comprehensive Course Study Guide Generator

This skill orchestrates the complete workflow for analyzing academic course materials and generating a production-ready PDF study guide.

## Usage

```bash
# Standard usage
/comprehensive-course-study-guide:course-study-guide ./course-materials

# With explicit syllabus specification
/comprehensive-course-study-guide:course-study-guide ./course-materials

Syllabus:
UNIT 1: Regular Languages and Finite Automata
UNIT 2: Context-Free Grammars and Pushdown Automata
UNIT 3: Turing Machines and Computability
Midsem syllabus only.

# Current directory (if no argument provided)
/comprehensive-course-study-guide:course-study-guide
```

## Argument Parsing

The skill accepts the following argument patterns:

1. **Directory path** (required unless using current directory): First non-flag argument is the input directory
2. **Syllabus specification** (optional): Everything after a blank line or "Syllabus:" is treated as the user-provided syllabus
3. **Flags** (optional):
   - `--web` - Enable optional web research for supplementary material
   - `--pdf-only` - Generate only PDF, not HTML source
   - `--keep-work` - Retain intermediate workspace after completion
   - `--verbose` - Verbose logging

## Workflow Overview

```
Input directory
      ↓
1. INSPECT ENVIRONMENT → Check dependencies
      ↓
2. INVENTORY FILES → Recursive scan, classify by type
      ↓
3. EXTRACT MATERIALS → Text, structure, metadata from all files
      ↓
4. CLASSIFY MATERIALS → COURSE_HANDOUT, SYLLABUS, PYQ, LECTURE_NOTES, etc.
      ↓
5. IDENTIFY SYLLABUS → Priority: user > handout > dedicated > inference
      ↓
6. EXTRACT & NORMALIZE PYQ QUESTIONS → Structural representation
      ↓
7. ANALYZE PYQ PATTERNS → Exact repetition, conceptual, pattern families
      ↓
8. BUILD TOPIC HIERARCHY → Syllabus-aligned canonical topics
      ↓
9. MAP QUESTIONS TO TOPICS → Evidence-based mapping
      ↓
10. CALCULATE PRIORITY → Historical + material-derived evidence
      ↓
11. ANALYZE LECTURE EMPHASIS → Coverage depth, repetition, examples
      ↓
12. GENERATE CONTENT → Comprehensive notes per topic
      ↓
13. BUILD STRUCTURED DOCUMENT MODEL → study-guide-content.json
      ↓
14. RENDER HTML → Component-based templates + MathJax + SVG
      ↓
15. RENDER PDF → Playwright + Chromium
      ↓
16. VISUAL QA → Screenshot pages, detect issues
      ↓
17. REPAIR & REGENERATE → Auto-fix layout problems
      ↓
18. VALIDATE FINAL PDF → Content completeness check
      ↓
19. DELIVER → study-guide.pdf + supporting files
```

## Output Structure

```
study-guide-output/
├── study-guide.pdf              # Primary deliverable
├── study-guide.html             # Editable HTML source
├── styles.css                   # General styling
├── print.css                    # Print-specific CSS
├── study-guide-content.json     # Structured content model
├── analysis-report.md           # Full analysis report
├── pyq-analysis.md              # PYQ analysis details
├── question-bank.md             # Structured question bank
├── topic-priority.md            # Priority classifications with evidence
├── source-index.md              # Source provenance index
├── diagrams/                    # Generated SVG diagrams
├── images/                      # Copied/processed images
└── generation-log.txt           # Full generation log
```

## Key Principles

- **Source traceability**: Every claim links to source file + page/slide
- **No hallucination**: Insufficient evidence → explicit statement
- **Academic integrity**: Historical frequency ≠ future certainty
- **Separation of concerns**: Analysis → Content Model → Presentation → PDF
- **Visual validation**: PDF must pass automated + visual QA
- **Offline-capable**: No external CDN dependencies after install

## Subagents

- `material-analyst` - Lecture material extraction and topic discovery
- `pyq-analyst` - Question extraction, normalization, repetition analysis
- `content-writer` - Comprehensive academic content synthesis
- `document-reviewer` - HTML/PDF visual and content QA

## Intermediate Workspace

All intermediate data stored in `.study-guide-work/`:
- `inventory.json` - File inventory with classifications
- `sources.json` - Extracted content with provenance
- `syllabus.json` - Parsed syllabus hierarchy
- `topics.json` - Canonical topic hierarchy
- `questions.json` - Normalized question database
- `pyq-analysis.json` - Repetition and pattern analysis
- `topic-priority.json` - Evidence-based priorities
- `material-emphasis.json` - Lecture coverage analysis
- `study-guide-outline.json` - Document structure
- `study-guide-content.json` - Final content model

## Dependencies

Required:
- Python 3.10+ with: pymupdf, python-docx, python-pptx
- Node.js 18+ with: playwright (chromium)
- System: pdftotext, pdfinfo (poppler-utils)

Optional:
- pandoc (for additional format support)
- tesseract (for OCR of image-only PDFs)
- weasyprint (fallback PDF renderer)
- typst (alternative PDF renderer)