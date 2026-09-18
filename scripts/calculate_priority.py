#!/usr/bin/env python3
"""
Priority calculation script for the Comprehensive Course Study Guide plugin.
Calculates evidence-based topic priorities from PYQ analysis and material emphasis.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

PRIORITY_LABELS = ["VERY HIGH PRIORITY", "HIGH PRIORITY", "MODERATE PRIORITY", "LOWER PRIORITY"]

@dataclass
class TopicPriority:
    topic_id: str
    topic_title: str
    unit_number: int
    priority: str
    priority_score: float
    historical_evidence: Dict
    material_evidence: Dict
    evidence_summary: List[str]
    pyq_available: bool

def load_data(work_dir: str) -> tuple[Dict, Dict, Dict, Dict]:
    """Load all required data."""
    work_path = Path(work_dir).resolve()

    with open(work_path / "topics.json") as f:
        topics = json.load(f)

    with open(work_path / "material-emphasis.json") as f:
        material = json.load(f)

    # Load PYQ analysis if available
    pyq_analysis = {}
    pyq_path = work_path / "pyq-analysis.json"
    if pyq_path.exists():
        with open(pyq_path) as f:
            pyq_analysis = json.load(f)

    # Load questions for additional stats
    questions = {}
    q_path = work_path / "questions.json"
    if q_path.exists():
        with open(q_path) as f:
            questions = json.load(f)

    return topics, material, pyq_analysis, questions

def calculate_historical_score(topic_id: str, topic_title: str, pyq_analysis: Dict) -> tuple[float, Dict]:
    """Calculate priority score from historical PYQ data."""
    if not pyq_analysis:
        return 0.0, {}

    topic_stats = pyq_analysis.get("topic_statistics", {})

    # Try exact match first, then fuzzy match
    stats = topic_stats.get(topic_id) or topic_stats.get(topic_title)
    if not stats:
        # Try partial matching
        for key, value in topic_stats.items():
            if topic_title.lower() in key.lower() or key.lower() in topic_title.lower():
                stats = value
                break

    if not stats:
        return 0.0, {}

    # Weight factors
    weights = {
        "question_frequency": 0.25,
        "paper_frequency": 0.20,
        "year_coverage": 0.15,
        "mark_share": 0.20,
        "consecutive_years": 0.10,
        "max_marks": 0.10
    }

    # Normalize each factor (0-1 scale)
    max_qf = max(s.get("question_frequency", 0) for s in topic_stats.values()) or 1
    max_pf = max(s.get("paper_frequency", 0) for s in topic_stats.values()) or 1
    max_mm = max(s.get("max_marks_single_question", 0) for s in topic_stats.values()) or 1

    score = 0
    score += weights["question_frequency"] * (stats.get("question_frequency", 0) / max_qf)
    score += weights["paper_frequency"] * (stats.get("paper_frequency", 0) / max_pf)
    score += weights["year_coverage"] * stats.get("year_coverage", 0)
    score += weights["mark_share"] * stats.get("mark_share", 0)
    score += weights["consecutive_years"] * min(stats.get("consecutive_years", 0) / 5, 1.0)
    score += weights["max_marks"] * (stats.get("max_marks_single_question", 0) / max_mm)

    evidence = {
        "question_frequency": stats.get("question_frequency", 0),
        "paper_frequency": stats.get("paper_frequency", 0),
        "year_coverage": stats.get("year_coverage", 0),
        "total_observed_marks": stats.get("total_observed_marks", 0),
        "mark_share": stats.get("mark_share", 0),
        "consecutive_years": stats.get("consecutive_years", 0),
        "max_marks": stats.get("max_marks_single_question", 0),
        "question_types": stats.get("question_type_distribution", {}),
        "exam_types": stats.get("exam_type_distribution", {})
    }

    return score, evidence

def calculate_material_score(topic_id: str, topic_title: str, material: Dict) -> tuple[float, Dict]:
    """Calculate priority score from lecture material emphasis."""
    topic_coverage = material.get("topic_coverage", {})

    # Find matching coverage
    coverage = None
    for cov_id, cov_data in topic_coverage.items():
        if topic_title.lower() in cov_data.get("canonical_name", "").lower() or \
           cov_data.get("canonical_name", "").lower() in topic_title.lower():
            coverage = cov_data
            break

    if not coverage:
        return 0.0, {}

    metrics = coverage.get("metrics", {})

    # Weight factors for material emphasis
    weights = {
        "lecture_count": 0.15,
        "slide_count": 0.15,
        "depth_score": 0.30,
        "definition_count": 0.10,
        "formula_count": 0.10,
        "algorithm_count": 0.10,
        "example_count": 0.10
    }

    # Normalize (assuming max values)
    max_lectures = max(m.get("metrics", {}).get("lecture_count", 0) for m in topic_coverage.values()) or 1
    max_slides = max(m.get("metrics", {}).get("slide_count", 0) for m in topic_coverage.values()) or 1
    max_defs = max(m.get("metrics", {}).get("definition_count", 0) for m in topic_coverage.values()) or 1
    max_formulas = max(m.get("metrics", {}).get("formula_count", 0) for m in topic_coverage.values()) or 1
    max_algos = max(m.get("metrics", {}).get("algorithm_count", 0) for m in topic_coverage.values()) or 1
    max_examples = max(m.get("metrics", {}).get("example_count", 0) for m in topic_coverage.values()) or 1

    score = 0
    score += weights["lecture_count"] * (metrics.get("lecture_count", 0) / max_lectures)
    score += weights["slide_count"] * (metrics.get("slide_count", 0) / max_slides)
    score += weights["depth_score"] * metrics.get("depth_score", 0)
    score += weights["definition_count"] * (metrics.get("definition_count", 0) / max_defs)
    score += weights["formula_count"] * (metrics.get("formula_count", 0) / max_formulas)
    score += weights["algorithm_count"] * (metrics.get("algorithm_count", 0) / max_algos)
    score += weights["example_count"] * (metrics.get("example_count", 0) / max_examples)

    evidence = {
        "lecture_count": metrics.get("lecture_count", 0),
        "slide_count": metrics.get("slide_count", 0),
        "depth_score": metrics.get("depth_score", 0),
        "definitions": metrics.get("definition_count", 0),
        "formulas": metrics.get("formula_count", 0),
        "algorithms": metrics.get("algorithm_count", 0),
        "examples": metrics.get("example_count", 0),
        "diagrams": metrics.get("diagram_count", 0)
    }

    return score, evidence

def determine_priority_label(score: float, pyq_available: bool) -> str:
    """Convert numeric score to priority label."""
    if pyq_available:
        # With PYQ data, use historical thresholds
        if score >= 0.75:
            return "VERY HIGH PRIORITY"
        elif score >= 0.55:
            return "HIGH PRIORITY"
        elif score >= 0.35:
            return "MODERATE PRIORITY"
        else:
            return "LOWER PRIORITY"
    else:
        # Without PYQ, use material-only thresholds (more conservative)
        if score >= 0.80:
            return "VERY HIGH PRIORITY"
        elif score >= 0.60:
            return "HIGH PRIORITY"
        elif score >= 0.40:
            return "MODERATE PRIORITY"
        else:
            return "LOWER PRIORITY"

def build_evidence_summary(historical: Dict, material: Dict, priority: str, pyq_available: bool) -> List[str]:
    """Build human-readable evidence summary."""
    evidence = []

    if pyq_available and historical:
        if historical.get("question_frequency", 0) > 0:
            evidence.append(f"Appeared in {historical['question_frequency']} questions across {historical['paper_frequency']} papers")
        if historical.get("year_coverage", 0) > 0:
            evidence.append(f"Covered in {historical['year_coverage']*100:.0f}% of analyzed years")
        if historical.get("total_observed_marks", 0) > 0:
            evidence.append(f"Total {historical['total_observed_marks']} observed marks ({historical['mark_share']*100:.1f}% of paper)")
        if historical.get("consecutive_years", 0) > 1:
            evidence.append(f"Appeared in {historical['consecutive_years']} consecutive years")
        if historical.get("max_marks", 0) > 0:
            evidence.append(f"Maximum single question: {historical['max_marks']} marks")

        qtypes = historical.get("question_types", {})
        if qtypes:
            type_str = ", ".join(f"{k}: {v}" for k, v in qtypes.items())
            evidence.append(f"Question types: {type_str}")

    if material:
        if material.get("lecture_count", 0) > 0:
            evidence.append(f"Covered in {material['lecture_count']} lectures ({material['slide_count']} slides)")
        if material.get("depth_score", 0) > 0.5:
            evidence.append(f"High lecture depth (score: {material['depth_score']:.2f})")
        if material.get("definitions", 0) > 0:
            evidence.append(f"{material['definitions']} definitions, {material['formulas']} formulas, {material['algorithms']} algorithms")
        if material.get("examples", 0) > 0:
            evidence.append(f"{material['examples']} worked examples, {material['diagrams']} diagrams")

    if not evidence:
        evidence.append("Limited evidence available")

    return evidence

def calculate_all(work_dir: str) -> Dict[str, Any]:
    """Calculate priorities for all topics."""
    work_path = Path(work_dir).resolve()
    topics, material, pyq_analysis, questions = load_data(work_dir)

    pyq_available = bool(pyq_analysis and pyq_analysis.get("topic_statistics"))

    priorities = []

    for unit in topics.get("units", []):
        unit_num = unit.get("unit_number", 0)
        for topic in unit.get("topics", []):
            topic_id = topic.get("topic_id", "")
            topic_title = topic.get("title", "")

            # Calculate scores
            hist_score, hist_evidence = calculate_historical_score(topic_id, topic_title, pyq_analysis)
            mat_score, mat_evidence = calculate_material_score(topic_id, topic_title, material)

            # Combined score (weighted)
            if pyq_available:
                combined_score = 0.7 * hist_score + 0.3 * mat_score
            else:
                combined_score = mat_score  # Only material evidence

            priority_label = determine_priority_label(combined_score, pyq_available)
            evidence_summary = build_evidence_summary(hist_evidence, mat_evidence, priority_label, pyq_available)

            priority = TopicPriority(
                topic_id=topic_id,
                topic_title=topic_title,
                unit_number=unit_num,
                priority=priority_label,
                priority_score=round(combined_score, 3),
                historical_evidence=hist_evidence,
                material_evidence=mat_evidence,
                evidence_summary=evidence_summary,
                pyq_available=pyq_available
            )
            priorities.append(asdict(priority))

    # Sort by priority score descending
    priorities.sort(key=lambda p: p["priority_score"], reverse=True)

    output = {
        "calculation_timestamp": datetime.now().isoformat(),
        "pyq_available": pyq_available,
        "total_topics": len(priorities),
        "priority_distribution": {
            label: sum(1 for p in priorities if p["priority"] == label)
            for label in PRIORITY_LABELS
        },
        "priorities": priorities
    }

    output_file = work_path / "topic-priority.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Priority calculation complete:")
    for label, count in output["priority_distribution"].items():
        print(f"  {label}: {count}")

    return output

def main():
    if len(sys.argv) < 2:
        print("Usage: python calculate_priority.py <work_directory>")
        sys.exit(1)

    work_dir = sys.argv[1]

    try:
        calculate_all(work_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()