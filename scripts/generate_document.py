#!/usr/bin/env python3
"""
Document generation script for the Comprehensive Course Study Guide plugin.
Synthesizes all analysis data into a structured content model for HTML rendering.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ContentSection:
    type: str
    title: str
    content: Any
    source: List[str]
    metadata: Dict

def load_all_data(work_dir: str) -> Dict[str, Any]:
    """Load all analysis data."""
    work_path = Path(work_dir).resolve()

    data = {}
    files = [
        "topics.json", "topic-priority.json", "material-emphasis.json",
        "pyq-analysis.json", "questions.json", "classifications.json",
        "sources.json"
    ]

    for fname in files:
        fpath = work_path / fname
        if fpath.exists():
            with open(fpath) as f:
                data[fname.replace(".json", "")] = json.load(f)
        else:
            data[fname.replace(".json", "")] = {}

    return data

def build_revision_sections(priorities: List[Dict], questions_data: Dict, topics_data: Dict) -> Dict[str, List]:
    """Build revision sections: formulas, definitions, algorithms."""
    formulas = []
    definitions = []
    algorithms = []

    # Extract from material emphasis
    topic_coverage = topics_data.get("material_emphasis", {}).get("topic_coverage", {})

    for cov_id, cov_data in topic_coverage.items():
        canonical = cov_data.get("canonical_name", "")

        # Formulas
        for formula in cov_data.get("formulas", []):
            formulas.append({
                "topic": canonical,
                "latex": formula.get("latex", ""),
                "description": formula.get("text", ""),
                "source": formula.get("source", "")
            })

        # Definitions
        for defn in cov_data.get("definitions", []):
            definitions.append({
                "topic": canonical,
                "text": defn.get("text", ""),
                "source": defn.get("source", "")
            })

        # Algorithms
        for algo in cov_data.get("algorithms", []):
            algorithms.append({
                "topic": canonical,
                "name": algo.get("name", ""),
                "steps": algo.get("steps", []),
                "source": algo.get("source", "")
            })

    return {
        "formulas": formulas,
        "definitions": definitions,
        "algorithms": algorithms
    }

def build_question_bank(questions_data: Dict, pyq_analysis: Dict) -> Dict:
    """Build structured question bank."""
    questions = questions_data.get("questions", [])
    families = pyq_analysis.get("question_families", [])
    exact_reps = pyq_analysis.get("exact_repetitions", [])

    # Group by unit/topic
    by_unit = {}
    by_topic = {}
    by_family = {}

    for q in questions:
        topic = q.get("topic", "Unmapped")
        unit = q.get("unit", "Unknown")

        if unit not in by_unit:
            by_unit[unit] = []
        by_unit[unit].append(q)

        if topic not in by_topic:
            by_topic[topic] = []
        by_topic[topic].append(q)

    # Build family details
    for fam in families:
        by_family[fam["family_id"]] = {
            "canonical_name": fam["canonical_name"],
            "concept": fam["concept"],
            "occurrences": fam["occurrences"],
            "years": fam["years"],
            "topic": fam["topic"],
            "subtopic": fam["subtopic"],
            "members": fam["members"]
        }

    # Exact repetitions
    exact_details = {}
    for rep in exact_reps:
        exact_details[rep["cluster_id"]] = {
            "canonical_question": rep["canonical_question"],
            "occurrences": rep["occurrences"],
            "years": rep["years"],
            "exam_types": rep["exam_types"],
            "question_numbers": rep["question_numbers"],
            "marks": rep["marks"],
            "topic": rep["topic"],
            "subtopic": rep["subtopic"]
        }

    return {
        "by_unit": by_unit,
        "by_topic": by_topic,
        "families": by_family,
        "exact_repetitions": exact_details,
        "total_questions": len(questions)
    }

def build_source_index(classifications: Dict, sources: Dict) -> List[Dict]:
    """Build source index with provenance."""
    source_index = []

    for c in classifications.get("classifications", []):
        fp = c["file_path"]
        items = [item for item in sources.get("items", []) if item["source_file"] == fp]
        pages = sorted(set(item["page_or_slide"] for item in items if item.get("page_or_slide")))

        source_index.append({
            "file": fp,
            "filename": c["filename"],
            "classification": c["classification"],
            "confidence": c["confidence"],
            "pages_slides": pages,
            "page_count": c.get("page_count") or len(pages),
            "extracted_items": len(items)
        })

    return source_index

def generate_content_model(work_dir: str, course_name: str = "Course", syllabus_covered: str = "Full Syllabus") -> Dict[str, Any]:
    """Generate the complete structured content model."""
    data = load_all_data(work_dir)

    topics_data = data.get("topics", {})
    priorities_data = data.get("topic_priority", {})
    material_data = data.get("material_emphasis", {})
    pyq_data = data.get("pyq_analysis", {})
    questions_data = data.get("questions", {})
    classifications_data = data.get("classifications", {})
    sources_data = data.get("sources", {})

    priorities = priorities_data.get("priorities", [])
    pyq_available = priorities_data.get("pyq_available", False)

    # Build units with topics
    units = []
    for unit in topics_data.get("units", []):
        unit_obj = {
            "unit_number": unit.get("unit_number"),
            "title": unit.get("title"),
            "syllabus_reference": f"UNIT {unit.get('unit_number')}",
            "topics": []
        }

        for topic in unit.get("topics", []):
            topic_id = topic.get("topic_id")
            topic_title = topic.get("title")

            # Find priority
            priority_info = next((p for p in priorities if p["topic_id"] == topic_id), {})
            priority_label = priority_info.get("priority", "MODERATE PRIORITY")
            priority_score = priority_info.get("priority_score", 0)
            hist_evidence = priority_info.get("historical_evidence", {})
            mat_evidence = priority_info.get("material_evidence", {})
            evidence_summary = priority_info.get("evidence_summary", [])

            # Find material coverage
            coverage = topic.get("coverage", {})

            # Build sections for this topic
            sections = []

            # Definition section
            if coverage.get("definitions"):
                for defn in coverage["definitions"][:3]:  # Limit
                    sections.append(ContentSection(
                        type="definition",
                        title="Definition",
                        content=defn.get("text", ""),
                        source=[defn.get("source", "")],
                        metadata={}
                    ).__dict__)

            # Formulas
            if coverage.get("formulas"):
                for formula in coverage["formulas"][:5]:
                    sections.append(ContentSection(
                        type="formula",
                        title="Formula",
                        content={"latex": formula.get("latex", ""), "description": formula.get("text", "")},
                        source=[formula.get("source", "")],
                        metadata={}
                    ).__dict__)

            # Detailed explanation (placeholder - would be generated by content-writer)
            sections.append(ContentSection(
                type="explanation",
                title="Detailed Explanation",
                content=f"[Comprehensive explanation of {topic_title} would be synthesized here from lecture materials and reference sources.]",
                source=[],
                metadata={"placeholder": True}
            ).__dict__)

            # Algorithms/Procedures
            if coverage.get("algorithms"):
                for algo in coverage["algorithms"][:2]:
                    sections.append(ContentSection(
                        type="algorithm",
                        title=f"Algorithm: {algo.get('name', 'Procedure')}",
                        content={"steps": algo.get("steps", [])},
                        source=[algo.get("source", "")],
                        metadata={}
                    ).__dict__)

            # Worked examples
            if coverage.get("examples"):
                for ex in coverage["examples"][:2]:
                    sections.append(ContentSection(
                        type="worked_example",
                        title="Worked Example",
                        content={"problem": ex.get("description", ""), "solution": "[Solution would be synthesized here]"},
                        source=[ex.get("source", "")],
                        metadata={}
                    ).__dict__)

            # Diagrams
            if coverage.get("diagrams"):
                for diag in coverage["diagrams"][:2]:
                    sections.append(ContentSection(
                        type="diagram",
                        title="Diagram",
                        content={"spec": diag, "type": diag.get("type", "automaton")},
                        source=[diag.get("source", "")],
                        metadata={"diagram_id": f"{topic_id}-{diag.get('type', 'diag')}"}
                    ).__dict__)

            # PYQ Appearances
            if pyq_available:
                topic_questions = [q for q in questions_data.get("questions", []) if q.get("topic") == topic_title]
                if topic_questions:
                    appearances = []
                    for q in topic_questions[:5]:
                        appearances.append({
                            "year": q.get("year"),
                            "exam": q.get("exam"),
                            "question": q.get("question_number"),
                            "marks": q.get("marks"),
                            "text": q.get("normalized_text", "")[:200]
                        })

                    sections.append(ContentSection(
                        type="pyq_appearances",
                        title="Previous-Year Appearances",
                        content=appearances,
                        source=[f"{q['source']} {q['question_number']}" for q in topic_questions[:5]],
                        metadata={"family": topic_questions[0].get("canonical_concept_id") if topic_questions else None}
                    ).__dict__)

                    # Question patterns
                    patterns = list(set(q.get("question_type") for q in topic_questions if q.get("question_type")))
                    if patterns:
                        sections.append(ContentSection(
                            type="question_patterns",
                            title="Common Question Forms",
                            content=patterns,
                            source=[],
                            metadata={}
                        ).__dict__)

            # Exam tips
            sections.append(ContentSection(
                type="exam_tips",
                title="Exam Tips",
                content=[
                    f"Priority: {priority_label}",
                    f"Focus on: {', '.join(evidence_summary[:2])}" if evidence_summary else "Review lecture materials thoroughly"
                ],
                source=[],
                metadata={}
            ).__dict__)

            # Common mistakes
            sections.append(ContentSection(
                type="common_mistakes",
                title="Common Mistakes",
                content=[
                    "Not reading the question carefully",
                    "Missing edge cases in constructions",
                    "Forgetting to justify steps in proofs"
                ],
                source=[],
                metadata={}
            ).__dict__)

            # Quick revision
            revision_items = []
            if coverage.get("definitions"):
                revision_items.extend([d.get("text", "")[:100] for d in coverage["definitions"][:2]])
            if coverage.get("formulas"):
                revision_items.extend([f.get("latex", "") for f in coverage["formulas"][:2]])

            sections.append(ContentSection(
                type="revision_box",
                title="Quick Revision",
                content=revision_items,
                source=[],
                metadata={}
            ).__dict__)

            topic_obj = {
                "topic_id": topic_id,
                "title": topic_title,
                "canonical_name": topic_title,
                "priority": priority_label,
                "priority_score": priority_score,
                "historical_evidence": hist_evidence,
                "material_evidence": mat_evidence,
                "evidence_summary": evidence_summary,
                "sections": sections,
                "subtopics": [s.get("title") for s in topic.get("subtopics", [])]
            }
            unit_obj["topics"].append(topic_obj)

        # Determine unit priority
        unit_priorities = [t["priority"] for t in unit_obj["topics"]]
        if "VERY HIGH PRIORITY" in unit_priorities:
            unit_obj["priority"] = "VERY HIGH"
        elif "HIGH PRIORITY" in unit_priorities:
            unit_obj["priority"] = "HIGH"
        elif "MODERATE PRIORITY" in unit_priorities:
            unit_obj["priority"] = "MODERATE"
        else:
            unit_obj["priority"] = "LOWER"

        units.append(unit_obj)

    # Build revision sections
    revision = build_revision_sections(priorities, questions_data, {"material_emphasis": material_data})

    # Build question bank
    question_bank = build_question_bank(questions_data, pyq_data)

    # Build source index
    source_index = build_source_index(classifications_data, sources_data)

    # Analysis summary
    exam_pattern = pyq_data.get("exam_pattern", {})
    analysis_summary = {
        "papers_analyzed": exam_pattern.get("papers_analyzed", 0),
        "total_questions": exam_pattern.get("total_questions", 0),
        "repeated_families": len(pyq_data.get("question_families", [])),
        "exact_repetitions": len(pyq_data.get("exact_repetitions", [])),
        "high_priority_topics": sum(1 for p in priorities if p["priority"] in ("VERY HIGH PRIORITY", "HIGH PRIORITY"))
    }

    content_model = {
        "course": course_name,
        "syllabus_covered": syllabus_covered,
        "generation_date": datetime.now().isoformat(),
        "pyq_available": pyq_available,
        "analysis_summary": analysis_summary,
        "units": units,
        "formula_revision": revision["formulas"],
        "definition_revision": revision["definitions"],
        "algorithm_revision": revision["algorithms"],
        "question_bank": question_bank,
        "source_index": source_index,
        "disclaimer": "No previous-year question papers were provided. The topic priorities in this guide are inferred from the supplied course materials and should not be interpreted as historical exam weightage." if not pyq_available else None
    }

    return content_model

def generate_all(work_dir: str, output_dir: str, course_name: str = "Course", syllabus_covered: str = "Full Syllabus") -> Dict[str, Any]:
    """Generate content model and save."""
    work_path = Path(work_dir).resolve()
    output_path = Path(output_dir).resolve()

    content_model = generate_content_model(work_dir, course_name, syllabus_covered)

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "study-guide-content.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content_model, f, indent=2, ensure_ascii=False)

    print(f"Content model generated: {output_file}")
    print(f"  Units: {len(content_model['units'])}")
    print(f"  Topics: {sum(len(u['topics']) for u in content_model['units'])}")
    print(f"  PYQ available: {content_model['pyq_available']}")

    return content_model

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_document.py <work_directory> <output_directory> [course_name] [syllabus_covered]")
        sys.exit(1)

    work_dir = sys.argv[1]
    output_dir = sys.argv[2]
    course_name = sys.argv[3] if len(sys.argv) > 3 else "Course"
    syllabus_covered = sys.argv[4] if len(sys.argv) > 4 else "Full Syllabus"

    try:
        generate_all(work_dir, output_dir, course_name, syllabus_covered)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()