#!/usr/bin/env python3
"""
PDF Validation Script
Validates the generated study guide PDF for content completeness and visual issues
"""

import sys
import json
import subprocess
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ValidationIssue:
    issue_id: str
    type: str  # layout, content, visual, typography
    severity: str  # critical, major, minor, cosmetic
    page: int
    description: str
    element: Optional[str] = None
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False

@dataclass
class ValidationReport:
    timestamp: str
    pdf_path: str
    page_count: int
    automated_checks: Dict
    visual_issues: List[ValidationIssue]
    content_issues: List[ValidationIssue]
    summary: Dict

class PDFValidator:
    def __init__(self, pdf_path: str, content_model_path: str = None):
        self.pdf_path = Path(pdf_path)
        self.content_model_path = Path(content_model_path) if content_model_path else None
        self.doc = None
        self.content_model = None
        self.issues = []

    def load(self):
        """Load PDF and content model."""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")

        self.doc = fitz.open(self.pdf_path)

        if self.content_model_path and self.content_model_path.exists():
            with open(self.content_model_path) as f:
                self.content_model = json.load(f)

    def run_automated_checks(self) -> Dict:
        """Run automated content checks."""
        checks = {
            "pdf_readable": False,
            "text_extractable": False,
            "page_count_reasonable": False,
            "sections_present": {}
        }

        try:
            # Check PDF is readable
            checks["pdf_readable"] = True

            # Extract text from all pages
            full_text = ""
            for page in self.doc:
                full_text += page.get_text()

            checks["text_extractable"] = len(full_text) > 1000
            checks["page_count_reasonable"] = self.doc.page_count >= 5

            # Check for expected sections
            expected_sections = {
                "course_name": ["study guide", "comprehensive", "exam"],
                "syllabus": ["unit", "syllabus", "coverage"],
                "all_units": [],
                "pyq_analysis": ["previous.year", "pyq", "repetition", "question family"],
                "source_index": ["source index", "source", "material"],
                "revision_sections": ["revision", "formula", "definition", "algorithm"]
            }

            text_lower = full_text.lower()

            for section, keywords in expected_sections.items():
                if section == "all_units" and self.content_model:
                    # Check each unit title
                    units = self.content_model.get("units", [])
                    found = 0
                    for unit in units:
                        title = unit.get("title", "").lower()
                        if title and title in text_lower:
                            found += 1
                    checks["sections_present"][section] = found >= len(units) * 0.7
                else:
                    found = any(kw in text_lower for kw in keywords)
                    checks["sections_present"][section] = found

            # Check for missing content
            missing = [k for k, v in checks["sections_present"].items() if not v]
            checks["missing_content"] = missing

        except Exception as e:
            checks["error"] = str(e)

        return checks

    def check_visual_issues(self) -> List[ValidationIssue]:
        """Check for visual/layout issues by analyzing page content."""
        issues = []

        for page_num in range(self.doc.page_count):
            page = self.doc[page_num]

            # Get page dimensions
            rect = page.rect
            page_width = rect.width
            page_height = rect.height

            # Get text blocks with positions
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" not in block:
                    continue

                bbox = block.get("bbox", [0, 0, 0, 0])
                x0, y0, x1, y1 = bbox

                # Check for clipping (content too close to edges)
                margin_threshold = 20  # points
                if x0 < margin_threshold:
                    issues.append(ValidationIssue(
                        issue_id=f"clip-left-p{page_num+1}",
                        type="layout",
                        severity="major",
                        page=page_num + 1,
                        description=f"Content clipped at left margin (x={x0:.1f})",
                        element="text-block",
                        suggested_fix="Increase left margin in @page CSS or reduce content width",
                        auto_fixable=True
                    ))

                if x1 > page_width - margin_threshold:
                    issues.append(ValidationIssue(
                        issue_id=f"clip-right-p{page_num+1}",
                        type="layout",
                        severity="major",
                        page=page_num + 1,
                        description=f"Content clipped at right margin (x={x1:.1f}, page_width={page_width:.1f})",
                        element="text-block",
                        suggested_fix="Reduce content width or add max-width: 100% to containers",
                        auto_fixable=True
                    ))

                if y0 < margin_threshold:
                    issues.append(ValidationIssue(
                        issue_id=f"clip-top-p{page_num+1}",
                        type="layout",
                        severity="major",
                        page=page_num + 1,
                        description=f"Content clipped at top margin (y={y0:.1f})",
                        element="text-block",
                        suggested_fix="Increase top margin in @page CSS",
                        auto_fixable=True
                    ))

                if y1 > page_height - margin_threshold:
                    issues.append(ValidationIssue(
                        issue_id=f"clip-bottom-p{page_num+1}",
                        type="layout",
                        severity="major",
                        page=page_num + 1,
                        description=f"Content clipped at bottom margin (y={y1:.1f}, page_height={page_height:.1f})",
                        element="text-block",
                        suggested_fix="Increase bottom margin or adjust content height",
                        auto_fixable=True
                    ))

                # Check for orphan headings (heading at bottom of page)
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                    block_text += "\n"

                block_text = block_text.strip()
                if self.is_heading(block_text, block):
                    # Check if heading is in bottom 15% of page
                    if y1 > page_height * 0.85:
                        issues.append(ValidationIssue(
                            issue_id=f"orphan-heading-p{page_num+1}",
                            type="layout",
                            severity="minor",
                            page=page_num + 1,
                            description=f"Heading at bottom of page: '{block_text[:50]}...'",
                            element="heading",
                            suggested_fix="Add break-before: avoid-page to heading CSS",
                            auto_fixable=True
                        ))

            # Check for images/SVGs that might be clipped
            images = page.get_images(full=True)
            for img in images:
                # Get image position (approximate)
                try:
                    img_info = page.get_image_info(xrefs=[img[0]])
                    if img_info:
                        for info in img_info:
                            bbox = info.get("bbox", [0, 0, 0, 0])
                            if bbox[2] > page_width - 10 or bbox[3] > page_height - 10:
                                issues.append(ValidationIssue(
                                    issue_id=f"image-clipped-p{page_num+1}",
                                    type="visual",
                                    severity="major",
                                    page=page_num + 1,
                                    description="Image/SVG may be clipped at page edge",
                                    element="image",
                                    suggested_fix="Add max-width: 100% and height: auto to diagram containers",
                                    auto_fixable=True
                                ))
                except:
                    pass

        return issues

    def is_heading(self, text: str, block: Dict) -> bool:
        """Determine if a text block is a heading."""
        if not text or len(text) > 120:
            return False

        # Check font size
        max_size = 0
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                max_size = max(max_size, span.get("size", 0))

        return max_size > 13

    def check_content_completeness(self) -> List[ValidationIssue]:
        """Check if all expected content from model is present in PDF."""
        issues = []

        if not self.content_model:
            return issues

        # Extract all PDF text
        full_text = ""
        for page in self.doc:
            full_text += page.get_text()

        text_lower = full_text.lower()

        # Check units
        for unit in self.content_model.get("units", []):
            unit_title = unit.get("title", "").lower()
            if unit_title and unit_title not in text_lower:
                issues.append(ValidationIssue(
                    issue_id=f"missing-unit-{unit.get('unit_number')}",
                    type="content",
                    severity="major",
                    page=0,
                    description=f"Unit title not found in PDF: {unit.get('title')}",
                    element="unit-title",
                    suggested_fix="Check HTML generation for unit headers",
                    auto_fixable=False
                ))

            # Check high-priority topics
            for topic in unit.get("topics", []):
                if topic.get("priority") in ("VERY HIGH PRIORITY", "HIGH PRIORITY"):
                    topic_title = topic.get("title", "").lower()
                    if topic_title and topic_title not in text_lower:
                        issues.append(ValidationIssue(
                            issue_id=f"missing-topic-{topic.get('topic_id')}",
                            type="content",
                            severity="major",
                            page=0,
                            description=f"High-priority topic not found in PDF: {topic.get('title')}",
                            element="topic-title",
                            suggested_fix="Check topic rendering in HTML template",
                            auto_fixable=False
                        ))

        # Check PYQ analysis if available
        if self.content_model.get("pyq_available"):
            pyq_keywords = ["previous.year", "repetition", "question family", "exact repetition"]
            for kw in pyq_keywords:
                if kw not in text_lower:
                    issues.append(ValidationIssue(
                        issue_id=f"missing-pyq-{kw}",
                        type="content",
                        severity="minor",
                        page=0,
                        description=f"PYQ analysis keyword missing: {kw}",
                        element="pyq-section",
                        suggested_fix="Verify PYQ analysis section is rendered",
                        auto_fixable=False
                    ))

        # Check revision sections
        revision_keywords = ["formula", "definition", "algorithm", "revision"]
        for kw in revision_keywords:
            if kw not in text_lower:
                issues.append(ValidationIssue(
                    issue_id=f"missing-revision-{kw}",
                    type="content",
                    severity="minor",
                    page=0,
                    description=f"Revision section keyword missing: {kw}",
                    element="revision-section",
                    suggested_fix="Verify revision reference section is rendered",
                    auto_fixable=False
                ))

        # Check source index
        if "source index" not in text_lower and "source_index" not in text_lower:
            issues.append(ValidationIssue(
                issue_id="missing-source-index",
                type="content",
                severity="minor",
                page=0,
                description="Source index not found in PDF",
                element="source-index",
                suggested_fix="Add source index section to HTML template",
                auto_fixable=False
            ))

        return issues

    def check_typography(self) -> List[ValidationIssue]:
        """Check for typography issues."""
        issues = []

        for page_num in range(self.doc.page_count):
            page = self.doc[page_num]
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" not in block:
                    continue

                for line in block["lines"]:
                    for span in line["spans"]:
                        size = span.get("size", 12)
                        font = span.get("font", "")

                        # Check for tiny text
                        if size < 7:
                            issues.append(ValidationIssue(
                                issue_id=f"tiny-text-p{page_num+1}",
                                type="typography",
                                severity="minor",
                                page=page_num + 1,
                                description=f"Very small text detected: {size:.1f}pt",
                                element="text",
                                suggested_fix="Increase minimum font size in print CSS",
                                auto_fixable=True
                            ))

                        # Check for potential font fallback issues
                        if "cmap" in font.lower() or "identity" in font.lower():
                            issues.append(ValidationIssue(
                                issue_id=f"font-fallback-p{page_num+1}",
                                type="typography",
                                severity="cosmetic",
                                page=page_num + 1,
                                description=f"Possible font fallback: {font}",
                                element="text",
                                suggested_fix="Ensure web fonts are loaded before PDF generation",
                                auto_fixable=False
                            ))

        return issues

    def validate(self) -> ValidationReport:
        """Run all validation checks."""
        self.load()

        print(f"Validating PDF: {self.pdf_path}")
        print(f"Pages: {self.doc.page_count}")

        # Run checks
        automated = self.run_automated_checks()
        visual = self.check_visual_issues()
        content = self.check_content_completeness()
        typography = self.check_typography()

        all_issues = visual + content + typography

        # Count by severity
        severity_counts = {"critical": 0, "major": 0, "minor": 0, "cosmetic": 0}
        for issue in all_issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        passed = severity_counts["critical"] == 0 and severity_counts["major"] == 0

        report = ValidationReport(
            timestamp=datetime.now().isoformat(),
            pdf_path=str(self.pdf_path),
            page_count=self.doc.page_count,
            automated_checks=automated,
            visual_issues=visual,
            content_issues=content + typography,
            summary={
                "total_issues": len(all_issues),
                "critical": severity_counts["critical"],
                "major": severity_counts["major"],
                "minor": severity_counts["minor"],
                "cosmetic": severity_counts["cosmetic"],
                "passed": passed,
                "automated_checks_passed": all(automated.get(k, False) for k in
                    ["pdf_readable", "text_extractable", "page_count_reasonable"])
            }
        )

        return report

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_pdf.py <pdf_path> [content_model_path]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    content_model_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        validator = PDFValidator(pdf_path, content_model_path)
        report = validator.validate()

        # Save report
        output_path = Path(pdf_path).parent / "validation-report.json"
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)

        print(f"\nValidation Report:")
        print(f"  Pages: {report.page_count}")
        print(f"  Passed: {report.summary['passed']}")
        print(f"  Issues: {report.summary['total_issues']} "
              f"(C:{report.summary['critical']} M:{report.summary['major']} "
              f"m:{report.summary['minor']} c:{report.summary['cosmetic']})")
        print(f"  Report saved: {output_path}")

        if not report.summary["passed"]:
            print("\n❌ Validation FAILED - Major issues found")
            for issue in report.visual_issues + report.content_issues:
                if issue.severity in ("critical", "major"):
                    print(f"  [{issue.severity.upper()}] p{issue.page}: {issue.description}")
            sys.exit(1)
        else:
            print("\n✅ Validation PASSED")
            sys.exit(0)

    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()