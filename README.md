# Comprehensive Course Study Guide Generator

A production-ready Claude Code plugin that analyzes academic course materials and previous-year question papers to generate comprehensive, exam-focused, professionally formatted PDF study guides.

## Features

- **Multi-format Support**: PDF, PPT/PPTX, DOC/DOCX, Markdown, Text, Images
- **Intelligent Classification**: Automatically identifies syllabus, course handouts, PYQs, lecture materials
- **Deep PYQ Analysis**: Detects exact repetitions, conceptual question families, and recurring patterns
- **Evidence-based Priorities**: Calculates topic priorities from historical exam data + lecture emphasis
- **Comprehensive Content Synthesis**: Generates definitions, formulas, algorithms, worked examples, diagrams
- **Professional PDF Output**: Publication-ready with MathJax math, SVG diagrams, proper typography
- **Visual QA Loop**: Automated PDF validation with screenshot-based inspection
- **Source Traceability**: Every claim linked to source file + page/slide number
- **Academic Integrity**: Clear distinction between historical evidence and predictions

## Installation

```bash
# Install plugin into ~/.claude/plugins/comprehensive-course-study-guide
npx @grafixdevloper/comprehensive-course-study-guide

# Install dependencies
pip install pymupdf python-docx python-pptx pdfplumber
npx playwright install chromium

# Optional dependencies
pip install pandas openpyxl pillow pytesseract
# sudo apt install poppler-utils tesseract-ocr pandoc
```

## Quick Start

```bash
# Start Claude with the plugin
claude --plugin-dir ~/.claude/plugins/comprehensive-course-study-guide

# Generate study guide from course materials
/comprehensive-course-study-guide:course-study-guide ./course-materials
```

### With Explicit Syllabus

```bash
/comprehensive-course-study-guide:course-study-guide ./course-materials

Syllabus:
UNIT 1: Regular Languages and Finite Automata
UNIT 2: Context-Free Grammars
Midsem syllabus only.
```

## Usage

### Standard Invocation

```bash
/comprehensive-course-study-guide:course-study-guide <input_directory>
```

### Arguments

| Argument | Description |
|----------|-------------|
| `<input_directory>` | Path to course materials (default: current directory) |
| `Syllabus:` (in message body) | Explicit syllabus specification |
| `--web` | Enable web research for supplementary material |
| `--pdf-only` | Generate only PDF, not HTML source |
| `--keep-work` | Retain intermediate workspace after completion |
| `--verbose` | Verbose logging |

### Syllabus Format

```
Syllabus:
UNIT 1: Topic Name
  - Subtopic 1
  - Subtopic 2
UNIT 2: Another Topic
Midsem syllabus only.
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
├── validation-report.json       # QA validation results
├── generation-log.txt           # Full generation log
├── diagrams/                    # Generated SVG diagrams
└── images/                      # Copied/processed images
```

## Workflow

```
Input Directory
       ↓
1. INSPECT ENVIRONMENT → Check dependencies
       ↓
2. INVENTORY FILES → Recursive scan, classify by type
       ↓
3. EXTRACT MATERIALS → Text, structure, metadata with provenance
       ↓
4. CLASSIFY MATERIALS → COURSE_HANDOUT, SYLLABUS, PYQ, LECTURE_NOTES, etc.
       ↓
5. IDENTIFY SYLLABUS → Priority: user > handout > dedicated > inference
       ↓
6. NORMALIZE PYQ QUESTIONS → Structural representation
       ↓
7. ANALYZE PYQ PATTERNS → Exact repetition, conceptual families, pattern families
       ↓
8. BUILD TOPIC HIERARCHY → Syllabus-aligned canonical topics
       ↓
9. MAP QUESTIONS TO TOPICS → Evidence-based mapping
       ↓
10. CALCULATE PRIORITIES → Historical + material-derived evidence
       ↓
11. ANALYZE LECTURE EMPHASIS → Coverage depth, repetition, examples
       ↓
12. GENERATE CONTENT → Comprehensive notes per topic
       ↓
13. BUILD CONTENT MODEL → study-guide-content.json
       ↓
14. RENDER HTML → Component templates + MathJax + SVG
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

## Architecture

### Plugin Structure
```
comprehensive-course-study-guide/
├── .claude-plugin/plugin.json    # Plugin metadata
├── skills/course-study-guide/    # Main skill (orchestration)
├── agents/                       # Subagents
│   ├── material-analyst.md       # Lecture analysis
│   ├── pyq-analyst.md            # PYQ analysis
│   ├── content-writer.md         # Content synthesis
│   └── document-reviewer.md      # QA/validation
├── scripts/                      # Processing pipeline
│   ├── inspect_environment.py
│   ├── inventory_files.py
│   ├── extract_materials.py
│   ├── classify_materials.py
│   ├── normalize_questions.py
│   ├── analyze_pyqs.py
│   ├── build_topic_map.py
│   ├── calculate_priority.py
│   ├── generate_document.py
│   ├── render_pdf.js
│   ├── render_pdf_pages.js
│   └── validate_pdf.py
├── templates/                    # HTML/CSS templates
│   ├── study-guide.html
│   ├── styles.css
│   ├── print.css
│   └── components/
├── diagrams/                     # SVG diagram generators
│   ├── automata.js
│   ├── flowcharts.js
│   ├── block-diagrams.js
│   ├── graphs.js
│   ├── trees.js
│   └── process-diagrams.js
├── references/                   # Methodology documentation
├── tests/fixtures/               # Test data
└── README.md
```

### Separation of Concerns

```
ACADEMIC ANALYSIS (scripts + agents)
         ↓
