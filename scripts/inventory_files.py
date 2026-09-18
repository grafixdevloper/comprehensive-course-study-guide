#!/usr/bin/env python3
"""
File inventory script for the Comprehensive Course Study Guide plugin.
Recursively scans input directory, identifies relevant files, and creates an inventory.
"""

import os
import sys
import json
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Supported extensions
SUPPORTED_EXTENSIONS = {
    '.pdf', '.ppt', '.pptx', '.doc', '.docx',
    '.txt', '.md', '.csv', '.xlsx',
    '.jpg', '.jpeg', '.png', '.webp'
}

PRIORITY_EXTENSIONS = {
    '.pdf': 1,
    '.ppt': 2, '.pptx': 2,
    '.doc': 3, '.docx': 3,
    '.md': 4, '.txt': 4,
    '.jpg': 5, '.jpeg': 5, '.png': 5, '.webp': 5,
    '.csv': 6, '.xlsx': 6,
}

@dataclass
class FileInfo:
    path: str
    filename: str
    extension: str
    size: int
    modified: str
    page_count: Optional[int] = None
    slide_count: Optional[int] = None
    extractable: bool = True
    probable_classification: str = "OTHER"
    classification_confidence: float = 0.0
    priority: int = 99

def get_file_info(filepath: Path, root: Path) -> FileInfo:
    """Get basic file information."""
    stat = filepath.stat()
    rel_path = filepath.relative_to(root)
    ext = filepath.suffix.lower()

    return FileInfo(
        path=str(rel_path),
        filename=filepath.name,
        extension=ext,
        size=stat.st_size,
        modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
        priority=PRIORITY_EXTENSIONS.get(ext, 99)
    )

def estimate_pages(filepath: Path) -> Optional[int]:
    """Estimate page count for PDF files."""
    if filepath.suffix.lower() != '.pdf':
        return None
    try:
        import fitz
        doc = fitz.open(filepath)
        count = doc.page_count
        doc.close()
        return count
    except Exception:
        return None

def estimate_slides(filepath: Path) -> Optional[int]:
    """Estimate slide count for PPT/PPTX files."""
    ext = filepath.suffix.lower()
    if ext not in ('.ppt', '.pptx'):
        return None
    try:
        from pptx import Presentation
        prs = Presentation(filepath)
        return len(prs.slides)
    except Exception:
        return None

def classify_by_filename(filename: str) -> tuple[str, float]:
    """Classify file based on filename patterns."""
    name = filename.lower()

    # Course handout / syllabus
    if any(kw in name for kw in ['handout', 'course-handout', 'course_outline', 'course-outline']):
        return "COURSE_HANDOUT", 0.8
    if any(kw in name for kw in ['syllabus', 'syllabi']):
        return "SYLLABUS", 0.9

    # PYQ patterns
    pyq_keywords = ['pyq', 'previous', 'past', 'question', 'exam', 'midsem', 'endsem', 'midterm', 'final', 'quiz']
    year_pattern = any(c.isdigit() for c in name[:4])  # starts with year like 2023-

    if year_pattern and any(kw in name for kw in pyq_keywords):
        return "PYQ", 0.85
    if any(kw in name for kw in ['midsem', 'endsem', 'midterm', 'final exam', 'question-paper']):
        return "PYQ", 0.8

    # Lecture materials
    if any(kw in name for kw in ['lecture', 'lec-', 'lect-', 'class-', 'session-']):
        if any(kw in name for kw in ['slide', 'ppt', 'powerpoint']):
            return "LECTURE_SLIDES", 0.8
        return "LECTURE_NOTES", 0.75
    if any(kw in name for kw in ['notes', 'note-', 'summary']):
        return "LECTURE_NOTES", 0.7

    # Reference materials
    if any(kw in name for kw in ['reference', 'ref-', 'textbook', 'book-', 'chapter']):
        return "REFERENCE_MATERIAL", 0.7

    # Assignments
    if any(kw in name for kw in ['assignment', 'homework', 'hw-', 'problem-set', 'pset']):
        return "ASSIGNMENT", 0.8

    # Lab materials
    if any(kw in name for kw in ['lab', 'laboratory', 'practical']):
        return "LAB_MATERIAL", 0.8

    return "OTHER", 0.3

def create_inventory(input_dir: str, output_dir: str) -> Dict[str, Any]:
    """Create file inventory for the input directory."""
    root = Path(input_dir).resolve()
    output_path = Path(output_dir).resolve()

    if not root.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    # Find all relevant files
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(root.rglob(f"*{ext}"))

    # Also find files without extensions that might be relevant
    for filepath in root.rglob("*"):
        if filepath.is_file() and filepath.suffix == '' and filepath.name not in ['.DS_Store', 'Thumbs.db']:
            files.append(filepath)

    # Remove duplicates and sort
    unique_files = sorted(set(files), key=lambda f: (PRIORITY_EXTENSIONS.get(f.suffix.lower(), 99), str(f)))

    inventory = []
    for filepath in unique_files:
        # Skip files in the plugin's own directory
        if 'comprehensive-course-study-guide' in str(filepath):
            continue
        if '.study-guide-work' in str(filepath):
            continue
        if 'study-guide-output' in str(filepath):
            continue

        info = get_file_info(filepath, root)

        # Get page/slide counts
        info.page_count = estimate_pages(filepath)
        info.slide_count = estimate_slides(filepath)

        # Classify
        classification, confidence = classify_by_filename(info.filename)
        info.probable_classification = classification
        info.classification_confidence = confidence

        # Mark as non-extractable for certain formats
        if info.extension in ('.jpg', '.jpeg', '.png', '.webp'):
            info.extractable = False  # Will need OCR

        inventory.append(asdict(info))

    # Summary statistics
    by_classification = {}
    by_extension = {}
    total_size = 0

    for item in inventory:
        cls = item['probable_classification']
        by_classification[cls] = by_classification.get(cls, 0) + 1
        ext = item['extension']
        by_extension[ext] = by_extension.get(ext, 0) + 1
        total_size += item['size']

    result = {
        "input_directory": str(root),
        "scan_timestamp": datetime.now().isoformat(),
        "total_files": len(inventory),
        "total_size_bytes": total_size,
        "by_classification": by_classification,
        "by_extension": by_extension,
        "files": inventory
    }

    # Save inventory
    output_path.mkdir(parents=True, exist_ok=True)
    inventory_file = output_path / "inventory.json"
    with open(inventory_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Inventory created: {inventory_file}")
    print(f"Total files: {len(inventory)}")
    print(f"By classification: {by_classification}")
    print(f"By extension: {by_extension}")

    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python inventory_files.py <input_directory> [output_directory]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else ".study-guide-work"

    try:
        create_inventory(input_dir, output_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()