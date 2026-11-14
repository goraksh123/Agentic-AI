# scanner.py
# Scans all PHP/HTML/JS/CSS files in ERP

import os
import re
from pathlib import Path
from config import (
    ERP_PATH, SCAN_EXTENSIONS,
    SKIP_FOLDERS, MAX_FILE_SIZE
)

class ERPScanner:
    """
    Scans Font Accounting ERP codebase
    Extracts all relevant code information
    """

    def __init__(self):
        self.erp_path   = Path(ERP_PATH)
        self.all_files  = []
        self.php_files  = []
        self.js_files   = []
        self.css_files  = []

    # ── SCAN ALL FILES ──────────────────────
    def scan_all_files(self):
        """Scan entire ERP directory"""
        print(f"\n🔍 Scanning: {self.erp_path}")
        print("─" * 50)

        for root, dirs, files in os.walk(
            self.erp_path
        ):
            # Skip unwanted folders
            dirs[:] = [
                d for d in dirs
                if d not in SKIP_FOLDERS
            ]

            for file in files:
                ext = Path(file).suffix.lower()
                if ext in SCAN_EXTENSIONS:
                    full_path = Path(root) / file
                    self.all_files.append(full_path)

        print(f"✅ Found {len(self.all_files)} files")
        return self.all_files

    # ── READ FILE CONTENT ───────────────────
    def read_file(self, file_path):
        """Read file with size limit"""
        try:
            size = os.path.getsize(file_path)
            if size > MAX_FILE_SIZE:
                # Read only first part of large files
                with open(
                    file_path, 'r',
                    encoding='utf-8',
                    errors='ignore'
                ) as f:
                    content = f.read(MAX_FILE_SIZE)
                    return content + \
                        "\n... [FILE TRUNCATED]"

            with open(
                file_path, 'r',
                encoding='utf-8',
                errors='ignore'
            ) as f:
                return f.read()

        except Exception as e:
            return f"[ERROR READING FILE: {e}]"

    # ── EXTRACT PHP FUNCTIONS ───────────────
    def extract_php_functions(self, content):
        """Extract all function names from PHP"""
        pattern = r'function\s+(\w+)\s*\('
        functions = re.findall(pattern, content)
        return functions

    # ── EXTRACT PHP CLASSES ─────────────────
    def extract_php_classes(self, content):
        """Extract all class names from PHP"""
        pattern = r'class\s+(\w+)'
        classes = re.findall(pattern, content)
        return classes

    # ── EXTRACT SQL QUERIES ─────────────────
    def extract_sql_queries(self, content):
        """Extract SQL queries from PHP files"""
        # Find SELECT, INSERT, UPDATE, DELETE
        pattern = r'(SELECT|INSERT|UPDATE|DELETE' \
                  r'|CREATE TABLE|ALTER TABLE)' \
                  r'[^;]{10,200}'
        queries = re.findall(
            pattern, content,
            re.IGNORECASE | re.DOTALL
        )
        return queries[:10]  # max 10 per file

    # ── EXTRACT FORM FIELDS ─────────────────
    def extract_form_fields(self, content):
        """Extract HTML form inputs"""
        pattern = r'<input[^>]*name=["\']([^"\']+)'
        fields = re.findall(
            pattern, content, re.IGNORECASE
        )
        return fields

    # ── EXTRACT INCLUDES ────────────────────
    def extract_includes(self, content):
        """Extract included files"""
        pattern = r'(?:include|require)' \
                  r'(?:_once)?\s*[("\']([^"\'()]+)'
        includes = re.findall(
            pattern, content, re.IGNORECASE
        )
        return includes

    # ── GET FILE SUMMARY ────────────────────
    def get_file_summary(self, file_path):
        """Get complete summary of a PHP file"""
        content  = self.read_file(file_path)
        rel_path = file_path.relative_to(
            self.erp_path
        )

        summary = {
            "path"      : str(rel_path),
            "full_path" : str(file_path),
            "size"      : os.path.getsize(file_path),
            "content"   : content,
            "functions" : self.extract_php_functions(
                            content),
            "classes"   : self.extract_php_classes(
                            content),
            "sql_queries": self.extract_sql_queries(
                            content),
            "form_fields": self.extract_form_fields(
                            content),
            "includes"  : self.extract_includes(
                            content)
        }
        return summary

    # ── GROUP BY MODULE ─────────────────────
    def group_by_module(self):
        """Group files by folder (module)"""
        modules = {}

        for file_path in self.all_files:
            if file_path.suffix == '.php':
                # Get parent folder as module name
                rel     = file_path.relative_to(
                    self.erp_path
                )
                parts   = rel.parts
                module  = parts[0] if len(parts) > 1 \
                          else "root"

                if module not in modules:
                    modules[module] = []
                modules[module].append(file_path)

        return modules

    # ── PRINT SCAN SUMMARY ──────────────────
    def print_summary(self):
        """Print what was found"""
        php_count = sum(
            1 for f in self.all_files
            if f.suffix == '.php'
        )
        js_count  = sum(
            1 for f in self.all_files
            if f.suffix == '.js'
        )
        css_count = sum(
            1 for f in self.all_files
            if f.suffix == '.css'
        )

        print("\n📊 SCAN SUMMARY:")
        print("─" * 40)
        print(f"  PHP files  : {php_count}")
        print(f"  JS files   : {js_count}")
        print(f"  CSS files  : {css_count}")
        print(f"  Total      : {len(self.all_files)}")

        modules = self.group_by_module()
        print(f"\n📁 MODULES FOUND ({len(modules)}):")
        for mod, files in modules.items():
            print(f"  {mod:20} → {len(files)} files")