STRUCTURED CONTENT MODEL (study-guide-content.json)
         ↓
DOCUMENT PRESENTATION (templates + CSS)
         ↓
PDF RENDERING (Playwright + Chromium)
         ↓
VISUAL QA (screenshot + validation)
```

## PYQ Analysis Details

### Three Repetition Types

1. **Exact Repetition** (≥90% similarity)
   - Same wording across papers
   - Tracks: occurrences, years, exam types, marks

2. **Conceptual Repetition** (Question Families)
   - Different wording, same concept
   - Semantic clustering (≥70% similarity)
   - Example: "DFA minimization" variants

3. **Pattern Repetition**
   - Recurring task templates
   - "Convert NFA to DFA", "Prove non-regularity", etc.
   - Frequency, papers, years, avg marks

### Statistics (Observed, Not Predicted)
- Question frequency
- Paper frequency  
- Year coverage
- Mark share
- Consecutive years
- Question type distribution

## Priority System

| Priority | With PYQs | Without PYQs | Basis |
|----------|-----------|--------------|-------|
| VERY HIGH | ≥0.75 | ≥0.80 | Consistent historical + material |
| HIGH | ≥0.55 | ≥0.60 | Frequent historical + strong material |
| MODERATE | ≥0.35 | ≥0.40 | Occasional historical / moderate material |
| LOWER | <0.35 | <0.40 | Rare/absent historical, minimal material |

## Document Design

- **A4 paper**, professional margins
- **Georgia/Inter** font stack
- **MathJax** for LaTeX math (`\(...\)`, `\[...\]`)
- **SVG diagrams** (vector, crisp at any size)
- **Color-coded callouts** for PYQ repetitions, priorities, tips
- **Page headers/footers** with page numbers
- **Print-optimized CSS** with proper page breaks

## Dependencies

### Required
- Python 3.10+
  - `pymupdf` (PyMuPDF)
  - `python-docx`
  - `python-pptx`
- Node.js 18+
  - `playwright` with Chromium
- System
  - `pdftotext`, `pdfinfo` (poppler-utils)

### Optional
- `pandoc` (additional format support)
- `tesseract-ocr` (image OCR)
- `weasyprint` (fallback PDF renderer)
- `typst` (alternative PDF renderer)

## Academic Integrity

The plugin strictly maintains:
- **No hallucination**: Never invents questions, marks, statistics
- **Traceability**: Every claim → source file + page/slide
- **Historical ≠ Predictive**: "Observed in 4 of 5 papers" not "Will appear"
- **Clear disclaimers**: When no PYQs provided
- **Conflict documentation**: When sources disagree

## Testing

```bash
# Run with test fixtures
/comprehensive-course-study-guide:course-study-guide ./tests/fixtures/sample-course
```

Test fixtures include:
- Syllabus (midsem only)
- Course handout
- 2 PYQ papers (2022, 2023) with exact + conceptual repetitions
- 2 lecture files with definitions, formulas, examples

## Configuration

Edit `.claude-plugin/plugin.json` for:
- Dependency versions
- Permission settings
- Script entry points

## Troubleshooting

### "Playwright/Chromium not found"
```bash
npx playwright install chromium
```

### "Module not found: fitz"
```bash
pip install pymupdf
```

### "PDF generation timeout"
Increase timeout in `render_pdf.js` or check for infinite MathJax loading

### "Math not rendering"
Ensure MathJax CDN accessible or use local copy

### Visual QA failures
Check `validation-report.json` for specific issues, adjust CSS/templates

## License

MIT License - See LICENSE file

## Contributing

1. Fork the plugin
2. Add features/fixes
3. Update methodology docs in `references/`
4. Add test cases in `tests/fixtures/`
5. Submit PR

## Support

- Check `generation-log.txt` for detailed logs
- Review `validation-report.json` for QA issues
- See `references/` for methodology details
- File issues with sample materials (redacted)