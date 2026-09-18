# Repetition Detection Reference

## Overview
This document details the algorithms and approaches for detecting three types of repetition in previous-year question papers.

## Three Types of Repetition

### 1. Exact / Near-Exact Repetition
**Definition**: Same or nearly identical wording appearing across multiple papers.

**Detection Algorithm**:
```
For each pair of questions (q1, q2):
  similarity = LevenshteinRatio(normalize(q1.text), normalize(q2.text))
  If similarity ≥ 0.90:
    Group into same cluster
```

**Normalization**:
- Remove marks indicators: `[8]`, `(10 marks)`
- Remove question numbers: `Q1(a)`, `2.`
- Standardize whitespace
- Lowercase for comparison
- Remove punctuation variations

**Clustering**:
- Transitive clustering (if A≈B and B≈C, then A≈B≈C)
- Each cluster gets canonical question (first occurrence)
- Record: cluster_id, canonical_text, member_questions, years, exam_types, marks

**Output Format**:
```json
{
  "cluster_id": "exact-001",
  "canonical_question": "Explain the pumping lemma for regular languages.",
  "occurrences": 3,
  "years": [2021, 2023, 2024],
  "exam_types": ["midsem", "endsem", "midsem"],
  "question_numbers": ["Q2(a)", "Q3(b)", "Q1(c)"],
  "marks": [5, 5, 8],
  "topic": "Regular Languages",
  "subtopic": "Pumping Lemma",
  "member_ids": ["2021-midsem-Q2-a", "2023-endsem-Q3-b", "2024-midsem-Q1-c"]
}
```

### 2. Conceptual Repetition (Question Families)
**Definition**: Different wording testing the same core concept.

**Detection Algorithm**:
```
1. Group questions by canonical_concept_id (from normalization)
2. Within each concept group, compute pairwise semantic similarity
3. Cluster using threshold ≥ 0.70
4. Each cluster = one question family
```

**Canonical Concept ID Generation**:
```
concepts = extract_concepts(question_text)
concept_id = sort(concepts)[:3].join('-') + '-' + question_type
Example: "dfa-construction-ends-with"
```

**Semantic Similarity**:
- TF-IDF vectors over normalized question texts
- Cosine similarity
- Or: Sentence embeddings (if available)
- Fallback: Keyword overlap (Jaccard on concept sets)

**Family Structure**:
```json
{
  "family_id": "fam-001",
  "canonical_name": "DFA Construction for Suffix Languages",
  "concept": "Construct DFA for language ending with specific pattern",
  "members": [
    {"id": "2022-midsem-Q3", "text": "Construct DFA for strings ending in 01", "year": 2022, "exam": "midsem", "marks": 8},
    {"id": "2023-endsem-Q4", "text": "Design DFA accepting strings ending with 101", "year": 2023, "exam": "endsem", "marks": 10},
    {"id": "2024-midsem-Q2", "text": "Build DFA for L = {w | w ends with 00}", "year": 2024, "exam": "midsem", "marks": 8}
  ],
  "occurrences": 3,
  "years": [2022, 2023, 2024],
  "topic": "Finite Automata",
  "subtopic": "DFA Construction",
  "pattern": "dfa-construction-suffix"
}
```

### 3. Pattern Repetition
**Definition**: Recurring task templates across different specific questions.

**Pattern Catalog** (extensible):
| Pattern ID | Description | Example Questions |
|------------|-------------|-------------------|
| `dfa-construction` | Construct DFA for given language | "Construct DFA for L={w|w ends with 01}" |
| `nfa-to-dfa` | Convert NFA to equivalent DFA | "Convert the given NFA to DFA" |
| `dfa-minimization` | Minimize given DFA | "Minimize the following DFA" |
| `regex-to-fa` | Convert regex to FA | "Convert (0+1)*01 to NFA" |
| `fa-to-regex` | Convert FA to regex | "Find regex for the given DFA" |
| `pumping-lemma` | Prove non-regularity using pumping lemma | "Prove {0^n 1^n} is not regular" |
| `closure-proof` | Prove closure property | "Prove regular languages closed under intersection" |
| `cross-product` | Construct product automaton | "Construct DFA for L1 ∩ L2" |
| `myhill-nerode` | Apply Myhill-Nerode theorem | "Find equivalence classes for L" |
| `cfg-construction` | Construct CFG for language | "Give CFG for {a^n b^n}" |
| `pda-construction` | Construct PDA for CFL | "Design PDA for {a^n b^n}" |
| `ambiguity` | Show grammar is ambiguous | "Show the grammar is ambiguous" |

