#!/usr/bin/env python3
"""
Master pipeline orchestration script for the Comprehensive Course Study Guide plugin.
Runs the complete analysis and generation pipeline.
"""

import sys
import os
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

class PipelineOrchestrator:
    def __init__(self, input_dir: str, output_dir: str = None, work_dir: str = None,
                 syllabus_text: str = None, course_name: str = "Course",
                 syllabus_covered: str = "Full Syllabus", verbose: bool = False,
                 keep_work: bool = False, pdf_only: bool = False):
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve() if output_dir else self.input_dir / "study-guide-output"
        self.work_dir = Path(work_dir).resolve() if work_dir else self.input_dir / ".study-guide-work"
        self.syllabus_text = syllabus_text
        self.course_name = course_name
        self.syllabus_covered = syllabus_covered
        self.verbose = verbose
        self.keep_work = keep_work
        self.pdf_only = pdf_only

        self.scripts_dir = Path(__file__).parent.resolve()
        self.plugin_dir = self.scripts_dir.parent
        self.templates_dir = self.plugin_dir / "templates"
        self.diagrams_dir = self.plugin_dir / "diagrams"

        self.log_lines = []

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {level}: {message}"
        self.log_lines.append(line)
        if self.verbose or level in ("WARNING", "ERROR"):
            print(line)

    def run_script(self, script_name: str, args: List[str] = None) -> bool:
        """Run a Python script from the scripts directory."""
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            self.log(f"Script not found: {script_path}", "ERROR")
            return False

        cmd = [sys.executable, str(script_path)] + (args or [])
        self.log(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    self.log(f"  {line}")
            if result.returncode != 0:
                self.log(f"Script failed (exit {result.returncode}): {result.stderr}", "ERROR")
                return False
            return True
        except subprocess.TimeoutExpired:
            self.log(f"Script timed out: {script_name}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Script error: {e}", "ERROR")
            return False

    def run_node_script(self, script_name: str, args: List[str] = None) -> bool:
        """Run a Node.js script from the scripts directory."""
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            self.log(f"Script not found: {script_path}", "ERROR")
            return False

        cmd = ["node", str(script_path)] + (args or [])
        self.log(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    self.log(f"  {line}")
            if result.returncode != 0:
                self.log(f"Script failed (exit {result.returncode}): {result.stderr}", "ERROR")
                return False
            return True
        except subprocess.TimeoutExpired:
            self.log(f"Script timed out: {script_name}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Script error: {e}", "ERROR")
            return False

    def copy_templates(self):
        """Copy template files to output directory."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Copy main template files
        for fname in ["styles.css", "print.css"]:
            src = self.templates_dir / fname
            dst = self.output_dir / fname
            if src.exists():
                shutil.copy2(src, dst)
                self.log(f"Copied template: {fname}")

        # Copy diagrams
        diagrams_dst = self.output_dir / "diagrams"
        diagrams_dst.mkdir(exist_ok=True)
        for fname in os.listdir(self.diagrams_dir):
            if fname.endswith(".js"):
                shutil.copy2(self.diagrams_dir / fname, diagrams_dst / fname)

    def generate_html(self, content_model_path: Path) -> Path:
        """Generate HTML from content model using template."""
        self.log("Generating HTML from content model...")

        # Load content model
        with open(content_model_path) as f:
            content = json.load(f)

        # Load HTML template
        template_path = self.templates_dir / "study-guide.html"
        with open(template_path) as f:
            template = f.read()

        # Prepare template variables
        # Convert content to JSON string for embedding
        content_json = json.dumps(content, ensure_ascii=False)

        # Simple template substitution (in production, use a proper templating engine)
        html = template.replace("{{content_json}}", content_json)
        html = html.replace("{{course}}", content.get("course", self.course_name))
        html = html.replace("{{syllabus_covered}}", content.get("syllabus_covered", self.syllabus_covered))
        html = html.replace("{{generation_date}}", content.get("generation_date", datetime.now().isoformat()))
        html = html.replace("{{pyq_available}}", str(content.get("pyq_available", False)).lower())

        # Handle conditional sections
        if content.get("pyq_available"):
            html = html.replace("{{#if pyq_available}}", "").replace("{{/if}}", "")
        else:
            # Remove PYQ sections
            import re
            html = re.sub(r"\{\{#if pyq_available\}\}.*?\{\{/if\}\}", "", html, flags=re.DOTALL)

        if content.get("disclaimer"):
            html = html.replace("{{disclaimer}}", content["disclaimer"])
        else:
            html = html.replace("{{#if disclaimer}}", "").replace("{{/if}}", "")
            html = html.replace("{{disclaimer}}", "")

        # Save HTML
        html_path = self.output_dir / "study-guide.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        self.log(f"HTML saved: {html_path}")
        return html_path

    def run_pipeline(self) -> Dict[str, Any]:
        """Run the complete pipeline."""
        self.log("=" * 60)
        self.log("COMPREHENSIVE COURSE STUDY GUIDE PIPELINE")
        self.log("=" * 60)
        self.log(f"Input: {self.input_dir}")
        self.log(f"Output: {self.output_dir}")
        self.log(f"Work: {self.work_dir}")

        # Clean work directory if not keeping
        if not self.keep_work and self.work_dir.exists():
            shutil.rmtree(self.work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)

        # Copy templates to output
        self.copy_templates()

        # Pipeline steps
        steps = [
            ("Environment Inspection", lambda: self.run_script("inspect_environment.py")),
            ("File Inventory", lambda: self.run_script("inventory_files.py", [str(self.input_dir), str(self.work_dir)])),
            ("Content Extraction", lambda: self.run_script("extract_materials.py", [str(self.input_dir), str(self.work_dir)])),
            ("Classification", lambda: self.run_script("classify_materials.py", [str(self.work_dir)])),
            ("Question Normalization", lambda: self.run_script("normalize_questions.py", [str(self.work_dir)])),
            ("PYQ Analysis", lambda: self.run_script("analyze_pyqs.py", [str(self.work_dir)])),
            ("Topic Map Building", lambda: self.run_script("build_topic_map.py", [str(self.work_dir), self.syllabus_text or ""])),
            ("Priority Calculation", lambda: self.run_script("calculate_priority.py", [str(self.work_dir)])),
            ("Document Generation", lambda: self.run_script("generate_document.py", [str(self.work_dir), str(self.output_dir), self.course_name, self.syllabus_covered])),
        ]

        for step_name, step_func in steps:
            self.log(f"\n--- STEP: {step_name} ---")
            if not step_func():
                self.log(f"Pipeline failed at: {step_name}", "ERROR")
                return {"success": False, "failed_step": step_name}

        # Generate HTML
        content_model_path = self.output_dir / "study-guide-content.json"
        if not content_model_path.exists():
            self.log("Content model not found!", "ERROR")
            return {"success": False, "error": "Content model not generated"}

        html_path = self.generate_html(content_model_path)

        # Render PDF
        self.log("\n--- STEP: PDF Rendering ---")
        pdf_path = self.output_dir / "study-guide.pdf"
        if not self.run_node_script("render_pdf.js", [
            "--html", str(html_path),
            "--pdf", str(pdf_path),
            "--work-dir", str(self.work_dir)
        ]):
            self.log("PDF rendering failed", "ERROR")
            return {"success": False, "error": "PDF rendering failed"}

        # Visual QA
        self.log("\n--- STEP: Visual QA ---")
        qa_dir = self.work_dir / "qa" / "pages"
        if not self.run_node_script("render_pdf_pages.js", [
            "--pdf", str(pdf_path),
            "--output", str(qa_dir)
        ]):
            self.log("Page rendering for QA failed", "WARNING")

        # Validate PDF
        self.log("\n--- STEP: PDF Validation ---")
        if not self.run_script("validate_pdf.py", [str(pdf_path), str(content_model_path)]):
            self.log("PDF validation failed", "WARNING")

        # Save generation log
        log_path = self.output_dir / "generation-log.txt"
        with open(log_path, 'w') as f:
            f.write('\n'.join(self.log_lines))

        # Clean up work directory if not keeping
        if not self.keep_work and self.work_dir.exists():
            shutil.rmtree(self.work_dir)
            self.log("Cleaned up work directory")

        self.log("\n" + "=" * 60)
        self.log("PIPELINE COMPLETED SUCCESSFULLY")
        self.log("=" * 60)

        return {
            "success": True,
            "pdf": str(pdf_path),
            "html": str(html_path),
            "output_dir": str(self.output_dir),
            "log": str(log_path)
        }

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive Course Study Guide Generator")
    parser.add_argument("input_dir", help="Input directory with course materials")
    parser.add_argument("-o", "--output", help="Output directory (default: input_dir/study-guide-output)")
    parser.add_argument("-w", "--work-dir", help="Work directory (default: input_dir/.study-guide-work)")
    parser.add_argument("-s", "--syllabus", help="Syllabus text (or @file to read from file)")
    parser.add_argument("--course-name", default="Course", help="Course name")
    parser.add_argument("--syllabus-covered", default="Full Syllabus", help="Syllabus coverage description")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--keep-work", action="store_true", help="Keep work directory after completion")
    parser.add_argument("--pdf-only", action="store_true", help="Generate only PDF (not implemented)")

    args = parser.parse_args()

    # Handle syllabus from file
    syllabus_text = args.syllabus
    if syllabus_text and syllabus_text.startswith("@"):
        with open(syllabus_text[1:]) as f:
            syllabus_text = f.read()

    orchestrator = PipelineOrchestrator(
        input_dir=args.input_dir,
        output_dir=args.output,
        work_dir=args.work_dir,
        syllabus_text=syllabus_text,
        course_name=args.course_name,
        syllabus_covered=args.syllabus_covered,
        verbose=args.verbose,
        keep_work=args.keep_work,
        pdf_only=args.pdf_only
    )

    result = orchestrator.run_pipeline()

    if result["success"]:
        print("\n✅ Study guide generated successfully!")
        print(f"  PDF: {result['pdf']}")
        print(f"  HTML: {result['html']}")
        print(f"  Output: {result['output_dir']}")
        sys.exit(0)
    else:
        print(f"\n❌ Pipeline failed: {result.get('error', result.get('failed_step', 'Unknown error'))}")
        sys.exit(1)

if __name__ == "__main__":
    main()