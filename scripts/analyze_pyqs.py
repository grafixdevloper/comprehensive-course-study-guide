#!/usr/bin/env python3
"""
PYQ analysis script for the Comprehensive Course Study Guide plugin.
Analyzes normalized questions for repetition patterns, topic mapping, and statistics.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher

@dataclass
class ExactRepetition:
    cluster_id: str
    canonical_question: str
    occurrences: int
    years: List[int]
    exam_types: List[str]
    question_numbers: List[str]
    marks: List[int]
    topic: str
    subtopic: str
    member_ids: List[str]

@dataclass
class QuestionFamily:
    family_id: str
    canonical_name: str
    concept: str
    members: List[Dict]
    occurrences: int
    years: List[int]
    topic: str
    subtopic: str
    pattern: str

@dataclass
class PatternRepetition:
    pattern_id: str
    description: str
    frequency: int
    papers: int
    years: List[int]
    avg_marks: float
    subtopics: List[str]

def load_questions(work_dir: str) -> Dict:
    """Load normalized questions."""
    with open(Path(work_dir) / "questions.json") as f:
        return json.load(f)

def similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_exact_repetitions(questions: List[Dict], threshold: float = 0.9) -> List[ExactRepetition]:
    """Find exact/near-exact question repetitions."""
    clusters = []
    used = set()

    for i, q1 in enumerate(questions):
        if q1["id"] in used:
            continue

        cluster = [q1]
        used.add(q1["id"])

        for j, q2 in enumerate(questions[i+1:], i+1):
            if q2["id"] in used:
                continue

            sim = similarity(q1["normalized_text"], q2["normalized_text"])
            if sim >= threshold:
                cluster.append(q2)
                used.add(q2["id"])

        if len(cluster) > 1:
            # Create cluster record
            canonical = cluster[0]["normalized_text"]
            years = sorted(set(q["year"] for q in cluster if q["year"]))
            exam_types = list(set(q["exam"] for q in cluster if q["exam"]))
            q_numbers = [q["question_number"] for q in cluster]
            marks = [q["marks"] for q in cluster if q["marks"]]

            cluster_id = f"exact-{len(clusters)+1:03d}"

            clusters.append(ExactRepetition(
                cluster_id=cluster_id,
                canonical_question=canonical,
                occurrences=len(cluster),
                years=years,
                exam_types=exam_types,
                question_numbers=q_numbers,
                marks=marks,
                topic=cluster[0].get("topic", "Unknown"),
                subtopic=cluster[0].get("subtopic", "Unknown"),
                member_ids=[q["id"] for q in cluster]
            ))

    return clusters

def find_question_families(questions: List[Dict], threshold: float = 0.7) -> List[QuestionFamily]:
    """Find conceptual question families (semantic similarity)."""
    # Group by canonical_concept_id first
    concept_groups = defaultdict(list)
    for q in questions:
        cid = q.get("canonical_concept_id", "unknown")
        concept_groups[cid].append(q)

    families = []
    family_num = 0

    for concept_id, group in concept_groups.items():
        if len(group) < 2:
            continue

        # Further cluster by semantic similarity within concept group
        used = set()
        for i, q1 in enumerate(group):
            if q1["id"] in used:
                continue

            family = [q1]
            used.add(q1["id"])

            for j, q2 in enumerate(group[i+1:], i+1):
                if q2["id"] in used:
                    continue

                sim = similarity(q1["normalized_text"], q2["normalized_text"])
                if sim >= threshold:
                    family.append(q2)
                    used.add(q2["id"])

            if len(family) >= 2:
                family_num += 1
                years = sorted(set(q["year"] for q in family if q["year"]))
                members = []
                for q in family:
                    members.append({
                        "id": q["id"],
                        "text": q["normalized_text"][:200],
                        "year": q["year"],
                        "exam": q["exam"],
                        "marks": q["marks"]
                    })

                families.append(QuestionFamily(
                    family_id=f"fam-{family_num:03d}",
                    canonical_name=f"{concept_id.replace('-', ' ').title()}",
                    concept=concept_id,
                    members=members,
                    occurrences=len(family),
                    years=years,
                    topic=family[0].get("topic", "Unknown"),
                    subtopic=family[0].get("subtopic", "Unknown"),
                    pattern=concept_id
                ))

    return families

def identify_patterns(questions: List[Dict]) -> List[PatternRepetition]:
    """Identify recurring question patterns."""
    pattern_counts = defaultdict(lambda: {"count": 0, "papers": set(), "years": set(), "marks": [], "subtopics": set()})

    for q in questions:
        pattern = q.get("canonical_concept_id", "unknown")
        pattern_counts[pattern]["count"] += 1
        if q.get("source"):
            pattern_counts[pattern]["papers"].add(q["source"])
        if q.get("year"):
            pattern_counts[pattern]["years"].add(q["year"])
        if q.get("marks"):
            pattern_counts[pattern]["marks"].append(q["marks"])
        if q.get("subtopic"):
            pattern_counts[pattern]["subtopics"].add(q["subtopic"])

    patterns = []
    for pid, data in pattern_counts.items():
        if data["count"] >= 2:  # Only recurring patterns
            patterns.append(PatternRepetition(
                pattern_id=pid,
                description=pid.replace('-', ' ').title(),
                frequency=data["count"],
                papers=len(data["papers"]),
                years=sorted(data["years"]),
                avg_marks=sum(data["marks"]) / len(data["marks"]) if data["marks"] else 0,
                subtopics=sorted(data["subtopics"])
            ))

    return sorted(patterns, key=lambda p: p.frequency, reverse=True)

def map_questions_to_topics(questions: List[Dict], syllabus: Dict) -> List[Dict]:
    """Map questions to syllabus topics."""
    # Build topic keywords from syllabus
    topic_keywords = {}
    for unit in syllabus.get("units", []):
        for topic in unit.get("topics", []):
            topic_id = topic.get("topic_id", "")
            keywords = topic.get("keywords", [topic.get("title", "").lower()])
            topic_keywords[topic_id] = [k.lower() for k in keywords]

    # Also check subtopics
    for unit in syllabus.get("units", []):
        for topic in unit.get("topics", []):
            for subtopic in topic.get("subtopics", []):
                topic_id = subtopic.get("topic_id", "")
                keywords = subtopic.get("keywords", [subtopic.get("title", "").lower()])
                topic_keywords[topic_id] = [k.lower() for k in keywords]

    mapped = []
    for q in questions:
        text = q["normalized_text"].lower()
        concepts = [c.lower() for c in q.get("concepts", [])]

        best_topic = None
        best_score = 0

        for topic_id, keywords in topic_keywords.items():
            score = 0
            for kw in keywords:
                if kw in text:
                    score += 2
                for concept in concepts:
                    if kw in concept or concept in kw:
                        score += 3
            if score > best_score:
                best_score = score
                best_topic = topic_id

        if best_topic and best_score > 0:
            q["topic"] = best_topic
            # Find subtopic
            for unit in syllabus.get("units", []):
                for topic in unit.get("topics", []):
                    if topic.get("topic_id") == best_topic:
                        q["topic"] = topic.get("title", best_topic)
                        for subtopic in topic.get("subtopics", []):
                            for kw in subtopic.get("keywords", []):
                                if kw.lower() in text:
                                    q["subtopic"] = subtopic.get("title", "")
                                    break
                        break

        mapped.append(q)

    return mapped

def calculate_topic_statistics(questions: List[Dict], total_papers: int, total_years: List[int]) -> Dict:
    """Calculate statistics per topic."""
    topic_stats = defaultdict(lambda: {
        "question_frequency": 0,
        "paper_frequency": set(),
        "year_coverage": set(),
        "total_observed_marks": 0,
        "marks_list": [],
        "question_types": defaultdict(int),
        "exam_types": defaultdict(int),
        "max_marks": 0,
        "consecutive_years": 0
    })

    for q in questions:
        topic = q.get("topic") or q.get("canonical_concept_id", "unknown")
        stats = topic_stats[topic]

        stats["question_frequency"] += 1
        if q.get("source"):
            stats["paper_frequency"].add(q["source"])
        if q.get("year"):
            stats["year_coverage"].add(q["year"])
        if q.get("marks"):
            stats["total_observed_marks"] += q["marks"]
            stats["marks_list"].append(q["marks"])
            stats["max_marks"] = max(stats["max_marks"], q["marks"])
        if q.get("question_type"):
            stats["question_types"][q["question_type"]] += 1
        if q.get("exam"):
            stats["exam_types"][q["exam"]] += 1

    # Finalize stats
    result = {}
    total_marks = sum(q.get("marks", 0) for q in questions if q.get("marks"))

    for topic, stats in topic_stats.items():
        years = sorted(stats["year_coverage"])
        consecutive = 1
        max_consecutive = 1
        for i in range(1, len(years)):
            if years[i] == years[i-1] + 1:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 1

        result[topic] = {
            "question_frequency": stats["question_frequency"],
            "paper_frequency": len(stats["paper_frequency"]),
            "year_coverage": len(stats["year_coverage"]) / len(total_years) if total_years else 0,
            "total_observed_marks": stats["total_observed_marks"],
            "mark_share": stats["total_observed_marks"] / total_marks if total_marks > 0 else 0,
            "avg_marks_per_question": sum(stats["marks_list"]) / len(stats["marks_list"]) if stats["marks_list"] else 0,
            "question_type_distribution": dict(stats["question_types"]),
            "exam_type_distribution": dict(stats["exam_types"]),
            "max_marks_single_question": stats["max_marks"],
            "consecutive_years": max_consecutive
        }

    return result

def analyze_exam_pattern(questions: List[Dict], classifications: Dict) -> Dict:
    """Analyze overall exam pattern from PYQs."""
    papers = set(q["source"] for q in questions if q.get("source"))

    # Get paper metadata
    paper_meta = {}
    for c in classifications.get("classifications", []):
        if c["classification"] == "PYQ" and c["file_path"] in papers:
            meta = c.get("pyq_metadata", {})
            paper_meta[c["file_path"]] = meta

    # Analyze sections
    sections = defaultdict(lambda: {"questions": 0, "marks": []})
    for q in questions:
        sec = q.get("section", "Unknown")
        sections[sec]["questions"] += 1
        if q.get("marks"):
            sections[sec]["marks"].append(q["marks"])

    section_details = {}
    for sec, data in sections.items():
        avg_marks = sum(data["marks"]) / len(data["marks"]) if data["marks"] else 0
        section_details[sec] = {
            "questions": data["questions"],
            "avg_marks": round(avg_marks, 1),
            "marks_range": [min(data["marks"]), max(data["marks"])] if data["marks"] else [0, 0]
        }

    # Theory vs problem ratio
    theory_types = {"explanation", "definition", "proof", "derivation", "analysis", "comparison"}
    problem_types = {"construction", "conversion", "minimization", "computation", "application"}

    theory_count = sum(1 for q in questions if q.get("question_type") in theory_types)
    problem_count = sum(1 for q in questions if q.get("question_type") in problem_types)

    return {
        "papers_analyzed": len(papers),
        "years_covered": sorted(set(q["year"] for q in questions if q.get("year"))),
        "exam_types": sorted(set(q["exam"] for q in questions if q.get("exam"))),
        "total_questions": len(questions),
        "total_marks": sum(q.get("marks", 0) for q in questions if q.get("marks")),
        "sections": sorted(sections.keys()),
        "section_details": section_details,
        "theory_vs_problem_ratio": theory_count / (theory_count + problem_count) if (theory_count + problem_count) > 0 else 0,
        "question_type_distribution": {
            t: sum(1 for q in questions if q.get("question_type") == t)
            for t in set(q.get("question_type") for q in questions)
        }
    }

def analyze_all(work_dir: str, syllabus_file: Optional[str] = None) -> Dict[str, Any]:
    """Run complete PYQ analysis."""
    work_path = Path(work_dir).resolve()

    # Load data
    questions_data = load_questions(work_dir)
    questions = questions_data["questions"]

    with open(work_path / "classifications.json") as f:
        classifications = json.load(f)

    # Load syllabus if available
    syllabus = {}
    if syllabus_file and Path(syllabus_file).exists():
        with open(syllabus_file) as f:
            syllabus = json.load(f)
    else:
        # Try to load from work dir
        syllabus_path = work_path / "syllabus.json"
        if syllabus_path.exists():
            with open(syllabus_path) as f:
                syllabus = json.load(f)

    # Map questions to topics
    questions = map_questions_to_topics(questions, syllabus)

    # Save updated questions
    questions_data["questions"] = questions
    with open(work_path / "questions.json", 'w') as f:
        json.dump(questions_data, f, indent=2, ensure_ascii=False)

    # Run analyses
    exact_reps = find_exact_repetitions(questions)
    families = find_question_families(questions)
    patterns = identify_patterns(questions)

    # Exam pattern
    exam_pattern = analyze_exam_pattern(questions, classifications)

    # Topic statistics
    years = exam_pattern["years_covered"]
    topic_stats = calculate_topic_statistics(questions, exam_pattern["papers_analyzed"], years)

    output = {
        "analysis_timestamp": datetime.now().isoformat(),
        "exam_pattern": exam_pattern,
        "exact_repetitions": [asdict(r) for r in exact_reps],
        "question_families": [asdict(f) for f in families],
        "pattern_repetitions": [asdict(p) for p in patterns],
        "topic_statistics": topic_stats
    }

    output_file = work_path / "pyq-analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"PYQ Analysis complete:")
    print(f"  Exact repetitions: {len(exact_reps)}")
    print(f"  Question families: {len(families)}")
    print(f"  Patterns: {len(patterns)}")
    print(f"  Topics with stats: {len(topic_stats)}")

    return output

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_pyqs.py <work_directory> [syllabus_file]")
        sys.exit(1)

    work_dir = sys.argv[1]
    syllabus_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        analyze_all(work_dir, syllabus_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()