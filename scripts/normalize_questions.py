#!/usr/bin/env python3
"""
Question normalization script for the Comprehensive Course Study Guide plugin.
Extracts and normalizes questions from PYQ files into structured representation.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from difflib import SequenceMatcher

@dataclass
class NormalizedQuestion:
    id: str
    source: str
    year: Optional[int]
    exam: Optional[str]
    semester: Optional[str]
    section: Optional[str]
    question_number: str
    sub_question: Optional[str]
    raw_text: str
    normalized_text: str
    topic: Optional[str]
    subtopic: Optional[str]
    question_type: Optional[str]
    marks: Optional[int]
    concepts: List[str]
    canonical_concept_id: Optional[str]

def load_data(work_dir: str) -> tuple[Dict, Dict]:
    """Load classifications and sources."""
    work_path = Path(work_dir).resolve()

    with open(work_path / "classifications.json") as f:
        classifications = json.load(f)

    with open(work_path / "sources.json") as f:
        sources = json.load(f)

    return classifications, sources

def get_pyq_files(classifications: Dict) -> List[Dict]:
    """Get all files classified as PYQ."""
    return [c for c in classifications["classifications"] if c["classification"] == "PYQ"]

def extract_questions_from_text(text: str, source_file: str, pyq_meta: Dict) -> List[Dict]:
    """Extract individual questions from PYQ text."""
    questions = []

    # Common question patterns
    patterns = [
        # Q1(a), Q2(b), etc.
        r'(?:^|\n)\s*(?:Q|Question)\s*(\d+)\s*\(([a-z])\)\s*[:\.]?\s*(.*?)(?=\n\s*(?:Q|Question)\s*\d+\s*\([a-z]\)|\n\s*(?:Q|Question)\s*\d+\s*[:\.]|\Z)',
        # Q1., Q2., etc.
        r'(?:^|\n)\s*(?:Q|Question)\s*(\d+)\s*[:\.]?\s*(.*?)(?=\n\s*(?:Q|Question)\s*\d+\s*[:\.]|\Z)',
        # 1., 2., etc. (numbered list)
        r'(?:^|\n)\s*(\d+)\s*[:\.]?\s*(.*?)(?=\n\s*\d+\s*[:\.]|\Z)',
        # (a), (b), etc. subquestions
        r'(?:^|\n)\s*\(([a-z])\)\s*[:\.]?\s*(.*?)(?=\n\s*\([a-z]\)|\Z)',
    ]

    # Try each pattern
    for pattern in patterns:
        matches = list(re.finditer(pattern, text, re.DOTALL | re.IGNORECASE))
        if matches:
            for match in matches:
                groups = match.groups()
                if len(groups) == 3:  # Q1(a) format
                    q_num, sub_q, q_text = groups
                    questions.append({
                        "question_number": f"Q{q_num}",
                        "sub_question": sub_q,
                        "raw_text": q_text.strip()
                    })
                elif len(groups) == 2:  # Q1. or 1. format
                    q_num, q_text = groups
                    # Check if it's a sub-question
                    if q_num.isdigit() and int(q_num) < 100:
                        questions.append({
                            "question_number": f"Q{q_num}",
                            "sub_question": None,
                            "raw_text": q_text.strip()
                        })
            if questions:
                break

    # If no structured questions found, try to split by marks patterns
    if not questions:
        # Look for marks indicators like [8], (8 marks), etc.
        parts = re.split(r'\[\s*(\d+)\s*marks?\s*\]|\(\s*(\d+)\s*marks?\s*\)', text)
        # This is a fallback - just split by double newlines
        sections = [s.strip() for s in text.split('\n\n') if len(s.strip()) > 20]
        for i, section in enumerate(sections):
            questions.append({
                "question_number": f"Q{i+1}",
                "sub_question": None,
                "raw_text": section
            })

    return questions

def normalize_text(text: str) -> str:
    """Normalize question text for comparison."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove marks indicators
    text = re.sub(r'\[\s*\d+\s*marks?\s*\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(\s*\d+\s*marks?\s*\)', '', text, flags=re.IGNORECASE)
    # Remove question numbers
    text = re.sub(r'^(?:Q|Question)\s*\d+\s*[:\.]?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\d+\s*[:\.]?\s*', '', text)
    text = re.sub(r'^\([a-z]\)\s*[:\.]?\s*', '', text)
    return text.strip()

