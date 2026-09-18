#!/usr/bin/env python3
"""
Environment inspection script for the Comprehensive Course Study Guide plugin.
Checks for required and optional dependencies.
"""

import sys
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

def check_command(cmd: str, version_flag: str = "--version") -> Tuple[bool, str]:
    """Check if a command exists and get its version."""
    path = shutil.which(cmd)
    if not path:
        return False, ""
    try:
        result = subprocess.run([cmd, version_flag], capture_output=True, text=True, timeout=10)
        version = result.stdout.strip().split('\n')[0] if result.stdout else "unknown"
        return True, version
    except Exception:
        return True, "unknown"

def check_python_package(pkg: str) -> Tuple[bool, str]:
    """Check if a Python package is importable and get version."""
    try:
        module = __import__(pkg)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, ""

def check_node_package(pkg: str) -> Tuple[bool, str]:
    """Check if a Node package is available via npx."""
    try:
        result = subprocess.run(["npx", "--yes", pkg, "--version"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, ""
    except Exception:
        return False, ""

def main():
    print("=" * 60)
    print("Comprehensive Course Study Guide - Environment Inspection")
    print("=" * 60)

    results = {
        "required": {},
        "optional": {},
        "summary": {"required_ok": 0, "required_missing": 0, "optional_ok": 0, "optional_missing": 0}
    }

    # Required Python packages
    required_python = [
        ("fitz", "PyMuPDF"),
        ("docx", "python-docx"),
        ("pptx", "python-pptx"),
    ]

    print("\n📦 Required Python Packages:")
    for import_name, display_name in required_python:
        ok, version = check_python_package(import_name)
        status = "✅" if ok else "❌"
        print(f"  {status} {display_name}: {version if ok else 'NOT FOUND'}")
        results["required"][display_name] = {"available": ok, "version": version}
        if ok:
            results["summary"]["required_ok"] += 1
        else:
            results["summary"]["required_missing"] += 1

    # Required system commands
    required_commands = [
        ("pdftotext", "--version", "poppler-utils (pdftotext)"),
        ("pdfinfo", "-v", "poppler-utils (pdfinfo)"),
        ("python3", "--version", "Python 3"),
        ("node", "--version", "Node.js"),
        ("npm", "--version", "npm"),
    ]

    print("\n🔧 Required System Commands:")
    for cmd, flag, display_name in required_commands:
        ok, version = check_command(cmd, flag)
        status = "✅" if ok else "❌"
        print(f"  {status} {display_name}: {version if ok else 'NOT FOUND'}")
        results["required"][display_name] = {"available": ok, "version": version}
        if ok:
            results["summary"]["required_ok"] += 1
        else:
            results["summary"]["required_missing"] += 1

    # Required Node/Playwright
    print("\n🌐 Required Node/Playwright:")
    ok, version = check_node_package("playwright")
    status = "✅" if ok else "❌"
    print(f"  {status} Playwright: {version if ok else 'NOT FOUND (run: npx playwright install)'}")
    results["required"]["Playwright"] = {"available": ok, "version": version}
    if ok:
        results["summary"]["required_ok"] += 1
    else:
        results["summary"]["required_missing"] += 1

    # Optional dependencies
    optional_python = [
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("PIL", "Pillow"),
        ("pytesseract", "pytesseract"),
        ("pdfplumber", "pdfplumber"),
    ]

    print("\n📦 Optional Python Packages:")
    for import_name, display_name in optional_python:
        ok, version = check_python_package(import_name)
        status = "✅" if ok else "⚪"
        print(f"  {status} {display_name}: {version if ok else 'not installed'}")
        results["optional"][display_name] = {"available": ok, "version": version}
        if ok:
            results["summary"]["optional_ok"] += 1
        else:
            results["summary"]["optional_missing"] += 1

    optional_commands = [
        ("pandoc", "--version", "pandoc"),
        ("tesseract", "--version", "tesseract-ocr"),
        ("typst", "--version", "typst"),
    ]

    print("\n🔧 Optional System Commands:")
    for cmd, flag, display_name in optional_commands:
        ok, version = check_command(cmd, flag)
        status = "✅" if ok else "⚪"
        print(f"  {status} {display_name}: {version if ok else 'not installed'}")
        results["optional"][display_name] = {"available": ok, "version": version}
        if ok:
            results["summary"]["optional_ok"] += 1
        else:
            results["summary"]["optional_missing"] += 1

    # Optional Node packages
    print("\n🌐 Optional Node Packages:")
    ok, version = check_node_package("weasyprint")
    status = "✅" if ok else "⚪"
    print(f"  {status} WeasyPrint: {version if ok else 'not installed'}")
    results["optional"]["WeasyPrint"] = {"available": ok, "version": version}
    if ok:
        results["summary"]["optional_ok"] += 1
    else:
        results["summary"]["optional_missing"] += 1

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Required:  {results['summary']['required_ok']} OK, {results['summary']['required_missing']} MISSING")
    print(f"Optional:  {results['summary']['optional_ok']} OK, {results['summary']['optional_missing']} missing")

    if results["summary"]["required_missing"] > 0:
        print("\n❌ MISSING REQUIRED DEPENDENCIES - Plugin cannot run")
        print("\nInstallation hints:")
        print("  - poppler-utils: apt install poppler-utils / brew install poppler / choco install poppler")
        print("  - Python packages: pip install pymupdf python-docx python-pptx")
        print("  - Playwright: npx playwright install chromium")
        sys.exit(1)
    else:
        print("\n✅ All required dependencies available")
        sys.exit(0)

if __name__ == "__main__":
    main()