**Detection**:
```
For each question:
  pattern_id = canonical_concept_id (from normalization)
  Increment pattern_counts[pattern_id]

Filter: pattern_counts[pattern_id] ≥ 2
```

**Statistics per Pattern**:
```json
{
  "pattern_id": "dfa-construction",
  "description": "Construct DFA for given language",
  "frequency": 12,
  "papers": 5,
  "years": [2020, 2021, 2022, 2023, 2024],
  "avg_marks": 7.5,
  "subtopics": ["DFA Construction", "NFA to DFA", "Suffix Languages"],
  "question_types": {"construction": 10, "theory": 2}
}
```

## Implementation Notes

### Similarity Functions

**Levenshtein Ratio** (for exact):
```python
def levenshtein_ratio(s1, s2):
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    return 1 - distance / max_len if max_len > 0 else 1.0
```

**Cosine Similarity** (for conceptual):
```python
def cosine_similarity(vec1, vec2):
    dot = sum(a*b for a,b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a*a for a in vec1))
    norm2 = math.sqrt(sum(b*b for b in vec2))
    return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
```

### Clustering Algorithm

**Hierarchical Agglomerative** (for exact):
```python
def cluster_exact(questions, threshold=0.9):
    clusters = []
    used = set()
    for i, q1 in enumerate(questions):
        if q1.id in used: continue
        cluster = [q1]
        used.add(q1.id)
        for j, q2 in enumerate(questions[i+1:], i+1):
            if q2.id in used: continue
            if levenshtein_ratio(q1.norm_text, q2.norm_text) >= threshold:
                cluster.append(q2)
                used.add(q2.id)
        if len(cluster) > 1:
            clusters.append(cluster)
    return clusters
```

**DBSCAN-style** (for conceptual):
```python
def cluster_conceptual(questions, threshold=0.7):
    families = []
    used = set()
    for i, q1 in enumerate(questions):
        if q1.id in used: continue
        family = [q1]
        used.add(q1.id)
        for j, q2 in enumerate(questions[i+1:], i+1):
            if q2.id in used: continue
            if cosine_similarity(q1.vector, q2.vector) >= threshold:
                family.append(q2)
                used.add(q2.id)
        if len(family) > 1:
            families.append(family)
    return families
```

## Quality Control

### False Positive Prevention
- Minimum text length for comparison: 30 characters
- Require at least 2 distinct papers for exact repetition
- Require at least 2 distinct years for conceptual families
- Manual review flag for similarity 0.85-0.90

### False Negative Prevention
- Normalize common variations:
  - "DFA" ↔ "Deterministic Finite Automaton"
  - "NFA" ↔ "Non-deterministic Finite Automaton"
  - "pumping lemma" ↔ "pumping lemma for regular languages"
  - "minimize" ↔ "minimisation" (UK/US spelling)
- Include sub-question text in parent question context

### Validation
- Spot-check 10% of clusters manually
- Verify each cluster has ≥ 2 different papers
- Ensure no single paper dominates a family
- Cross-check with topic mapping

## Output Integration

Repetition data flows into:
1. **Topic Statistics** - Boosts priority scores
2. **Question Bank** - Families and exact reps documented
3. **Topic Content** - "Previous-Year Appearances" sections
4. **Exam Analysis** - Pattern frequency tables
5. **Visual Callouts** - "★ REPEATED PYQ TOPIC" badges

## Limitations

1. **OCR Errors**: May affect similarity scores for scanned papers
2. **Language Variations**: UK/US spelling, synonyms
3. **Context Dependence**: Same question may test different depths
4. **Partial Repetition**: Sub-parts of questions may repeat
5. **Semantic Drift**: Same pattern, evolved difficulty

## Future Improvements

- Sentence transformer embeddings for better semantic similarity
- Sub-question level analysis
- Difficulty progression tracking
- Cross-course pattern detection