def identify_question_type(text: str) -> Optional[str]:
    """Identify the type of question."""
    text_lower = text.lower()

    type_patterns = {
        "construction": [r'\b(construct|design|build|create|draw)\b'],
        "conversion": [r'\b(convert|transform|translate)\b'],
        "minimization": [r'\b(minimiz|reduc|simplif)\b'],
        "proof": [r'\b(prove|proof|show that|demonstrate)\b'],
        "derivation": [r'\b(derive|derivation|obtain)\b'],
        "explanation": [r'\b(explain|describe|discuss|elaborate)\b'],
        "definition": [r'\b(define|definition|what is)\b'],
        "computation": [r'\b(calculate|compute|solve|find|determine|evaluate)\b'],
        "analysis": [r'\b(analy[sz]e|examine|investigate)\b'],
        "comparison": [r'\b(compare|contrast|difference|similar)\b'],
        "application": [r'\b(apply|application|use|implement)\b'],
    }

    for qtype, patterns in type_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return qtype

    return "unknown"

def extract_concepts(text: str) -> List[str]:
    """Extract key concepts from question text."""
    # Common CS/engineering concepts
    concept_patterns = [
        r'\b(DFA|NFA|ε-NFA|FA|finite automaton)\b',
        r'\b(regular language|regular expression|regex)\b',
        r'\b(context.free|CFG|pushdown|PDA)\b',
        r'\b(Turing|TM|computab|decidab)\b',
        r'\b(pumping lemma|closure propert)\b',
        r'\b(minimiz|equivalen|determiniz)\b',
        r'\b(recurrence|recursion|complexity|big.?O)\b',
        r'\b(graph|tree|heap|stack|queue)\b',
        r'\b(sort|search|travers)\b',
        r'\b(database|SQL|normaliz|transaction)\b',
        r'\b(network|protocol|TCP|IP|routing)\b',
        r'\b(process|thread|schedul|deadlock)\b',
        r'\b(memory|virtual|paging|segment)\b',
    ]

    concepts = []
    for pattern in concept_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        concepts.extend(matches)

    return list(set(concepts))

def generate_canonical_id(concepts: List[str], qtype: str) -> str:
    """Generate a canonical concept ID for grouping."""
    if not concepts:
        return f"unknown-{qtype}"

    # Sort concepts for consistency
    sorted_concepts = sorted(c.lower().replace(' ', '-') for c in concepts)
    return f"{'-'.join(sorted_concepts[:3])}-{qtype}"

def normalize_all(work_dir: str) -> Dict[str, Any]:
    """Normalize all questions from PYQ files."""
    work_path = Path(work_dir).resolve()
    classifications, sources = load_data(work_dir)

    pyq_files = get_pyq_files(classifications)
    all_questions = []

    # Build lookup for file items
    file_items = {}
    for item in sources["items"]:
        fp = item["source_file"]
        if fp not in file_items:
            file_items[fp] = []
        file_items[fp].append(item)

    for pyq_file in pyq_files:
        rel_path = pyq_file["file_path"]
        pyq_meta = pyq_file.get("pyq_metadata", {})

        items = file_items.get(rel_path, [])
        if not items:
            continue

        # Combine all text from this file
        full_text = "\n".join(item["content"] for item in items)

        # Extract questions
        raw_questions = extract_questions_from_text(full_text, rel_path, pyq_meta)

        for i, raw_q in enumerate(raw_questions):
            raw_text = raw_q["raw_text"]
            normalized = normalize_text(raw_text)
            qtype = identify_question_type(normalized)
            concepts = extract_concepts(normalized)
            canonical_id = generate_canonical_id(concepts, qtype)

            # Generate unique ID
            year = pyq_meta.get("year")
            exam = pyq_meta.get("exam_type")
            q_id = f"{year or 'unk'}-{exam or 'unk'}-{raw_q['question_number']}"
            if raw_q.get("sub_question"):
                q_id += f"-{raw_q['sub_question']}"

            question = NormalizedQuestion(
                id=q_id,
                source=rel_path,
                year=year,
                exam=exam,
                semester=pyq_meta.get("semester"),
                section=raw_q.get("section"),
                question_number=raw_q["question_number"],
                sub_question=raw_q.get("sub_question"),
                raw_text=raw_text,
                normalized_text=normalized,
                topic=None,  # Will be mapped later
                subtopic=None,
                question_type=qtype,
                marks=None,  # Will be extracted if possible
                concepts=concepts,
                canonical_concept_id=canonical_id
            )
            all_questions.append(asdict(question))

    # Try to extract marks from raw text
    for q in all_questions:
        marks_match = re.search(r'\[\s*(\d+)\s*marks?\s*\]|\(\s*(\d+)\s*marks?\s*\)', q["raw_text"], re.IGNORECASE)
        if marks_match:
            q["marks"] = int(marks_match.group(1) or marks_match.group(2))

    output = {
        "normalization_timestamp": datetime.now().isoformat(),
        "total_questions": len(all_questions),
        "questions": all_questions
    }

    output_file = work_path / "questions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Normalized {len(all_questions)} questions")
    return output

def main():
    if len(sys.argv) < 2:
        print("Usage: python normalize_questions.py <work_directory>")
        sys.exit(1)

    work_dir = sys.argv[1]

    try:
        normalize_all(work_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()