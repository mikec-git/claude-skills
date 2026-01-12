#!/usr/bin/env python3
"""
Markdown Syntax Validator for Claude Code Skills.

Validates that skill files are valid Markdown and adhere to Anthropic's
required format for Claude Code skills.

Checks performed:
1. YAML frontmatter syntax and structure
2. Markdown heading hierarchy
3. Code block matching (opening/closing)
4. Link syntax validation
5. List formatting consistency
6. Required skill structure patterns

Usage:
    python validate_syntax.py <skill_path>
    python validate_syntax.py ./my-skill/SKILL.md
    python validate_syntax.py ./my-skill/  # Validates all .md files
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SyntaxIssue:
    """A single syntax issue found during validation."""
    line_number: int
    category: str
    severity: str  # error, warning
    message: str
    context: Optional[str] = None


@dataclass
class SyntaxReport:
    """Complete syntax validation report."""
    file_path: Path
    issues: list[SyntaxIssue] = field(default_factory=list)

    def add(self, issue: SyntaxIssue):
        self.issues.append(issue)

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> list[SyntaxIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[SyntaxIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def print_report(self):
        status = "PASS" if self.passed else "FAIL"
        print(f"\n{'='*60}")
        print(f"MARKDOWN SYNTAX VALIDATION: {status}")
        print(f"{'='*60}")
        print(f"File: {self.file_path}")
        print()

        if not self.issues:
            print("No syntax issues found.")
        else:
            # Group by category
            categories = {}
            for issue in self.issues:
                if issue.category not in categories:
                    categories[issue.category] = []
                categories[issue.category].append(issue)

            for cat, issues in sorted(categories.items()):
                print(f"\n{cat}")
                print("-" * len(cat))
                for issue in issues:
                    icon = "✗" if issue.severity == "error" else "⚠"
                    print(f"  {icon} Line {issue.line_number}: {issue.message}")
                    if issue.context:
                        # Truncate long context lines
                        ctx = issue.context[:60] + "..." if len(issue.context) > 60 else issue.context
                        print(f"    → {ctx}")

        print()
        if self.errors:
            print(f"ERRORS: {len(self.errors)}")
        if self.warnings:
            print(f"WARNINGS: {len(self.warnings)}")
        print(f"VERDICT: {status}")


def validate_frontmatter_syntax(content: str, lines: list[str], report: SyntaxReport, is_skill_file: bool = True):
    """Validate YAML frontmatter syntax and structure."""
    # Check for frontmatter presence
    # Only require frontmatter for SKILL.md files
    if not content.startswith("---"):
        if is_skill_file:
            report.add(SyntaxIssue(
                line_number=1,
                category="Frontmatter",
                severity="error",
                message="SKILL.md must start with YAML frontmatter (---)"
            ))
        return

    # Find closing delimiter
    lines_text = content.split('\n')
    closing_line = None
    for i, line in enumerate(lines_text[1:], start=2):
        if line.strip() == "---":
            closing_line = i
            break

    if closing_line is None:
        report.add(SyntaxIssue(
            line_number=1,
            category="Frontmatter",
            severity="error",
            message="Frontmatter missing closing delimiter (---)"
        ))
        return

    # Extract frontmatter content
    frontmatter_lines = lines_text[1:closing_line-1]

    # Check for required fields
    has_name = False
    has_description = False

    for i, line in enumerate(frontmatter_lines, start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Check for valid YAML key-value syntax
        if ':' not in stripped:
            report.add(SyntaxIssue(
                line_number=i,
                category="Frontmatter",
                severity="error",
                message="Invalid YAML syntax: missing colon separator",
                context=line
            ))
            continue

        key = stripped.split(':', 1)[0].strip()

        # Check for leading whitespace issues (YAML is whitespace-sensitive)
        if line.startswith(' ') and not line.startswith('  '):
            report.add(SyntaxIssue(
                line_number=i,
                category="Frontmatter",
                severity="warning",
                message="Inconsistent indentation in YAML (use 2 spaces for nested items)",
                context=line
            ))

        if key == "name":
            has_name = True
        elif key == "description":
            has_description = True

    if not has_name:
        report.add(SyntaxIssue(
            line_number=1,
            category="Frontmatter",
            severity="error",
            message="Missing required 'name' field in frontmatter"
        ))

    if not has_description:
        report.add(SyntaxIssue(
            line_number=1,
            category="Frontmatter",
            severity="error",
            message="Missing required 'description' field in frontmatter"
        ))


def validate_heading_hierarchy(lines: list[str], report: SyntaxReport):
    """Validate heading hierarchy (no skipping levels)."""
    current_level = 0
    in_code_block = False
    in_agent_prompt = False

    for i, line in enumerate(lines, start=1):
        # Track code blocks to skip headings inside them
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Track agent-prompt tags (subagent prompts have their own heading structure)
        if '<agent-prompt' in line:
            in_agent_prompt = True
            continue
        if '</agent-prompt>' in line:
            in_agent_prompt = False
            continue

        if in_agent_prompt:
            continue

        # Match heading lines
        match = re.match(r'^(#{1,6})\s+', line)
        if match:
            level = len(match.group(1))

            # First heading can be any level
            if current_level == 0:
                current_level = level
                continue

            # Check for skipped levels (e.g., ## to ####)
            if level > current_level + 1:
                report.add(SyntaxIssue(
                    line_number=i,
                    category="Headings",
                    severity="warning",
                    message=f"Heading level skipped: jumped from H{current_level} to H{level}",
                    context=line.strip()
                ))

            current_level = level

            # Check for missing space after #
            if re.match(r'^#+[^#\s]', line):
                report.add(SyntaxIssue(
                    line_number=i,
                    category="Headings",
                    severity="error",
                    message="Heading missing space after # characters",
                    context=line.strip()
                ))


def validate_code_blocks(lines: list[str], report: SyntaxReport):
    """Validate code block delimiters are properly matched."""
    in_code_block = False
    code_block_start = 0
    code_block_lang = None

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Check for code block delimiter
        if stripped.startswith("```"):
            if not in_code_block:
                # Opening delimiter
                in_code_block = True
                code_block_start = i
                # Extract language specifier
                lang = stripped[3:].strip()
                code_block_lang = lang if lang else None
            else:
                # Closing delimiter
                in_code_block = False
                code_block_start = 0
                code_block_lang = None

    # Check for unclosed code block
    if in_code_block:
        report.add(SyntaxIssue(
            line_number=code_block_start,
            category="Code Blocks",
            severity="error",
            message="Unclosed code block (missing closing ```)",
            context=f"Code block opened at line {code_block_start}"
        ))


def validate_links(lines: list[str], report: SyntaxReport):
    """Validate Markdown link syntax."""
    # Pattern for markdown links: [text](url)
    link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]*)\)')
    # Pattern for broken links (missing parts)
    # These patterns look for markdown link syntax, not JSON arrays
    broken_link_patterns = [
        (re.compile(r'\[[^\]]*\]\([^)]*$'), "Link URL not closed with )"),
        # Look for [text at line end, but NOT preceded by : or = (JSON/code patterns)
        (re.compile(r'(?<![:\s=])\[[a-zA-Z][^\]]*$'), "Link text not closed with ]"),
        (re.compile(r'(?<!\])\([^)]+\.md\)'), "Link URL without link text"),
    ]

    in_code_block = False
    for i, line in enumerate(lines, start=1):
        # Track code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip lines inside code blocks
        if in_code_block:
            continue

        # Check for common link syntax errors
        for pattern, message in broken_link_patterns:
            if pattern.search(line):
                report.add(SyntaxIssue(
                    line_number=i,
                    category="Links",
                    severity="warning",
                    message=message,
                    context=line.strip()
                ))

        # Validate found links
        for match in link_pattern.finditer(line):
            text, url = match.groups()

            # Check for empty link text
            if not text.strip():
                report.add(SyntaxIssue(
                    line_number=i,
                    category="Links",
                    severity="warning",
                    message="Link has empty text",
                    context=match.group(0)
                ))

            # Check for empty URL
            if not url.strip():
                report.add(SyntaxIssue(
                    line_number=i,
                    category="Links",
                    severity="error",
                    message="Link has empty URL",
                    context=match.group(0)
                ))

            # Check for spaces in URL (should be encoded)
            if ' ' in url and not url.startswith('<'):
                report.add(SyntaxIssue(
                    line_number=i,
                    category="Links",
                    severity="warning",
                    message="Link URL contains spaces (should be URL-encoded)",
                    context=match.group(0)
                ))


def validate_lists(lines: list[str], report: SyntaxReport):
    """Validate list formatting consistency."""
    in_code_block = False

    for i, line in enumerate(lines, start=1):
        # Track code blocks to skip them
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Check for unordered list items
        unordered_match = re.match(r'^(\s*)([-*+])\s', line)
        if unordered_match:
            indent, marker = unordered_match.groups()

            # Check for inconsistent indentation (not multiple of 2)
            if len(indent) % 2 != 0 and len(indent) > 0:
                report.add(SyntaxIssue(
                    line_number=i,
                    category="Lists",
                    severity="warning",
                    message=f"List indentation is {len(indent)} spaces (recommend multiples of 2)",
                    context=line.rstrip()
                ))

        # Check for ordered list items
        ordered_match = re.match(r'^(\s*)(\d+)\.\s', line)
        if ordered_match:
            indent, num = ordered_match.groups()

            # Check for inconsistent indentation
            if len(indent) % 2 != 0 and len(indent) > 0:
                report.add(SyntaxIssue(
                    line_number=i,
                    category="Lists",
                    severity="warning",
                    message=f"List indentation is {len(indent)} spaces (recommend multiples of 2)",
                    context=line.rstrip()
                ))

        # Check for list item without space after marker
        # Exclude: horizontal rules (---, ***, ___), emphasis (**text, *text)
        stripped = line.strip()
        if re.match(r'^[-*+]\S', stripped):
            # Skip horizontal rules (3+ of same character)
            if re.match(r'^[-*_]{3,}\s*$', stripped):
                continue
            # Skip emphasis markers (** or * followed by word character)
            if re.match(r'^[*]{1,2}\w', stripped):
                continue
            report.add(SyntaxIssue(
                line_number=i,
                category="Lists",
                severity="error",
                message="List item missing space after marker",
                context=line.strip()
            ))


def validate_tables(lines: list[str], report: SyntaxReport):
    """Validate Markdown table syntax."""
    in_code_block = False
    table_start = None
    header_cols = 0

    for i, line in enumerate(lines, start=1):
        # Track code blocks
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        stripped = line.strip()

        # Detect table rows (lines starting and ending with |)
        if stripped.startswith("|") and stripped.endswith("|"):
            cols = len([c for c in stripped.split("|") if c.strip() or c == ""])

            if table_start is None:
                # First row (header)
                table_start = i
                header_cols = cols
            else:
                # Subsequent rows - check column count matches
                if cols != header_cols:
                    report.add(SyntaxIssue(
                        line_number=i,
                        category="Tables",
                        severity="error",
                        message=f"Table row has {cols} columns but header has {header_cols}",
                        context=stripped[:60] + "..." if len(stripped) > 60 else stripped
                    ))
        elif table_start is not None:
            # Table ended
            table_start = None
            header_cols = 0


def validate_emphasis(lines: list[str], report: SyntaxReport):
    """Validate emphasis markers (*, **, _, __)."""
    in_code_block = False

    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Skip inline code
        line_no_code = re.sub(r'`[^`]+`', '', line)

        # Check for unmatched bold markers (**)
        bold_count = len(re.findall(r'\*\*', line_no_code))
        if bold_count % 2 != 0:
            report.add(SyntaxIssue(
                line_number=i,
                category="Emphasis",
                severity="warning",
                message="Potentially unmatched bold markers (**)",
                context=line.strip()
            ))

        # Check for unmatched underscore bold markers (__)
        underscore_bold_count = len(re.findall(r'__', line_no_code))
        if underscore_bold_count % 2 != 0:
            report.add(SyntaxIssue(
                line_number=i,
                category="Emphasis",
                severity="warning",
                message="Potentially unmatched bold markers (__)",
                context=line.strip()
            ))


def validate_skill_structure(content: str, lines: list[str], report: SyntaxReport, is_skill_file: bool = True):
    """Validate skill-specific structural requirements."""
    # Only validate skill structure for SKILL.md files
    if not is_skill_file:
        return
    # Check for H1 heading after frontmatter
    in_frontmatter = content.startswith("---")
    found_h1 = False
    frontmatter_closed = False

    for i, line in enumerate(lines, start=1):
        if in_frontmatter:
            if i > 1 and line.strip() == "---":
                frontmatter_closed = True
                in_frontmatter = False
            continue

        if frontmatter_closed and not found_h1:
            if line.strip().startswith("# "):
                found_h1 = True
            elif line.strip() and not line.strip().startswith("#"):
                # Non-empty, non-heading content before H1
                report.add(SyntaxIssue(
                    line_number=i,
                    category="Skill Structure",
                    severity="warning",
                    message="Content appears before main heading (H1)",
                    context=line.strip()
                ))
                break

    if frontmatter_closed and not found_h1:
        # Check if there's any H1 at all
        if not re.search(r'^# ', content, re.MULTILINE):
            report.add(SyntaxIssue(
                line_number=1,
                category="Skill Structure",
                severity="warning",
                message="Skill file should have a main heading (# Title)"
            ))


def validate_inline_code(lines: list[str], report: SyntaxReport):
    """Validate inline code backtick matching."""
    in_code_block = False

    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Skip table cells that describe code block syntax (e.g., "Matched ``` delimiters")
        # These intentionally show backtick characters as content
        if '|' in line and '```' in line:
            continue

        # Remove matched inline code spans first, then count remaining
        line_processed = re.sub(r'`[^`]+`', '', line)
        backtick_count = line_processed.count('`')
        if backtick_count % 2 != 0:
            report.add(SyntaxIssue(
                line_number=i,
                category="Inline Code",
                severity="warning",
                message="Potentially unmatched inline code backtick",
                context=line.strip()
            ))


def validate_syntax(file_path: Path) -> SyntaxReport:
    """Run all syntax validations on a file."""
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    content = file_path.read_text()
    lines = content.split('\n')

    report = SyntaxReport(file_path=file_path)

    # Determine if this is a SKILL.md file (requires frontmatter and skill structure)
    is_skill_file = file_path.name == "SKILL.md"

    # Run all validations
    validate_frontmatter_syntax(content, lines, report, is_skill_file)
    validate_heading_hierarchy(lines, report)
    validate_code_blocks(lines, report)
    validate_links(lines, report)
    validate_lists(lines, report)
    validate_tables(lines, report)
    validate_emphasis(lines, report)
    validate_inline_code(lines, report)
    validate_skill_structure(content, lines, report, is_skill_file)

    return report


def validate_directory(dir_path: Path) -> list[SyntaxReport]:
    """Validate all markdown files in a directory."""
    reports = []
    md_files = list(dir_path.glob("*.md"))

    if not md_files:
        print(f"No markdown files found in {dir_path}")
        return reports

    for md_file in sorted(md_files):
        reports.append(validate_syntax(md_file))

    return reports


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"Error: Path not found: {path}")
        sys.exit(1)

    if path.is_dir():
        reports = validate_directory(path)
        all_passed = all(r.passed for r in reports)
        for report in reports:
            report.print_report()
        print(f"\n{'='*60}")
        print(f"OVERALL: {'PASS' if all_passed else 'FAIL'}")
        print(f"Files checked: {len(reports)}")
        sys.exit(0 if all_passed else 1)
    else:
        report = validate_syntax(path)
        report.print_report()
        sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
