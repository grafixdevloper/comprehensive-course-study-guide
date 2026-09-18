# Weightage Methodology Reference

## Overview
This document describes the evidence-based methodology for calculating topic priorities and weightage in the study guide.

## Core Principle
**Historical frequency ≠ Future certainty**

All weightage calculations are based on **observed historical data** from supplied previous-year papers. They describe what *has happened*, not what *will happen*.

## Data Sources

### Primary: PYQ Analysis (when available)
- Question frequency per topic
- Marks distribution per topic
- Year coverage
- Paper coverage
- Question type distribution
- Exam type distribution

### Secondary: Material Emphasis (always available)
- Lecture/slide count per topic
- Depth of coverage (definitions, formulas, algorithms, examples)
- Repetition across lectures
- Course handout emphasis
- Syllabus positioning

### Tertiary: Structural Indicators
- Topic centrality (prerequisites, dependencies)
- Conceptual foundationality
- Assessment likelihood (construction vs theory)

## Historical Weightage Calculation

### Factors and Weights (With PYQ Data)

| Factor | Weight | Description |
|--------|--------|-------------|
| Question Frequency | 0.25 | Total questions on topic across all papers |
| Paper Frequency | 0.20 | Distinct papers containing topic |
| Year Coverage | 0.15 | Fraction of analyzed years with topic |
| Mark Share | 0.20 | Topic marks / total marks |
| Consecutive Years | 0.10 | Max consecutive years appeared |
| Max Single Question | 0.10 | Highest marks for single question on topic |

### Normalization
Each factor is normalized to [0, 1] using min-max across all topics:
```
normalized = (value - min) / (max - min)
```
If max == min, normalized = 1.0

### Historical Score Formula
```
historical_score = Σ(weight_i × normalized_factor_i)
```

### Historical Evidence Package
For each topic, the following evidence is recorded:
```json
{
  "question_frequency": 12,
  "paper_frequency": 5,
  "year_coverage": 1.0,
  "total_observed_marks": 90,
  "mark_share": 0.20,
  "consecutive_years": 5,
  "max_marks_single_question": 15,
  "question_type_distribution": {"construction": 10, "theory": 2},
  "exam_type_distribution": {"midsem": 7, "endsem": 5}
}
```

## Material Emphasis Calculation

### Factors and Weights (Material Only)

| Factor | Weight | Description |
|--------|--------|-------------|
| Lecture Count | 0.15 | Distinct lecture files covering topic |
| Slide Count | 0.15 | Total slides/pages on topic |
| Depth Score | 0.30 | Composite coverage metric |
| Definition Count | 0.10 | Distinct definitions |
| Formula Count | 0.10 | Distinct formulas |
| Algorithm Count | 0.10 | Distinct algorithms/procedures |
| Example Count | 0.10 | Worked examples |

### Depth Score Components
```
depth_score = 0.15*lec_norm + 0.15*slide_norm + 0.30*repetition + 
              0.10*def_norm + 0.10*formula_norm + 0.10*algo_norm + 0.10*ex_norm
```

### Material Evidence Package
```json
{
  "lecture_count": 3,
  "slide_count": 35,
  "depth_score": 0.92,
  "definitions": 5,
  "formulas": 8,
  "algorithms": 2,
  "examples": 6,
  "diagrams": 8,
  "repetition_score": 0.8
}
```

## Combined Priority Score

### With PYQ Data Available
```
combined_score = 0.70 × historical_score + 0.30 × material_score
```
**Rationale**: Historical exam data is stronger predictor but material emphasis provides context for topics not yet tested or recently added.

### Without PYQ Data (Material-Derived Only)
```
combined_score = material_score
```
**Disclaimer Required**: "No previous-year question papers were provided. The topic priorities in this guide are inferred from the supplied course materials and should not be interpreted as historical exam weightage."

## Priority Labels

### With PYQ Data (Historical + Material)
| Label | Score Range | Interpretation |
|-------|-------------|----------------|
| VERY HIGH PRIORITY | ≥ 0.75 | Consistently tested, high marks, multi-year |
| HIGH PRIORITY | ≥ 0.55 | Frequently tested, significant marks |
| MODERATE PRIORITY | ≥ 0.35 | Occasional appearance, moderate marks |
| LOWER PRIORITY | < 0.35 | Rarely tested, low marks, or not in PYQs |

