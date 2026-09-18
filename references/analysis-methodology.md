# Analysis Methodology Reference

## Overview
This document describes the methodology used by the Comprehensive Course Study Guide plugin for analyzing academic materials and generating study guides.

## File Classification Methodology

### Classification Categories
1. **COURSE_HANDOUT** - Official course information, policies, schedule
2. **SYLLABUS** - Topic outline, learning objectives, unit breakdown
3. **PYQ** - Previous year question papers (exams, quizzes, midterms)
4. **LECTURE_NOTES** - Textual lecture content, summaries
5. **LECTURE_SLIDES** - PPT/PPTX slide decks
6. **REFERENCE_MATERIAL** - Textbook chapters, reference books, papers
7. **ASSIGNMENT** - Homework, problem sets, projects
8. **LAB_MATERIAL** - Laboratory manuals, practical guides
9. **OTHER** - Unclassified materials

### Classification Process
1. **Filename Analysis** (weight: 30%)
   - Keywords in filename (handout, syllabus, midsem, lecture, etc.)
   - Year patterns (2023-midsem, 2024-final)
   - File extensions (.pptx → LECTURE_SLIDES)

2. **Content Analysis** (weight: 70%)
   - Keyword frequency analysis
   - Structural patterns (questions with marks, sections)
   - Document metadata
   - Confidence scoring (0.0-1.0)

3. **Conflict Resolution**
   - Explicit user syllabus > Course handout > Dedicated syllabus > Inference
   - Primary lecture material > Inferred summaries
   - PYQs describe historical exams but don't override syllabus scope

## PYQ Analysis Methodology

### Question Extraction
1. **Structural Parsing**
   - Question numbering patterns (Q1, Q2(a), 1., (a))
   - Marks indicators ([8], (10 marks))
   - Section headers (Section A, Section B)

2. **Normalization**
   - Remove formatting artifacts
   - Standardize whitespace
   - Extract marks, question numbers, sub-questions

### Repetition Detection (Three Types)

#### Type 1: Exact/Near-Exact Repetition
- **Threshold**: Levenshtein similarity ≥ 0.9
- **Evidence**: Same wording, minor variations (typos, synonyms)
- **Recording**: Occurrences, years, exam types, question numbers, marks

#### Type 2: Conceptual Repetition (Question Families)
- **Threshold**: Semantic similarity ≥ 0.7
- **Method**: Concept embedding + clustering
- **Grouping**: Same core concept, different surface forms
- **Example**: "Explain DFA minimization" vs "Describe the procedure for minimizing a deterministic finite automaton"

#### Type 3: Pattern Repetition
- **Templates**: Recurring task types
  - "Convert NFA to DFA"
  - "Construct DFA for language"
  - "Minimize DFA"
  - "Prove closure property"
  - "Construct ε-NFA"
  - "Solve recurrence"
  - "Design circuit"
- **Recording**: Frequency, papers, years, average marks, subtopics

### Topic Mapping
1. **Syllabus-Anchored**: Use syllabus hierarchy as target
2. **Keyword Matching**: Concept overlap between question and topic
3. **Confidence Scoring**: 0.0-1.0 per mapping
4. **Manual Review Flag**: Low confidence mappings flagged

### Statistical Calculations
All statistics are **observed** (not predicted):

- **Question Frequency**: Total questions on topic across all papers
- **Paper Frequency**: Distinct papers containing topic
- **Year Coverage**: Years with topic / total analyzed years
- **Total Observed Marks**: Sum of marks for topic questions
- **Mark Share**: Topic marks / total marks across all papers
- **Average Marks**: Mean marks per question on topic
- **Consecutive Years**: Maximum consecutive years topic appeared

## Material Emphasis Analysis

### Coverage Metrics (per topic)
- **Lecture Count**: Distinct lecture files covering topic
- **Slide Count**: Total slides/pages covering topic
- **Definition Count**: Distinct definitions
- **Formula Count**: Distinct mathematical formulas
- **Algorithm Count**: Distinct algorithms/procedures
- **Example Count**: Worked examples
- **Diagram Count**: Diagrams/figures
- **Repetition Score**: Cross-lecture recurrence (0-1)
- **Depth Score**: Weighted combination (0-1)

### Weighting
```
depth_score = 0.15*lecture_count_norm + 0.15*slide_count_norm + 
              0.30*repetition_score + 0.10*definition_count_norm +
              0.10*formula_count_norm + 0.10*algorithm_count_norm + 
              0.10*example_count_norm
```

## Priority Calculation

### With PYQ Data (Historical + Material)
```
combined_score = 0.7 * historical_score + 0.3 * material_score
```

### Without PYQ Data (Material Only)
```
combined_score = material_score
```

### Priority Thresholds (With PYQ)
- **VERY HIGH**: ≥ 0.75
- **HIGH**: ≥ 0.55
- **MODERATE**: ≥ 0.35
- **LOWER**: < 0.35

### Priority Thresholds (Without PYQ)
- **VERY HIGH**: ≥ 0.80
- **HIGH**: ≥ 0.60
- **MODERATE**: ≥ 0.40
- **LOWER**: < 0.40

### Evidence Requirements
Every HIGH/VERY HIGH classification must include:
- Quantitative evidence (counts, percentages, marks)
- Source references (file, page, slide)
- Qualitative description (question types, lecture emphasis)

## No-Hallucination Policy

### Never Invent:
- Previous year questions
- Marks allocations
- Dates, syllabus items
- Lecture emphasis claims
- Statistics
- Repetition claims
- Diagram content
- Source attributions

### When Evidence Insufficient:
Explicitly state:
- "Not established from supplied materials"
- "Insufficient evidence"
- "No previous-year question papers were provided"

### Language Requirements:
- "Observed historically"
- "Repeated across supplied papers"
- "High historical emphasis"
- "Material-derived emphasis"
- **AVOID**: "Guaranteed to appear", "Certain question", "Will definitely come"

## Source Traceability

### Provenance Format
Every analytical claim includes:
```
[Source: filename.pdf, page N]
[Source: lecture-XX.pptx, slide N]
[PYQ: YYYY ExamType, QN]
```

### Source Index
Final output includes complete source index with:
- File path, classification, confidence
- Pages/slides analyzed
- Items extracted
- Role in analysis

## Conflict Resolution

### Hierarchy
1. **User-provided syllabus** (explicit)
2. **Official course handout**
3. **Dedicated syllabus document**
4. **Primary lecture materials**
5. **Reference materials**
6. **Inferred from PYQs** (for pattern detection only)

### Documentation
Meaningful conflicts are documented in analysis report with:
- Conflicting sources
- Nature of conflict
- Resolution rationale