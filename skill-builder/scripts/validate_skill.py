#!/usr/bin/env python3
"""
Skill Validator - Deterministic checks for Claude Code skills.

Performs structural and metadata validation without requiring LLM judgment.
Run terminology checks separately with check_terminology.py.

Usage:
    python validate_skill.py <skill_path>
    python validate_skill.py ./my-skill/SKILL.md
    python validate_skill.py ./my-skill/  # Finds SKILL.md in directory
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationReport:
    """Complete validation report for a skill."""
    skill_name: str
    skill_path: Path
    results: list[ValidationResult] = field(default_factory=list)

    def add(self, result: ValidationResult):
        self.results.append(result)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results if r.severity == "error")

    @property
    def errors(self) -> list[ValidationResult]:
        return [r for r in self.results if not r.passed and r.severity == "error"]

    @property
    def warnings(self) -> list[ValidationResult]:
        return [r for r in self.results if not r.passed and r.severity == "warning"]

    def print_report(self):
        status = "PASS" if self.passed else "FAIL"
        print(f"\n{'='*60}")
        print(f"SKILL VALIDATION REPORT: {status}")
        print(f"{'='*60}")
        print(f"Skill: {self.skill_name}")
        print(f"Path: {self.skill_path}")
        print()

        # Group by category
        categories = {}
        for r in self.results:
            cat = r.name.split(":")[0] if ":" in r.name else "General"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)

        for cat, results in categories.items():
            print(f"\n{cat}")
            print("-" * len(cat))
            for r in results:
                icon = "✓" if r.passed else "✗" if r.severity == "error" else "⚠"
                check_name = r.name.split(":")[-1].strip() if ":" in r.name else r.name
                print(f"  {icon} {check_name}: {r.message}")

        print()
        if self.errors:
            print(f"ERRORS: {len(self.errors)}")
        if self.warnings:
            print(f"WARNINGS: {len(self.warnings)}")
        print(f"VERDICT: {status}")


def parse_frontmatter(content: str) -> Optional[dict]:
    """
    Extract YAML frontmatter from skill file.
    Simple parser for key: value pairs. Handles quoted strings and multi-word values.
    """
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None

    frontmatter = {}
    for line in match.group(1).split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Remove surrounding quotes if present
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            frontmatter[key] = value
    return frontmatter if frontmatter else None


def validate_metadata(content: str, report: ValidationReport):
    """Validate skill metadata (frontmatter)."""
    frontmatter = parse_frontmatter(content)

    if not frontmatter:
        report.add(ValidationResult(
            "Metadata: Frontmatter",
            False,
            "No YAML frontmatter found. Expected ---\\nname: ...\\ndescription: ...\\n---"
        ))
        return

    # Check name
    name = frontmatter.get("name", "")

    if not name:
        report.add(ValidationResult(
            "Metadata: Name present",
            False,
            "Missing 'name' field in frontmatter"
        ))
    else:
        # Name format checks
        report.add(ValidationResult(
            "Metadata: Name length",
            len(name) <= 64,
            f"Name is {len(name)} chars (max 64)"
        ))

        report.add(ValidationResult(
            "Metadata: Name lowercase",
            name == name.lower(),
            f"Name must be lowercase: '{name}'"
        ))

        valid_chars = re.match(r'^[a-z0-9-]+$', name)
        report.add(ValidationResult(
            "Metadata: Name characters",
            bool(valid_chars),
            "Name must contain only lowercase letters, numbers, and hyphens"
        ))

        reserved = ["anthropic", "claude"]
        has_reserved = any(r in name.lower() for r in reserved)
        report.add(ValidationResult(
            "Metadata: No reserved words",
            not has_reserved,
            f"Name must not contain reserved words: {reserved}"
        ))

    # Check description
    description = frontmatter.get("description", "")

    if not description:
        report.add(ValidationResult(
            "Metadata: Description present",
            False,
            "Missing 'description' field in frontmatter"
        ))
    else:
        report.add(ValidationResult(
            "Metadata: Description length",
            len(description) <= 1024,
            f"Description is {len(description)} chars (max 1024)"
        ))

        # Check for first-person (I, my, we, our)
        first_person = re.search(r'\b(I|my|we|our)\b', description, re.IGNORECASE)
        report.add(ValidationResult(
            "Metadata: Third person",
            not first_person,
            "Description should use third person, not first person (I, my, we, our)",
            severity="warning"
        ))

        # Check for trigger phrases
        has_trigger = "use when" in description.lower() or "when" in description.lower()
        report.add(ValidationResult(
            "Metadata: Has triggers",
            has_trigger,
            "Description should include 'Use when...' trigger phrases",
            severity="warning"
        ))


def heading_to_slug(heading: str) -> str:
    """
    Convert a markdown heading to a GitHub-compatible anchor slug.

    Rules:
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove characters that aren't alphanumeric, hyphens, or underscores
    - Remove leading/trailing hyphens
    """
    slug = heading.lower()
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'[^a-z0-9_-]', '', slug)
    slug = slug.strip('-')
    return slug


def extract_headings(content: str) -> list[tuple[int, str, str]]:
    """
    Extract all headings from markdown content.

    Returns list of tuples: (level, heading_text, slug)
    Level 1 = #, Level 2 = ##, etc.
    """
    headings = []
    for line in content.split('\n'):
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            slug = heading_to_slug(text)
            headings.append((level, text, slug))
    return headings


def validate_toc(skill_path: Path, content: str, report: ValidationReport):
    """
    Validate table of contents format and link validity.

    Checks:
    1. TOC heading exists (## Contents or ## Table of Contents)
    2. TOC entries are properly formatted as [text](#anchor) links
    3. TOC anchor links point to actual headings in the document

    Note: Only applies to reference files, not SKILL.md itself.
    """
    # Skip SKILL.md - TOC only required for reference files
    if skill_path.name.upper() == "SKILL.MD":
        return

    lines = content.split('\n')
    line_count = len(lines)

    # Only check files over 500 lines
    if line_count <= 500:
        return

    # Find TOC section
    toc_match = re.search(r'^##\s*(Contents|Table of Contents)\s*$', content, re.MULTILINE | re.IGNORECASE)

    if not toc_match:
        # Required (error) for 1000+ lines, warning for 500-999 lines
        if line_count >= 1000:
            report.add(ValidationResult(
                "TOC: Presence",
                False,
                f"Files over 1000 lines ({line_count} lines) must have a '## Contents' or '## Table of Contents' section",
                severity="error"
            ))
        else:
            report.add(ValidationResult(
                "TOC: Presence",
                False,
                f"Files over 500 lines ({line_count} lines) should have a '## Contents' or '## Table of Contents' section",
                severity="warning"
            ))
        return

    report.add(ValidationResult(
        "TOC: Presence",
        True,
        "Table of contents found"
    ))

    # Extract all headings and their slugs
    headings = extract_headings(content)
    valid_slugs = {slug for _, _, slug in headings}

    # Find TOC section content (from TOC heading to next ## heading or ---)
    toc_start = toc_match.end()
    toc_end_match = re.search(r'^(##\s+[^#]|---)', content[toc_start:], re.MULTILINE)
    toc_end = toc_start + toc_end_match.start() if toc_end_match else len(content)
    toc_section = content[toc_start:toc_end]

    # Extract TOC entries - links in format [text](#anchor)
    toc_entries = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', toc_section)

    if not toc_entries:
        report.add(ValidationResult(
            "TOC: Format",
            False,
            "TOC should contain markdown links in format [Section Name](#anchor)",
            severity="warning"
        ))
        return

    report.add(ValidationResult(
        "TOC: Format",
        True,
        f"TOC contains {len(toc_entries)} entries with valid link format"
    ))

    # Validate each TOC entry links to an actual heading
    broken_links = []
    for text, anchor in toc_entries:
        if anchor not in valid_slugs:
            # Check if there's a close match (heading exists but slug doesn't match)
            close_matches = [
                (h_text, h_slug) for _, h_text, h_slug in headings
                if h_text.lower() == text.lower() and h_slug != anchor
            ]
            if close_matches:
                broken_links.append(
                    f"[{text}](#{anchor}) - heading exists but anchor should be #{close_matches[0][1]}"
                )
            else:
                broken_links.append(f"[{text}](#{anchor}) - no matching heading found")

    if broken_links:
        # Report first few broken links
        link_list = ", ".join(broken_links[:3])
        suffix = f" and {len(broken_links) - 3} more" if len(broken_links) > 3 else ""
        report.add(ValidationResult(
            "TOC: Link validity",
            False,
            f"Broken TOC links: {link_list}{suffix}",
            severity="warning"
        ))
    else:
        report.add(ValidationResult(
            "TOC: Link validity",
            True,
            f"All {len(toc_entries)} TOC links point to valid headings"
        ))


def extract_refs_outside_code_blocks(content: str) -> list[str]:
    """
    Extract markdown file references that are NOT inside fenced code blocks or inline code.

    Returns list of .md file paths referenced in the content.
    """
    lines = content.split('\n')
    in_code_block = False
    refs = []

    for line in lines:
        # Track code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip lines inside code blocks
        if in_code_block:
            continue

        # Remove inline code (backticks) before searching for refs
        # This prevents matching links inside `code` spans
        line_without_inline_code = re.sub(r'`[^`]+`', '', line)

        # Find markdown file references in this line
        line_refs = re.findall(r'\[.*?\]\(([^)]+\.md)\)', line_without_inline_code)
        refs.extend(line_refs)

    return refs


def validate_structure(skill_path: Path, content: str, report: ValidationReport):
    """Validate skill structure (file organization, line counts)."""
    lines = content.split('\n')

    # Line count
    report.add(ValidationResult(
        "Structure: Line count",
        len(lines) <= 500,
        f"SKILL.md is {len(lines)} lines (max 500)"
    ))

    # Validate TOC for long files (handles both existence and validity)
    validate_toc(skill_path, content, report)

    # Check for Windows paths
    windows_paths = re.findall(r'[A-Za-z]:\\|\\\\', content)
    report.add(ValidationResult(
        "Structure: Unix paths",
        not windows_paths,
        "Use forward slashes, not backslashes for paths"
    ))

    # Check reference file depth (if this is SKILL.md)
    if skill_path.name == "SKILL.md":
        skill_dir = skill_path.parent

        # Find all markdown file references (excluding those inside code blocks)
        refs = extract_refs_outside_code_blocks(content)
        nested_refs = []

        for ref in refs:
            ref_path = skill_dir / ref
            if ref_path.exists():
                ref_content = ref_path.read_text()
                # Check if reference file has its own .md references (excluding code blocks)
                nested = extract_refs_outside_code_blocks(ref_content)
                if nested:
                    nested_refs.append((ref, nested))

        report.add(ValidationResult(
            "Structure: Reference depth",
            not nested_refs,
            f"Reference files should not link to other .md files: {nested_refs}" if nested_refs else "References are one level deep"
        ))


def validate_references(skill_path: Path, content: str, report: ValidationReport):
    """Validate that referenced markdown files exist and are at most one level deep."""
    if not skill_path.name.endswith(".md"):
        return

    skill_dir = skill_path.parent

    # Find all markdown file references (excluding those in code blocks)
    refs = extract_refs_outside_code_blocks(content)

    for ref in refs:
        # Skip external URLs
        if ref.startswith("http://") or ref.startswith("https://"):
            continue

        # Resolve the reference path relative to the skill file
        ref_path = skill_dir / ref

        # Check if file exists
        if not ref_path.exists():
            report.add(ValidationResult(
                "References: File exists",
                False,
                f"Referenced file not found: {ref}"
            ))
        else:
            report.add(ValidationResult(
                "References: File exists",
                True,
                f"Referenced file exists: {ref}"
            ))

        # Check reference depth (should be at most one level deep from skill file)
        # Normalize the path and count directory components
        # Valid: "FILE.md", "subdir/FILE.md", "../FILE.md", "../sibling/FILE.md"
        # Invalid: "a/b/FILE.md", "../../FILE.md", "../a/b/FILE.md"
        ref_normalized = ref.replace("\\", "/")
        parts = ref_normalized.split("/")

        # Count parent traversals (..)
        parent_count = sum(1 for p in parts if p == "..")

        # Count forward directory components (excluding .., ., and filename)
        forward_dirs = [p for p in parts[:-1] if p not in ("..", ".")]
        forward_count = len(forward_dirs)

        # References should be at most one level in any direction
        # - One parent (..) plus one forward dir is OK (../sibling/FILE.md)
        # - More than one parent is too deep
        # - More than one forward dir is too deep
        is_too_deep = parent_count > 1 or forward_count > 1

        if is_too_deep:
            report.add(ValidationResult(
                "References: Depth",
                False,
                f"Reference too deep (max one level): {ref}"
            ))


def validate_no_emojis(content: str, report: ValidationReport):
    """Validate that skill files do not contain emojis."""
    # Regex pattern for common emoji ranges
    # This covers most Unicode emoji blocks
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
        "\U0001F680-\U0001F6FF"  # Transport and Map
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "]+",
        flags=re.UNICODE
    )

    lines = content.split('\n')
    emojis_found = []

    for i, line in enumerate(lines, start=1):
        matches = emoji_pattern.findall(line)
        if matches:
            for match in matches:
                emojis_found.append((i, match))

    if emojis_found:
        # Report first few emojis found
        emoji_list = ", ".join(f"'{e}' (line {ln})" for ln, e in emojis_found[:5])
        suffix = f" and {len(emojis_found) - 5} more" if len(emojis_found) > 5 else ""
        report.add(ValidationResult(
            "Content: No emojis",
            False,
            f"Emojis found: {emoji_list}{suffix}"
        ))
    else:
        report.add(ValidationResult(
            "Content: No emojis",
            True,
            "No emojis found"
        ))


def validate_file_types(skill_path: Path, report: ValidationReport):
    """Validate that skill directory contains only allowed file types."""
    # Only validate if we have a directory context
    if not skill_path.exists():
        return

    # Only validate file types for SKILL.md files or directories
    # Skip for arbitrary .md files to avoid scanning unrelated directories
    if skill_path.is_file() and skill_path.name != "SKILL.md":
        return

    skill_dir = skill_path.parent if skill_path.is_file() else skill_path

    # Allowed markdown extensions (anywhere in skill directory)
    markdown_extensions = {".md", ".markdown"}

    # Allowed script/code extensions (only in scripts/ directory)
    script_extensions = {
        # Python
        ".py", ".pyi", ".pyw",
        # JavaScript/TypeScript
        ".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx",
        # Shell
        ".sh", ".bash", ".zsh", ".fish",
        # Other languages
        ".rb", ".go", ".rs", ".pl", ".php", ".lua", ".r", ".R",
        # Config files
        ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf",
        # Data files that scripts might use
        ".csv", ".txt",
    }

    # Directories to ignore entirely
    ignored_dirs = {
        "__pycache__", ".git", ".svn", ".hg",
        "node_modules", ".venv", "venv", ".env",
        ".pytest_cache", ".mypy_cache", ".ruff_cache",
        "dist", "build", ".tox", ".eggs",
    }

    # Files to ignore
    ignored_files = {
        ".gitignore", ".gitattributes", ".editorconfig",
        ".DS_Store", "Thumbs.db",
        "__init__.py",  # Allow __init__.py in scripts
    }

    invalid_files = []

    # Walk the skill directory
    for item in skill_dir.rglob("*"):
        # Skip directories
        if item.is_dir():
            continue

        # Get path relative to skill directory
        try:
            rel_path = item.relative_to(skill_dir)
        except ValueError:
            continue

        # Skip ignored directories
        if any(ignored_dir in rel_path.parts for ignored_dir in ignored_dirs):
            continue

        # Skip ignored files
        if item.name in ignored_files:
            continue

        # Check file extension
        ext = item.suffix.lower()

        # Markdown files allowed anywhere
        if ext in markdown_extensions:
            continue

        # Script/config files only allowed in scripts/ directory
        if "scripts" in rel_path.parts:
            if ext in script_extensions:
                continue

        # If we get here, the file is not allowed
        invalid_files.append(str(rel_path))

    if invalid_files:
        # Report first few invalid files
        file_list = ", ".join(invalid_files[:5])
        suffix = f" and {len(invalid_files) - 5} more" if len(invalid_files) > 5 else ""
        report.add(ValidationResult(
            "Structure: File types",
            False,
            f"Unexpected files found: {file_list}{suffix}"
        ))
    else:
        report.add(ValidationResult(
            "Structure: File types",
            True,
            "All files have allowed types"
        ))


def validate_content(skill_path: Path, content: str, report: ValidationReport):
    """Validate content patterns (checklists, etc.)."""
    # Check for copyable checklists
    has_checklist = bool(re.search(r'- \[ \]', content))

    # Only warn if file seems to describe a workflow
    has_workflow_words = any(word in content.lower() for word in ['workflow', 'step', 'process', 'phase'])
    if has_workflow_words:
        report.add(ValidationResult(
            "Content: Copyable checklists",
            has_checklist,
            "Workflows should include copyable checklists (- [ ])",
            severity="warning"
        ))

    # Check for concrete examples (inline or via reference file)
    has_inline_examples = bool(re.search(r'##.*example|example:', content, re.IGNORECASE))
    has_example_ref = bool(re.search(r'\[.*?\]\([^)]*example[^)]*\.md\)', content, re.IGNORECASE))
    has_examples = has_inline_examples or has_example_ref
    report.add(ValidationResult(
        "Content: Has examples",
        has_examples,
        "Skill should include concrete examples (inline or via reference file)",
        severity="warning"
    ))

    # Check for pip/npm install commands near imports (only for non-Markdown files)
    if not skill_path.suffix.lower() in ('.md', '.markdown'):
        imports = re.findall(r'(?:import|from|require)\s+(\w+)', content)
        has_install_guidance = bool(re.search(r'pip install|npm install|yarn add', content))

        if imports:
            report.add(ValidationResult(
                "Content: Dependency install guidance",
                has_install_guidance,
                "Include install commands for dependencies",
                severity="warning"
            ))


def validate_skill(skill_path: Path) -> ValidationReport:
    """Run all validations on a skill."""
    # Handle directory vs file path
    if skill_path.is_dir():
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            print(f"Error: No SKILL.md found in {skill_path}")
            sys.exit(1)
        skill_path = skill_file

    if not skill_path.exists():
        print(f"Error: File not found: {skill_path}")
        sys.exit(1)

    content = skill_path.read_text()

    # Extract name from frontmatter for report
    frontmatter = parse_frontmatter(content)
    skill_name = frontmatter.get("name", "unknown") if frontmatter else "unknown"

    report = ValidationReport(skill_name=skill_name, skill_path=skill_path)

    # Run all validations
    validate_metadata(content, report)
    validate_structure(skill_path, content, report)
    validate_file_types(skill_path, report)
    validate_references(skill_path, content, report)
    validate_no_emojis(content, report)
    validate_content(skill_path, content, report)

    return report


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    report = validate_skill(skill_path)
    report.print_report()

    # Exit with error code if validation failed
    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