### Without PYQ Data (Material-Derived Only)
| Label | Score Range | Interpretation |
|-------|-------------|----------------|
| VERY HIGH PRIORITY | ≥ 0.80 | Extensive lecture coverage, core topic |
| HIGH PRIORITY | ≥ 0.60 | Strong lecture emphasis, multiple lectures |
| MODERATE PRIORITY | ≥ 0.40 | Covered in lectures, moderate depth |
| LOWER PRIORITY | < 0.40 | Brief mention, peripheral topic |

### Conservative Thresholds for Material-Only
Material-only thresholds are deliberately higher (more conservative) because:
- No external validation from exam history
- Lecture emphasis may not match exam emphasis
- Instructor preferences vary year to year

## Evidence Requirements

### Mandatory for HIGH/VERY HIGH
Every high-priority classification must include:
1. **Quantitative evidence** (counts, percentages, marks)
2. **Source references** (file, page/slide numbers)
3. **Qualitative description** (question types, lecture emphasis)

### Example Evidence Summary
```
DFA Minimization
Priority: VERY HIGH PRIORITY
Evidence:
• Appeared in 4 of 5 analyzed papers (80% paper frequency)
• 19 observed marks (18% of total observed marks)
• Appeared as both construction and theory questions
• Covered extensively in Lecture 07 (12 slides, 3 worked examples)
• Table-filling algorithm detailed in course handout p. 23
```

## No-Hallucination Rules

### Never State:
- "This topic carries X% weightage" (unless explicitly from official source)
- "This topic is guaranteed to appear"
- "Expect a question on this topic"
- "This is a sure-shot question"

### Always State:
- "Observed in X of Y papers"
- "Historically accounted for X% of marks"
- "Material-derived emphasis: HIGH"
- "No PYQ data available - priorities based on course materials"

### Language Standards:
| Instead of... | Use... |
|---------------|--------|
| "Weightage: 20%" | "Observed mark share: 20%" |
| "Important topic" | "High historical emphasis" |
| "Will come in exam" | "Repeated across supplied papers" |
| "Sure question" | "Exact repetition observed" |

## Special Cases

### Topics Not in PYQs But in Syllabus
- Material-derived priority only
- Flagged as "Not historically tested" in evidence
- May still be HIGH if core prerequisite

### Topics in PYQs But Not in Current Syllabus
- Included in analysis for pattern detection
- Marked as "Outside current syllabus"
- Not prioritized for current exam

### New Topics (Added This Year)
- Material-derived priority only
- Explicitly flagged as "New topic - no historical data"
- Priority based on lecture emphasis and prerequisites

### Removed Topics (Not in Current Syllabus)
- Excluded from priority calculation
- May appear in "Prerequisite/Context" section
- Not prioritized

## Validation

### Sanity Checks
1. **Sum of mark shares ≈ 1.0** (allowing for unmapped questions)
2. **Priority distribution reasonable** (not all VERY HIGH)
3. **Core prerequisites ≥ dependent topics** (usually)
4. **Consistency check**: Same topic, different subtopics → similar priority

### Manual Review Triggers
- Topic with 0 historical but VERY HIGH material → verify
- Topic with HIGH historical but LOW material → verify syllabus alignment
- Large discrepancy between historical and material scores → investigate

## Output Format

### Topic Priority Entry
```json
{
  "topic_id": "unit-1.topic-3",
  "topic_title": "DFA Minimization",
  "unit_number": 1,
  "priority": "VERY HIGH PRIORITY",
  "priority_score": 0.87,
  "historical_evidence": { ... },
  "material_evidence": { ... },
  "evidence_summary": [
    "Appeared in 4 of 5 analyzed papers",
    "19 observed marks (18% of total)",
    "Appeared as both construction and theory",
    "Covered extensively in Lecture 07 (12 slides)"
  ],
  "pyq_available": true
}
```

### Overall Priority Distribution
```json
{
  "priority_distribution": {
    "VERY HIGH PRIORITY": 3,
    "HIGH PRIORITY": 7,
    "MODERATE PRIORITY": 8,
    "LOWER PRIORITY": 4
  },
  "pyq_available": true,
  "calculation_timestamp": "2025-09-18T10:30:00Z"
}
```

## Limitations

1. **Sample Size**: Small number of papers (3-5 typical) → high variance
2. **Exam Evolution**: Instructor changes, curriculum updates
3. **Topic Granularity**: Coarse topics may mask subtopic variation
4. **Marks Variability**: Same topic, different marks across papers
5. **Selection Bias**: Only supplied papers analyzed

## Transparency Requirements

The final study guide must clearly communicate:
1. Number of papers analyzed
2. Years covered
3. Whether PYQ data was available
4. Methodology used (historical vs material-derived)
5. Disclaimer about predictive value
6. Evidence for each high-priority topic