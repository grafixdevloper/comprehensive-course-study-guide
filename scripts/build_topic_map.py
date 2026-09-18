#!/usr/bin/env python3
"""
Topic mapping script for the Comprehensive Course Study Guide plugin.
Builds canonical topic hierarchy from syllabus and discovered topics.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SyllabusTopic:
    topic_id: str
    title: str
    keywords: List[str]
    subtopics: List[Dict]
    unit_number: int
    unit_title: str

def load_data(work_dir: str, user_syllabus: Optional[str] = None) -> tuple[Dict, Dict, Dict]:
    """Load all required data."""
    work_path = Path(work_dir).resolve()

    with open(work_path / "classifications.json") as f:
        classifications = json.load(f)

    with open(work_path / "sources.json") as f:
        sources = json.load(f)

    with open(work_path / "material-emphasis.json") as f:
        material_emphasis = json.load(f)

    # Load user syllabus if provided
    user_syllabus_data = {}
    if user_syllabus:
        # Parse user syllabus text into structure
        user_syllabus_data = parse_user_syllabus(user_syllabus)

    return classifications, sources, material_emphasis, user_syllabus_data

def parse_user_syllabus(text: str) -> Dict:
    """Parse user-provided syllabus text into structured format."""
    units = []
    current_unit = None

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Unit pattern: "UNIT 1" or "Unit 1:" or "1."
        unit_match = re.match(r'^(?:UNIT|Unit)\s*(\d+)\s*[:\-]?\s*(.*)', line, re.IGNORECASE)
        if unit_match:
            if current_unit:
                units.append(current_unit)
            current_unit = {
                "unit_number": int(unit_match.group(1)),
                "title": unit_match.group(2).strip() or f"Unit {unit_match.group(1)}",
                "topics": []
            }
            continue

        # Topic pattern: "- Topic" or "  Topic" or "  - Topic"
        if current_unit:
            topic_match = re.match(r'^[\-\*]\s*(.+)', line)
            if topic_match:
                topic_title = topic_match.group(1).strip()
                current_unit["topics"].append({
                    "title": topic_title,
                    "subtopics": []
                })
            elif line and not line.startswith(('UNIT', 'Unit')):
                # Subtopic or continuation
                if current_unit["topics"]:
                    current_unit["topics"][-1]["subtopics"].append({
                        "title": line
                    })

    if current_unit:
        units.append(current_unit)

    return {"units": units}

def extract_syllabus_from_files(classifications: Dict, sources: Dict) -> Dict:
    """Extract syllabus from COURSE_HANDOUT and SYLLABUS classified files."""
    syllabus_files = [
        c for c in classifications["classifications"]
        if c["classification"] in ("COURSE_HANDOUT", "SYLLABUS")
    ]

    # Get content from these files
    file_items = {}
    for item in sources["items"]:
        fp = item["source_file"]
        if fp not in file_items:
            file_items[fp] = []
        file_items[fp].append(item)

    all_syllabus_text = ""
    for sf in syllabus_files:
        items = file_items.get(sf["file_path"], [])
        text = "\n".join(item["content"] for item in items)
        all_syllabus_text += f"\n--- {sf['filename']} ---\n" + text

    return parse_user_syllabus(all_syllabus_text)

def build_topic_hierarchy(user_syllabus: Dict, extracted_syllabus: Dict, material_emphasis: Dict) -> Dict:
    """Build canonical topic hierarchy merging all sources."""
    # Priority: user_syllabus > extracted_syllabus > material_emphasis

    base_syllabus = user_syllabus if user_syllabus.get("units") else extracted_syllabus

    # Enhance with material emphasis data
    topic_coverage = material_emphasis.get("topic_coverage", {})

    units = []
    for unit_idx, unit in enumerate(base_syllabus.get("units", []), 1):
        unit_obj = {
            "unit_number": unit.get("unit_number", unit_idx),
            "title": unit.get("title", f"Unit {unit_idx}"),
            "topics": []
        }

        for topic_idx, topic in enumerate(unit.get("topics", []), 1):
            topic_title = topic.get("title", f"Topic {topic_idx}")
            topic_id = f"unit-{unit_obj['unit_number']}.topic-{topic_idx}"

            # Find matching coverage data
            coverage = None
            for cov_id, cov_data in topic_coverage.items():
                if topic_title.lower() in cov_data.get("canonical_name", "").lower() or \
                   cov_data.get("canonical_name", "").lower() in topic_title.lower():
                    coverage = cov_data
                    break

            topic_obj = {
                "topic_id": topic_id,
                "title": topic_title,
                "keywords": [topic_title.lower()] + [s.get("title", "").lower() for s in topic.get("subtopics", [])],
                "subtopics": [],
                "coverage": coverage
            }

            for sub_idx, subtopic in enumerate(topic.get("subtopics", []), 1):
                sub_title = subtopic.get("title", f"Subtopic {sub_idx}")
                sub_id = f"{topic_id}.subtopic-{sub_idx}"

                topic_obj["subtopics"].append({
                    "topic_id": sub_id,
                    "title": sub_title,
                    "keywords": [sub_title.lower()]
                })

            unit_obj["topics"].append(topic_obj)

        units.append(unit_obj)

    return {"units": units}

def discover_additional_topics(material_emphasis: Dict, existing_topics: Dict) -> List[Dict]:
    """Discover topics covered in lectures but not in syllabus."""
    existing_names = set()
    for unit in existing_topics.get("units", []):
        for topic in unit.get("topics", []):
            existing_names.add(topic["title"].lower())
            for sub in topic.get("subtopics", []):
                existing_names.add(sub["title"].lower())

    additional = []
    for cov_id, cov_data in material_emphasis.get("topic_coverage", {}).items():
        name = cov_data.get("canonical_name", "").lower()
        if name and name not in existing_names:
            # Check if it has significant coverage
            if cov_data.get("metrics", {}).get("depth_score", 0) > 0.5:
                additional.append({
                    "canonical_name": cov_data["canonical_name"],
                    "coverage": cov_data,
                    "reason": "Covered in lectures but not in syllabus"
                })

    return additional

def build_all(work_dir: str, user_syllabus_text: Optional[str] = None) -> Dict[str, Any]:
    """Build complete topic map."""
    work_path = Path(work_dir).resolve()
    classifications, sources, material_emphasis, user_syllabus = load_data(work_dir, user_syllabus_text)

    # Extract syllabus from files
    extracted_syllabus = extract_syllabus_from_files(classifications, sources)

    # Build hierarchy
    hierarchy = build_topic_hierarchy(user_syllabus, extracted_syllabus, material_emphasis)

    # Discover additional topics
    additional = discover_additional_topics(material_emphasis, hierarchy)

    # Create alias map
    aliases = {}
    for unit in hierarchy.get("units", []):
        for topic in unit.get("topics", []):
            canonical = topic["title"].lower()
            aliases[canonical] = topic["topic_id"]
            for sub in topic.get("subtopics", []):
                aliases[sub["title"].lower()] = sub["topic_id"]

    output = {
        "build_timestamp": datetime.now().isoformat(),
        "syllabus_source": "user" if user_syllabus.get("units") else "extracted",
        "units": hierarchy.get("units", []),
        "additional_topics": additional,
        "aliases": aliases,
        "total_units": len(hierarchy.get("units", [])),
        "total_topics": sum(len(u.get("topics", [])) for u in hierarchy.get("units", [])),
        "total_subtopics": sum(len(t.get("subtopics", [])) for u in hierarchy.get("units", []) for t in u.get("topics", []))
    }

    output_file = work_path / "topics.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Topic map built: {output['total_units']} units, {output['total_topics']} topics, {output['total_subtopics']} subtopics")
    print(f"Additional topics discovered: {len(additional)}")

    return output

def main():
    if len(sys.argv) < 2:
        print("Usage: python build_topic_map.py <work_directory> [user_syllabus_text]")
        sys.exit(1)

    work_dir = sys.argv[1]
    user_syllabus = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        build_all(work_dir, user_syllabus)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()