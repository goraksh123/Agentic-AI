# agent.py
# Main ERP Documentation Agent

import os
import json
import time
from pathlib import Path
from tqdm import tqdm
from colorama import Fore, Style, init
import anthropic
import mysql.connector

from config import (
    ANTHROPIC_API_KEY, MODEL,
    MAX_TOKENS, DB_CONFIG, OUTPUT_PATH
)
from scanner import ERPScanner
from prompts import (
    MODULE_DOC_PROMPT,
    DATABASE_DOC_PROMPT,
    FLOW_DOC_PROMPT,
    SYSTEM_PROMPT
)

# Initialize colorama
init()

class ERPDocumentationAgent:
    """
    Main agent that reads PHP ERP code
    and generates complete documentation
    using Claude AI
    """

    def __init__(self):
        self.client  = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY
        )
        self.scanner = ERPScanner()
        self.output  = Path(OUTPUT_PATH)
        self.output.mkdir(exist_ok=True)

    # ── CALL CLAUDE AI ──────────────────────
    def ask_claude(self, prompt, context=""):
        """Send code to Claude for documentation"""
        try:
            message = self.client.messages.create(
                model      = MODEL,
                max_tokens = MAX_TOKENS,
                system     = SYSTEM_PROMPT,
                messages   = [
                    {
                        "role"   : "user",
                        "content": prompt
                    }
                ]
            )
            return message.content[0].text

        except Exception as e:
            print(f"{Fore.RED}Claude Error: {e}"
                  f"{Style.RESET_ALL}")
            return f"[ERROR: {e}]"

    # ── SAVE DOCUMENTATION ──────────────────
    def save_doc(self, content, filename, subfolder=""):
        """Save documentation to file"""
        if subfolder:
            folder = self.output / subfolder
            folder.mkdir(exist_ok=True)
            filepath = folder / filename
        else:
            filepath = self.output / filename

        with open(filepath, 'w',
                  encoding='utf-8') as f:
            f.write(content)

        print(f"  {Fore.GREEN}✅ Saved: "
              f"{filepath}{Style.RESET_ALL}")
        return filepath

    # ── DOCUMENT DATABASE ───────────────────
    def document_database(self):
        """Connect to MySQL and document all tables"""
        print(f"\n{Fore.CYAN}📊 SCANNING DATABASE..."
              f"{Style.RESET_ALL}")
        print("─" * 50)

        try:
            conn   = mysql.connector.connect(
                **DB_CONFIG
            )
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            tables_info = []

            for (table_name,) in tqdm(
                tables, desc="Reading tables"
            ):
                table_doc = {
                    "name"   : table_name,
                    "columns": [],
                    "indexes": [],
                    "sample" : []
                }

                # Get columns
                cursor.execute(
                    f"DESCRIBE `{table_name}`"
                )
                columns = cursor.fetchall()
                for col in columns:
                    table_doc["columns"].append({
                        "field"  : col[0],
                        "type"   : col[1],
                        "null"   : col[2],
                        "key"    : col[3],
                        "default": col[4]
                    })

                # Get row count
                cursor.execute(
                    f"SELECT COUNT(*) "
                    f"FROM `{table_name}`"
                )
                count = cursor.fetchone()[0]
                table_doc["row_count"] = count

                tables_info.append(table_doc)

            cursor.close()
            conn.close()

            print(f"✅ Found {len(tables_info)} tables")

            # Generate documentation with Claude
            tables_json = json.dumps(
                tables_info, indent=2
            )

            prompt = DATABASE_DOC_PROMPT.format(
                tables_info=tables_json
            )

            print("\n🤖 Generating DB documentation...")
            db_doc = self.ask_claude(prompt)

            self.save_doc(
                db_doc,
                "database_documentation.md",
                "database"
            )

            return tables_info

        except Exception as e:
            print(f"{Fore.RED}DB Error: {e}"
                  f"{Style.RESET_ALL}")
            return []

    # ── DOCUMENT MODULE ─────────────────────
    def document_module(self, module_name, files):
        """Generate documentation for one module"""
        print(f"\n  📁 Module: {module_name} "
              f"({len(files)} files)")

        # Collect all code from module
        all_code  = ""
        file_list = []

        for file_path in files[:10]:  # max 10 files
            summary = self.scanner.get_file_summary(
                file_path
            )
            file_list.append(summary['path'])

            # Add code with file header
            all_code += f"\n\n{'='*50}\n"
            all_code += f"FILE: {summary['path']}\n"
            all_code += f"FUNCTIONS: "
            all_code += f"{summary['functions']}\n"
            all_code += f"{'='*50}\n"
            all_code += summary['content'][:3000]

        # Limit total size
        all_code = all_code[:15000]

        # Generate module documentation
        prompt = MODULE_DOC_PROMPT.format(
            module_name  = module_name,
            file_list    = "\n".join(file_list),
            code_content = all_code
        )

        doc = self.ask_claude(prompt)

        # Save module doc
        safe_name = module_name.replace(
            "/", "_"
        ).replace("\\", "_")

        self.save_doc(
            doc,
            f"{safe_name}.md",
            "modules"
        )

        # Generate flow diagram
        flow_prompt = FLOW_DOC_PROMPT.format(
            module_name  = module_name,
            code_content = all_code[:8000]
        )
        flow_doc = self.ask_claude(flow_prompt)

        self.save_doc(
            flow_doc,
            f"{safe_name}_flow.md",
            "flows"
        )

        time.sleep(1)  # avoid rate limiting
        return doc

    # ── GENERATE MAIN README ────────────────
    def generate_readme(self, modules_found):
        """Generate main README.md"""

        module_list = "\n".join([
            f"- [{m}](modules/{m}.md)"
            for m in modules_found
        ])

        readme = f"""
# Font Accounting ERP — Complete Documentation

> Auto-generated by ERP Documentation Agent
> Generated on: {time.strftime('%Y-%m-%d %H:%M')}

## Overview
Font Accounting is a PHP-based ERP and
Accounting Framework with MySQL database.

## Modules
{module_list}

## Database
- [Database Documentation](database/database_documentation.md)

## Flow Diagrams
- [Module Flows](flows/)

## Quick Links
| Section | Description |
|---------|-------------|
| [Modules](modules/) | All ERP modules |
| [Database](database/) | DB schema & ERD |
| [Flows](flows/) | Process flows |
| [API](api/) | API endpoints |

## Tech Stack
- Language : PHP (< version 6)
- Database : MySQL
- Frontend : HTML, CSS, JavaScript
- Pattern  : MVC
"""
        self.save_doc(readme, "README.md")

    # ── RUN FULL AGENT ──────────────────────
    def run(self):
        """Run complete documentation agent"""

        print(f"""
{Fore.CYAN}
╔═══════════════════════════════════════╗
║   ERP DOCUMENTATION AGENT            ║
║   Font Accounting Framework          ║
╚═══════════════════════════════════════╝
{Style.RESET_ALL}""")

        # Step 1: Scan all files
        print(f"{Fore.YELLOW}STEP 1: Scanning ERP files..."
              f"{Style.RESET_ALL}")
        self.scanner.scan_all_files()
        self.scanner.print_summary()

        # Step 2: Document database
        print(f"\n{Fore.YELLOW}STEP 2: Documenting Database..."
              f"{Style.RESET_ALL}")
        self.document_database()

        # Step 3: Document each module
        print(f"\n{Fore.YELLOW}STEP 3: Documenting Modules..."
              f"{Style.RESET_ALL}")
        modules = self.scanner.group_by_module()
        modules_documented = []

        for module_name, files in tqdm(
            modules.items(),
            desc="Documenting modules"
        ):
            self.document_module(
                module_name, files
            )
            modules_documented.append(module_name)

        # Step 4: Generate README
        print(f"\n{Fore.YELLOW}STEP 4: Generating README..."
              f"{Style.RESET_ALL}")
        self.generate_readme(modules_documented)

        # Done!
        print(f"""
{Fore.GREEN}
╔═══════════════════════════════════════╗
║   ✅ DOCUMENTATION COMPLETE!          ║
║   Output: {OUTPUT_PATH:<28}║
╚═══════════════════════════════════════╝
{Style.RESET_ALL}""")

        print(f"📁 Open this folder to see docs:")
        print(f"   {Path(OUTPUT_PATH).absolute()}")


# ── RUN THE AGENT ───────────────────────
if __name__ == "__main__":
    agent = ERPDocumentationAgent()
    agent.run()