#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic File Handler - Bronze Tier Agent Skill
Handles reading, summarizing, and moving files from Needs_Action
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class BasicFileHandler:
    def __init__(self, vault_path="."):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.done = self.vault_path / "Done"
        self.plans = self.vault_path / "Plans"
        self.handbook = self.vault_path / "Company_Handbook.md"

    def read_handbook_rules(self):
        """Read and return Company Handbook rules"""
        if self.handbook.exists():
            with open(self.handbook, 'r', encoding='utf-8') as f:
                return f.read()
        return "No handbook found"

    def summarize_file(self, file_path):
        """Read and summarize a markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        word_count = len(content.split())

        summary = {
            'filename': file_path.name,
            'lines': len(lines),
            'words': word_count,
            'preview': content[:200] + '...' if len(content) > 200 else content
        }
        return summary

    def create_plan(self, file_info):
        """Create Plan.md with checkboxes for next steps"""
        plan_content = f"""# Action Plan
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## File: {file_info['filename']}
- Lines: {file_info['lines']}
- Words: {file_info['words']}

## Preview:
{file_info['preview']}

## Next Steps:
- [ ] Review file content
- [ ] Verify compliance with Company Handbook
- [ ] Process according to rules
- [ ] Move to Done when complete

## Company Handbook Rules Applied:
{self.read_handbook_rules()}
"""

        plan_path = self.plans / "Plan.md"
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        return plan_path

    def move_to_done(self, file_path):
        """Move completed file to Done folder"""
        dest = self.done / file_path.name
        shutil.move(str(file_path), str(dest))
        return dest

    def process_file(self, filename):
        """Main processing function"""
        print(f"\n{'='*60}")
        print("BASIC FILE HANDLER - Starting Process")
        print(f"{'='*60}\n")

        # Reference handbook first
        print("📖 Checking Company Handbook rules...")
        rules = self.read_handbook_rules()
        print(f"✓ Rules loaded\n")

        # Read and summarize
        file_path = self.needs_action / filename
        if not file_path.exists():
            print(f"❌ Error: File not found: {file_path.absolute()}")
            return

        print(f"📄 Reading file: {file_path.absolute()}")
        file_info = self.summarize_file(file_path)
        print(f"✓ File summarized ({file_info['words']} words, {file_info['lines']} lines)\n")

        # Create plan
        print("📝 Creating action plan...")
        plan_path = self.create_plan(file_info)
        print(f"✓ Plan created: {plan_path.absolute()}\n")

        # Move to done
        print("📦 Moving file to Done...")
        done_path = self.move_to_done(file_path)
        print(f"✓ File moved: {done_path.absolute()}\n")

        print(f"{'='*60}")
        print("✅ SUCCESS - Process Complete")
        print(f"{'='*60}")
        print(f"\nProcessed: {done_path.absolute()}")
        print(f"Plan: {plan_path.absolute()}")

def main():
    handler = BasicFileHandler()

    # List available files
    md_files = list(handler.needs_action.glob("*.md"))

    if not md_files:
        print("No .md files found in Needs_Action folder")
        return

    print("Available files in Needs_Action:")
    for i, f in enumerate(md_files, 1):
        print(f"{i}. {f.name}")

    # Process first file (or modify to accept input)
    if md_files:
        handler.process_file(md_files[0].name)

if __name__ == "__main__":
    main()
