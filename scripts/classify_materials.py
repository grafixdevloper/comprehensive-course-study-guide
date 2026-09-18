#!/usr/bin/env python3
"""
Classification script for the Comprehensive Course Study Guide plugin.
Classifies files into categories using both filename and content analysis.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

CLASSIFICATIONS = [
    "COURSE_HANDOUT",
    "SYLLABUS",
    "PYQ",
    "LECTURE_NOTES",
    "LECTURE_SLIDES",
    "REFERENCE_MATERIAL",
    "ASSIGNMENT",
    "LAB_MATERIAL",
    "OTHER"
]

@dataclass
class ClassificationResult:
    file_path: str
    filename: str
    classification: str
    confidence: float
    evidence: List[str]
    pyq_metadata: Optional[Dict[str, Any]] = None

def load_sources(work_dir: str) -> Dict[str, Any]:
    """Load extracted sources."""
    sources_file = Path(work_dir) / "sources.json"
    if not sources_file.exists():
        raise ValueError(f"Sources not found: {sources_file}")
    with open(sources_file) as f:
        return json.load(f)

def get_file_items(sources: Dict, rel_path: str) -> List[Dict]:
    """Get all extracted items for a specific file."""
    return [item for item in sources["items"] if item["source_file"] == rel_path]

def classify_by_content(items: List[Dict]) -> tuple[str, float, List[str]]:
    """Classify based on extracted content."""
    if not items:
        return "OTHER", 0.1, ["No content extracted"]

    # Combine all text
    all_text = " ".join(item["content"] for item in items).lower()
    content_types = [item["content_type"] for item in items]

    evidence = []

    # PYQ indicators
    pyq_score = 0
    pyq_patterns = [
        (r'\b(question|q\s*\d+)\b', 0.1),
        (r'\b(marks?|points?)\b', 0.1),
        (r'\b(mid\s*sem|end\s*sem|midterm|final)\b', 0.2),
        (r'\b(20\d{2})\b', 0.1),
        (r'\b(duration|time\s*allowed|maximum\s*marks)\b', 0.15),
        (r'\b(section\s*[a-c])\b', 0.1),
        (r'\b(answer\s*all|attempt\s*any)\b', 0.15),
    ]
    for pattern, weight in pyq_patterns:
        matches = len(re.findall(pattern, all_text))
        if matches > 0:
            pyq_score += min(weight * matches, weight * 3)
            evidence.append(f"PYQ pattern: {pattern} ({matches} matches)")

    # Syllabus indicators
    syllabus_score = 0
    syllabus_patterns = [
        (r'\b(syllabus|course\s*outline|curriculum)\b', 0.3),
        (r'\b(unit\s*\d+|module\s*\d+)\b', 0.2),
        (r'\b(topic|subtopic|chapter)\b', 0.1),
        (r'\b(learning\s*outcome|objective)\b', 0.15),
        (r'\b(prerequisite|reference\s*book)\b', 0.1),
    ]
    for pattern, weight in syllabus_patterns:
        matches = len(re.findall(pattern, all_text))
        if matches > 0:
            syllabus_score += min(weight * matches, weight * 2)
            evidence.append(f"Syllabus pattern: {pattern} ({matches} matches)")

    # Course handout indicators
    handout_score = 0
    handout_patterns = [
        (r'\b(course\s*handout|course\s*information)\b', 0.3),
        (r'\b(instructor|teacher|professor|ta)\b', 0.1),
        (r'\b(office\s*hours|contact|email)\b', 0.1),
        (r'\b(grading|assessment|evaluation)\b', 0.15),
        (r'\b(schedule|timetable|week\s*\d+)\b', 0.15),
    ]
    for pattern, weight in handout_patterns:
        matches = len(re.findall(pattern, all_text))
        if matches > 0:
            handout_score += min(weight * matches, weight * 2)
            evidence.append(f"Handout pattern: {pattern} ({matches} matches)")

    # Lecture notes indicators
    notes_score = 0
    notes_patterns = [
        (r'\b(lecture\s*\d+|class\s*\d+|session\s*\d+)\b', 0.2),
        (r'\b(notes?|summary|overview)\b', 0.1),
        (r'\b(example|illustration|worked)\b', 0.1),
        (r'\b(definition|theorem|proof|lemma)\b', 0.15),
    ]
    for pattern, weight in notes_patterns:
        matches = len(re.findall(pattern, all_text))
        if matches > 0:
            notes_score += min(weight * matches, weight * 2)
            evidence.append(f"Notes pattern: {pattern} ({matches} matches)")

    # Lecture slides indicators
    slides_score = 0
    if "pptx" in str(items[0].get("source_type", "")) or "ppt" in str(items[0].get("source_type", "")):
        slides_score += 0.3
        evidence.append("PPT/PPTX format")
    slide_indicators = len([c for c in content_types if c in ("heading", "list")])
    if slide_indicators > 5:
        slides_score += 0.2
        evidence.append(f"Slide-like structure ({slide_indicators} headings/lists)")

    # Reference material indicators
    ref_score = 0
    ref_patterns = [
        (r'\b(reference|textbook|bibliography|citation)\b', 0.2),
        (r'\b(chapter\s*\d+|section\s*\d+\.\d+)\b', 0.15),
        (r'\b(doi|isbn|publisher|author)\b', 0.1),
    ]
    for pattern, weight in ref_patterns:
        matches = len(re.findall(pattern, all_text))
        if matches > 0:
            ref_score += min(weight * matches, weight * 2)
            evidence.append(f"Reference pattern: {pattern} ({matches} matches)")

    # Assignment indicators
    assign_score = 0
    assign_patterns = [
        (r'\b(assignment|homework|problem\s*set)\b', 0.3),
        (r'\b(due\s*date|deadline|submit)\b', 0.15),
        (r'\b(solution|answer\s*key)\b', 0.1),
    ]
    for pattern, weight in assign_patterns:
        matches = len(re.findall(pattern, all_text))
        if matches > 0:
            assign_score += min(weight * matches, weight * 2)
            evidence.append(f"Assignment pattern: {pattern} ({matches} matches)")

    # Lab material indicators
    lab_score = 0
    lab_patterns = [
        (r'\b(lab|laboratory|practical|experiment)\b', 0.25),
        (r'\b(apparatus|procedure|observation|result)\b', 0.15),
    ]
    for pattern, weight in lab_patterns:
        matches = len(re.findall(pattern, all_text))
        if matches > 0:
            lab_score += min(weight * matches, weight * 2)
            evidence.append(f"Lab pattern: {pattern} ({matches} matches)")

    # Determine best classification
    scores = {
        "PYQ": pyq_score,
        "SYLLABUS": syllabus_score,
        "COURSE_HANDOUT": handout_score,
        "LECTURE_NOTES": notes_score,
        "LECTURE_SLIDES": slides_score,
        "REFERENCE_MATERIAL": ref_score,
        "ASSIGNMENT": assign_score,
        "LAB_MATERIAL": lab_score,
    }

    best = max(scores, key=scores.get)
    confidence = min(scores[best], 0.95)

    if confidence < 0.3:
        best = "OTHER"
        confidence = 0.3
        evidence.append("Low confidence - classified as OTHER")

    return best, confidence, evidence

def extract_pyq_metadata(items: List[Dict]) -> Optional[Dict[str, Any]]:
    """Extract PYQ-specific metadata from content."""
    all_text = " ".join(item["content"] for item in items)

    metadata = {}

    # Year
    year_match = re.search(r'\b(20\d{2})\b', all_text)
    if year_match:
        metadata["year"] = int(year_match.group(1))

    # Exam type
    exam_type = None
    if re.search(r'\bmid\s*sem\b', all_text, re.I):
        exam_type = "midsem"
    elif re.search(r'\bend\s*sem\b', all_text, re.I):
        exam_type = "endsem"
    elif re.search(r'\bmidterm\b', all_text, re.I):
        exam_type = "midterm"
    elif re.search(r'\bfinal\b', all_text, re.I):
        exam_type = "final"
    elif re.search(r'\bquiz\b', all_text, re.I):
        exam_type = "quiz"
    if exam_type:
        metadata["exam_type"] = exam_type

    # Duration
    dur_match = re.search(r'(duration|time\s*allowed)[\s:]*(\d+\s*(?:hr|hour|min|minute))', all_text, re.I)
    if dur_match:
        metadata["duration"] = dur_match.group(2)

    # Max marks
    marks_match = re.search(r'(maximum\s*marks|max\s*marks|total\s*marks)[\s:]*(\d+)', all_text, re.I)
    if marks_match:
        metadata["max_marks"] = int(marks_match.group(2))

    # Sections
    sections = re.findall(r'section\s*([a-c])', all_text, re.I)
    if sections:
        metadata["sections"] = sorted(set(s.upper() for s in sections))

    return metadata if metadata else None

def classify_all(work_dir: str) -> Dict[str, Any]:
    """Classify all files in the inventory."""
    work_path = Path(work_dir).resolve()

    # Load inventory and sources
    inventory_file = work_path / "inventory.json"
    sources = load_sources(work_dir)

    with open(inventory_file) as f:
        inventory = json.load(f)

    results = []

    for file_info in inventory["files"]:
        rel_path = file_info["path"]
        items = get_file_items(sources, rel_path)

        # Classify by content
        classification, confidence, evidence = classify_by_content(items)

        # Extract PYQ metadata if applicable
        pyq_metadata = None
        if classification == "PYQ":
            pyq_metadata = extract_pyq_metadata(items)

        result = ClassificationResult(
            file_path=rel_path,
            filename=file_info["filename"],
            classification=classification,
            confidence=confidence,
            evidence=evidence,
            pyq_metadata=pyq_metadata
        )
        results.append(asdict(result))

    # Save classifications
    output = {
        "classification_timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "classifications": results
    }

    output_file = work_path / "classifications.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Summary
    by_class = {}
    for r in results:
        cls = r["classification"]
        by_class[cls] = by_class.get(cls, 0) + 1

    print(f"Classification complete: {by_class}")
    return output

def main():
    if len(sys.argv) < 2:
        print("Usage: python classify_materials.py <work_directory>")
        sys.exit(1)

    work_dir = sys.argv[1]

    try:
        classify_all(work_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()