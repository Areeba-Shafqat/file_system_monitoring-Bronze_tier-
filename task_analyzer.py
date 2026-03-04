#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Analyzer - Bronze Tier Agent Skill
Analyzes tasks, identifies types, and routes appropriately
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class TaskAnalyzer:
    def __init__(self, vault_path="."):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.plans = self.vault_path / "Plans"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.handbook = self.vault_path / "Company_Handbook.md"

        # Sensitive keywords
        self.sensitive_keywords = ['payment', 'pay', 'invoice', 'transfer', 'confidential', 'sensitive']
        self.payment_threshold = 500

    def read_handbook_rules(self):
        """Read Company Handbook rules"""
        if self.handbook.exists():
            with open(self.handbook, 'r', encoding='utf-8') as f:
                return f.read()
        return "No handbook found"

    def identify_file_type(self, content):
        """Identify the type of file/task"""
        content_lower = content.lower()

        if any(keyword in content_lower for keyword in ['invoice', 'payment', 'bill']):
            return "payment_request"
        elif any(keyword in content_lower for keyword in ['email', 'reply', 'message']):
            return "communication"
        elif any(keyword in content_lower for keyword in ['report', 'summary', 'analysis']):
            return "report"
        else:
            return "file_drop"

    def extract_payment_amount(self, content):
        """Extract payment amounts from content"""
        # Look for patterns like $500, $1,000, etc.
        pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        matches = re.findall(pattern, content)

        amounts = []
        for match in matches:
            amount = float(match.replace(',', ''))
            amounts.append(amount)

        return amounts

    def check_approval_needed(self, content, file_type):
        """Check if approval is needed based on content"""
        reasons = []

        # Check for sensitive keywords
        content_lower = content.lower()
        for keyword in self.sensitive_keywords:
            if keyword in content_lower:
                reasons.append(f"Contains sensitive keyword: '{keyword}'")

        # Check payment amounts
        if file_type == "payment_request":
            amounts = self.extract_payment_amount(content)
            for amount in amounts:
                if amount > self.payment_threshold:
                    reasons.append(f"Payment amount ${amount:,.2f} exceeds threshold of ${self.payment_threshold}")

        return len(reasons) > 0, reasons

    def identify_steps(self, content, file_type):
        """Identify steps needed for multi-step tasks"""
        steps = []

        if file_type == "payment_request":
            steps = [
                "Verify payment details",
                "Check amount against approval threshold",
                "Confirm recipient information",
                "Process payment or escalate for approval"
            ]
        elif file_type == "communication":
            steps = [
                "Read message content",
                "Check Company Handbook for politeness rules",
                "Draft appropriate response",
                "Send reply"
            ]
        elif file_type == "report":
            steps = [
                "Review report requirements",
                "Gather necessary data",
                "Create report structure",
                "Complete and deliver report"
            ]
        else:
            steps = [
                "Review file content",
                "Determine appropriate action",
                "Execute action",
                "Verify completion"
            ]

        return steps

    def create_action_plan(self, file_info, file_type, steps, approval_needed, reasons):
        """Create detailed action plan"""
        plan_content = f"""# Task Analysis & Action Plan
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## File: {file_info['filename']}
**Type Identified:** {file_type.replace('_', ' ').title()}

## Analysis Summary:
- Lines: {file_info['lines']}
- Words: {file_info['words']}
- Approval Required: {'⚠️ YES' if approval_needed else '✓ NO'}

"""

        if approval_needed:
            plan_content += "## ⚠️ Approval Required - Reasons:\n"
            for reason in reasons:
                plan_content += f"- {reason}\n"
            plan_content += "\n"

        plan_content += "## Action Steps:\n"
        for i, step in enumerate(steps, 1):
            plan_content += f"- [ ] Step {i}: {step}\n"

        plan_content += f"\n## Company Handbook Rules:\n{self.read_handbook_rules()}\n"

        plan_content += f"\n## Content Preview:\n```\n{file_info['preview']}\n```\n"

        return plan_content

    def write_to_pending_approval(self, filename, content, reasons):
        """Write file to Pending_Approval folder"""
        approval_file = self.pending_approval / f"APPROVAL_NEEDED_{filename}"

        approval_content = f"""# APPROVAL REQUIRED
File: {filename}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Reasons for Approval:
"""
        for reason in reasons:
            approval_content += f"- {reason}\n"

        approval_content += f"\n## Original Content:\n{content}\n"

        with open(approval_file, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        return approval_file

    def analyze_file(self, filename):
        """Main analysis function with multi-step loop"""
        print(f"\n{'='*60}")
        print("TASK ANALYZER - Starting Analysis")
        print(f"{'='*60}\n")

        file_path = self.needs_action / filename
        if not file_path.exists():
            print(f"❌ Error: File not found: {file_path.absolute()}")
            return

        # Step 1: Read file
        print(f"📄 Step 1: Reading file: {file_path.absolute()}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        file_info = {
            'filename': filename,
            'lines': len(content.split('\n')),
            'words': len(content.split()),
            'preview': content[:300] + '...' if len(content) > 300 else content
        }
        print(f"✓ File read ({file_info['words']} words)\n")

        # Step 2: Identify type
        print("🔍 Step 2: Identifying file type...")
        file_type = self.identify_file_type(content)
        print(f"✓ Type identified: {file_type.replace('_', ' ').title()}\n")

        # Step 3: Check approval
        print("⚖️ Step 3: Checking if approval needed...")
        approval_needed, reasons = self.check_approval_needed(content, file_type)
        if approval_needed:
            print(f"⚠️ APPROVAL REQUIRED")
            for reason in reasons:
                print(f"  - {reason}")
        else:
            print(f"✓ No approval needed")
        print()

        # Step 4: Identify steps (multi-step loop)
        print("📋 Step 4: Creating multi-step action plan...")
        steps = self.identify_steps(content, file_type)
        print(f"✓ {len(steps)} steps identified\n")

        # Step 5: Create plan
        print("📝 Step 5: Writing action plan...")
        plan_content = self.create_action_plan(file_info, file_type, steps, approval_needed, reasons)
        plan_path = self.plans / "Plan.md"
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        print(f"✓ Plan created: {plan_path.absolute()}\n")

        # Step 6: Route to approval if needed
        if approval_needed:
            print("⚠️ Step 6: Routing to Pending_Approval...")
            approval_path = self.write_to_pending_approval(filename, content, reasons)
            print(f"✓ Approval file created: {approval_path.absolute()}\n")

        print(f"{'='*60}")
        print("✅ SUCCESS - Analysis Complete")
        print(f"{'='*60}")
        print(f"\nAnalyzed: {file_path.absolute()}")
        print(f"Type: {file_type.replace('_', ' ').title()}")
        print(f"Plan: {plan_path.absolute()}")
        if approval_needed:
            print(f"Approval: {approval_path.absolute()}")

def main():
    analyzer = TaskAnalyzer()

    # List available files
    md_files = list(analyzer.needs_action.glob("*.md"))

    if not md_files:
        print("No .md files found in Needs_Action folder")
        return

    print("Available files in Needs_Action:")
    for i, f in enumerate(md_files, 1):
        print(f"{i}. {f.name}")

    # Analyze first file
    if md_files:
        analyzer.analyze_file(md_files[0].name)

if __name__ == "__main__":
    main()
