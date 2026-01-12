#!/usr/bin/env python3
"""
Unit tests for validate_syntax.py

Tests cover:
- YAML frontmatter syntax validation
- Heading hierarchy validation
- Code block matching validation
- Link syntax validation
- List formatting validation
- Table syntax validation
- Emphasis marker validation
- Inline code backtick validation
- Skill structure validation
- SyntaxIssue and SyntaxReport dataclasses
- Integration tests for full validation pipeline
"""

import pytest
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validate_syntax import (
    validate_frontmatter_syntax,
    validate_heading_hierarchy,
    validate_code_blocks,
    validate_links,
    validate_lists,
    validate_tables,
    validate_emphasis,
    validate_inline_code,
    validate_skill_structure,
    validate_syntax,
    validate_directory,
    SyntaxIssue,
    SyntaxReport,
)


# =============================================================================
# SyntaxIssue Tests
# =============================================================================

class TestSyntaxIssue:
    """Tests for the SyntaxIssue dataclass."""

    def test_create_issue(self):
        """Basic issue creation should work."""
        issue = SyntaxIssue(
            line_number=10,
            category="Test",
            severity="error",
            message="Something is wrong"
        )
        assert issue.line_number == 10
        assert issue.category == "Test"
        assert issue.severity == "error"
        assert issue.message == "Something is wrong"
        assert issue.context is None

    def test_issue_with_context(self):
        """Issue with context should store it."""
        issue = SyntaxIssue(
            line_number=5,
            category="Links",
            severity="warning",
            message="Link issue",
            context="[text](url)"
        )
        assert issue.context == "[text](url)"

    def test_issue_severity_values(self):
        """Both error and warning severities should be valid."""
        error_issue = SyntaxIssue(1, "Cat", "error", "msg")
        warning_issue = SyntaxIssue(1, "Cat", "warning", "msg")
        assert error_issue.severity == "error"
        assert warning_issue.severity == "warning"


# =============================================================================
# SyntaxReport Tests
# =============================================================================

class TestSyntaxReport:
    """Tests for the SyntaxReport dataclass."""

    def test_empty_report_passes(self):
        """Empty report should pass."""
        report = SyntaxReport(file_path=Path("test.md"))
        assert report.passed is True
        assert len(report.issues) == 0

    def test_report_with_error_fails(self):
        """Report with error-severity issue should fail."""
        report = SyntaxReport(file_path=Path("test.md"))
        report.add(SyntaxIssue(1, "Test", "error", "Failed"))
        assert report.passed is False

    def test_report_with_warning_passes(self):
        """Report with only warnings should pass."""
        report = SyntaxReport(file_path=Path("test.md"))
        report.add(SyntaxIssue(1, "Test", "warning", "Minor issue"))
        assert report.passed is True

    def test_errors_property(self):
        """Errors property should return only error-severity issues."""
        report = SyntaxReport(file_path=Path("test.md"))
        report.add(SyntaxIssue(1, "A", "error", "Error"))
        report.add(SyntaxIssue(2, "B", "warning", "Warning"))
        report.add(SyntaxIssue(3, "C", "error", "Another error"))

        assert len(report.errors) == 2
        assert all(e.severity == "error" for e in report.errors)

    def test_warnings_property(self):
        """Warnings property should return only warning-severity issues."""
        report = SyntaxReport(file_path=Path("test.md"))
        report.add(SyntaxIssue(1, "A", "error", "Error"))
        report.add(SyntaxIssue(2, "B", "warning", "Warning"))
        report.add(SyntaxIssue(3, "C", "warning", "Another warning"))

        assert len(report.warnings) == 2
        assert all(w.severity == "warning" for w in report.warnings)


# =============================================================================
# validate_frontmatter_syntax Tests
# =============================================================================

class TestValidateFrontmatterSyntax:
    """Tests for the validate_frontmatter_syntax function."""

    def create_report(self):
        return SyntaxReport(file_path=Path("SKILL.md"))

    # Happy Path Tests

    def test_valid_frontmatter(self):
        """Valid frontmatter should not produce errors."""
        content = """---
name: my-skill
description: A test skill
---
# Content
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0

    def test_frontmatter_with_extra_fields(self):
        """Extra fields in frontmatter should be allowed."""
        content = """---
name: my-skill
description: A test skill
author: Test Author
version: 1.0.0
---
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0

    # Error Cases

    def test_missing_frontmatter_in_skill_file(self):
        """SKILL.md without frontmatter should produce error."""
        content = "# Just a heading\nContent here"
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        assert any(i.severity == "error" for i in report.issues)

    def test_missing_frontmatter_in_non_skill_file(self):
        """Non-SKILL.md without frontmatter should not produce error."""
        content = "# Just a heading\nContent here"
        lines = content.split('\n')
        report = SyntaxReport(file_path=Path("other.md"))
        validate_frontmatter_syntax(content, lines, report, is_skill_file=False)

        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0

    def test_unclosed_frontmatter(self):
        """Frontmatter without closing delimiter should produce error."""
        content = """---
name: my-skill
description: Unclosed
# No closing ---
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        assert any("closing" in i.message.lower() for i in report.issues)

    def test_missing_name_field(self):
        """Frontmatter without name should produce error."""
        content = """---
description: A skill without name
---
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        assert any("name" in i.message.lower() for i in report.issues)

    def test_missing_description_field(self):
        """Frontmatter without description should produce error."""
        content = """---
name: my-skill
---
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        assert any("description" in i.message.lower() for i in report.issues)

    def test_invalid_yaml_syntax(self):
        """Invalid YAML syntax should produce error."""
        content = """---
name my-skill
description: Missing colon in name
---
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        assert any("yaml" in i.message.lower() or "colon" in i.message.lower() for i in report.issues)

    # Quoted Key Tests

    def test_quoted_name_key_fails_validation(self):
        """Quoted 'name' key causes 'missing name' error.

        The validator checks for exact key match, so "name" != name.
        """
        content = """---
"name": my-skill
description: A skill
---
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        # Should report missing 'name' field
        assert any("name" in i.message.lower() and "missing" in i.message.lower()
                   for i in report.issues)

    def test_quoted_description_key_fails_validation(self):
        """Quoted 'description' key causes 'missing description' error."""
        content = """---
name: my-skill
"description": A skill
---
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        # Should report missing 'description' field
        assert any("description" in i.message.lower() and "missing" in i.message.lower()
                   for i in report.issues)

    def test_single_quoted_keys_fail_validation(self):
        """Single-quoted keys also fail validation."""
        content = """---
'name': my-skill
'description': A skill
---
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        errors = [i for i in report.issues if i.severity == "error"]
        # Should have errors for both missing fields
        assert len(errors) >= 2

    # Warning Cases

    def test_inconsistent_indentation(self):
        """Odd indentation should produce warning."""
        content = """---
name: my-skill
 description: Single space indent
---
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_frontmatter_syntax(content, lines, report, is_skill_file=True)

        warnings = [i for i in report.issues if i.severity == "warning"]
        assert any("indent" in w.message.lower() for w in warnings)


# =============================================================================
# validate_heading_hierarchy Tests
# =============================================================================

class TestValidateHeadingHierarchy:
    """Tests for the validate_heading_hierarchy function."""

    def create_report(self):
        return SyntaxReport(file_path=Path("test.md"))

    # Happy Path Tests

    def test_proper_hierarchy(self):
        """Proper heading hierarchy should not produce warnings."""
        lines = [
            "# H1",
            "## H2",
            "### H3",
            "## H2 again",
            "### H3 again"
        ]
        report = self.create_report()
        validate_heading_hierarchy(lines, report)

        assert len(report.issues) == 0

    def test_starting_with_h2(self):
        """Starting with H2 should be fine."""
        lines = [
            "## H2",
            "### H3",
        ]
        report = self.create_report()
        validate_heading_hierarchy(lines, report)

        assert len(report.issues) == 0

    # Warning Cases

    def test_skipped_level(self):
        """Skipping heading levels should produce warning."""
        lines = [
            "# H1",
            "### H3 (skipped H2)"
        ]
        report = self.create_report()
        validate_heading_hierarchy(lines, report)

        assert any("skipped" in i.message.lower() for i in report.issues)

    def test_multiple_skips(self):
        """Multiple level skips should all be reported."""
        lines = [
            "# H1",
            "#### H4 (skipped H2 and H3)",
            "## H2"
        ]
        report = self.create_report()
        validate_heading_hierarchy(lines, report)

        skip_issues = [i for i in report.issues if "skipped" in i.message.lower()]
        assert len(skip_issues) >= 1

    def test_heading_inside_code_block_ignored(self):
        """Headings inside code blocks should be ignored."""
        lines = [
            "# H1",
            "```python",
            "# This is a comment",
            "#### Not a real heading",
            "```",
            "## H2"
        ]
        report = self.create_report()
        validate_heading_hierarchy(lines, report)

        assert len(report.issues) == 0

    def test_missing_space_after_hash(self):
        """Missing space after # - test actual behavior.

        Note: The current implementation has the missing-space check inside
        the heading match block, but the heading regex requires a space.
        So lines like "##Invalid" won't be caught. This documents actual behavior.
        """
        lines = [
            "# Valid",
            "##Invalid heading"
        ]
        report = self.create_report()
        validate_heading_hierarchy(lines, report)

        # Due to implementation, ##Invalid is not detected as missing space
        # because the outer regex requires a space after #
        # This is a gap in the validation that could be improved
        assert len([i for i in report.issues if "space" in i.message.lower()]) == 0

    def test_heading_inside_agent_prompt_ignored(self):
        """Headings inside <agent-prompt> tags should be ignored.

        Agent-prompt tags contain prompts for subagents and may have
        their own heading hierarchy that shouldn't affect the main document.
        """
        lines = [
            "# Main Title",
            "## Section",
            "<agent-prompt>",
            "# Subagent Instructions",
            "#### Deep heading (would skip levels normally)",
            "</agent-prompt>",
            "### Subsection"
        ]
        report = self.create_report()
        validate_heading_hierarchy(lines, report)

        # No skip warning should be issued for headings inside agent-prompt
        assert len(report.issues) == 0

    def test_heading_after_agent_prompt_checked(self):
        """Headings after </agent-prompt> should resume normal checking."""
        lines = [
            "# Main Title",
            "## Section",
            "<agent-prompt>",
            "# Subagent",
            "</agent-prompt>",
            "#### Skipped levels (should trigger warning)"
        ]
        report = self.create_report()
        validate_heading_hierarchy(lines, report)

        # Should detect skip from ## to ####
        assert any("skipped" in i.message.lower() for i in report.issues)


# =============================================================================
# validate_code_blocks Tests
# =============================================================================

class TestValidateCodeBlocks:
    """Tests for the validate_code_blocks function."""

    def create_report(self):
        return SyntaxReport(file_path=Path("test.md"))

    # Happy Path Tests

    def test_matched_code_blocks(self):
        """Properly matched code blocks should not produce errors."""
        lines = [
            "```python",
            "print('hello')",
            "```",
            "",
            "```javascript",
            "console.log('hi')",
            "```"
        ]
        report = self.create_report()
        validate_code_blocks(lines, report)

        assert len(report.issues) == 0

    def test_empty_code_block(self):
        """Empty code block should be valid."""
        lines = [
            "```",
            "```"
        ]
        report = self.create_report()
        validate_code_blocks(lines, report)

        assert len(report.issues) == 0

    # Error Cases

    def test_unclosed_code_block(self):
        """Unclosed code block should produce error."""
        lines = [
            "```python",
            "print('hello')",
            "# No closing delimiter"
        ]
        report = self.create_report()
        validate_code_blocks(lines, report)

        assert any("unclosed" in i.message.lower() for i in report.issues)

    def test_unclosed_code_block_reports_start_line(self):
        """Unclosed code block should report the opening line number."""
        lines = [
            "Some text",
            "```python",
            "code here",
            "more code"
        ]
        report = self.create_report()
        validate_code_blocks(lines, report)

        issues = [i for i in report.issues if "unclosed" in i.message.lower()]
        assert len(issues) == 1
        assert issues[0].line_number == 2  # Line where ``` started

    def test_multiple_code_blocks_one_unclosed(self):
        """Multiple code blocks with one unclosed."""
        lines = [
            "```python",
            "first block",
            "```",
            "",
            "```javascript",
            "second block never closed"
        ]
        report = self.create_report()
        validate_code_blocks(lines, report)

        issues = [i for i in report.issues if "unclosed" in i.message.lower()]
        assert len(issues) == 1


# =============================================================================
# validate_links Tests
# =============================================================================

class TestValidateLinks:
    """Tests for the validate_links function."""

    def create_report(self):
        return SyntaxReport(file_path=Path("test.md"))

    # Happy Path Tests

    def test_valid_links(self):
        """Valid markdown links should not produce issues."""
        lines = [
            "[Link text](https://example.com)",
            "[Another link](path/to/file.md)",
            "[Third link](./local-file.txt)"
        ]
        report = self.create_report()
        validate_links(lines, report)

        # Filter out only error-level issues
        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0

    # Warning Cases

    def test_empty_link_text(self):
        """Empty link text should produce warning."""
        lines = ["[](https://example.com)"]
        report = self.create_report()
        validate_links(lines, report)

        assert any("empty text" in i.message.lower() for i in report.issues)

    def test_spaces_in_url(self):
        """Spaces in URL should produce warning."""
        lines = ["[Link](path/with spaces/file.md)"]
        report = self.create_report()
        validate_links(lines, report)

        assert any("space" in i.message.lower() for i in report.issues)

    # Error Cases

    def test_empty_url(self):
        """Empty URL should produce error."""
        lines = ["[Link text]()"]
        report = self.create_report()
        validate_links(lines, report)

        errors = [i for i in report.issues if i.severity == "error"]
        assert any("empty url" in i.message.lower() for i in errors)

    def test_links_in_code_block_ignored(self):
        """Links inside code blocks should be ignored."""
        lines = [
            "```markdown",
            "[Broken link]()",
            "```"
        ]
        report = self.create_report()
        validate_links(lines, report)

        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0


# =============================================================================
# validate_lists Tests
# =============================================================================

class TestValidateLists:
    """Tests for the validate_lists function."""

    def create_report(self):
        return SyntaxReport(file_path=Path("test.md"))

    # Happy Path Tests

    def test_valid_unordered_lists(self):
        """Valid unordered lists should not produce issues."""
        lines = [
            "- Item 1",
            "- Item 2",
            "  - Nested item",
            "  - Another nested",
            "- Item 3"
        ]
        report = self.create_report()
        validate_lists(lines, report)

        assert len(report.issues) == 0

    def test_valid_ordered_lists(self):
        """Valid ordered lists should not produce issues."""
        lines = [
            "1. First",
            "2. Second",
            "3. Third"
        ]
        report = self.create_report()
        validate_lists(lines, report)

        assert len(report.issues) == 0

    # Warning Cases

    def test_odd_indentation(self):
        """Odd indentation should produce warning."""
        lines = [
            "- Item 1",
            "   - Three space indent"  # 3 spaces instead of 2
        ]
        report = self.create_report()
        validate_lists(lines, report)

        warnings = [i for i in report.issues if i.severity == "warning"]
        assert any("indent" in w.message.lower() for w in warnings)

    # Error Cases

    def test_missing_space_after_marker(self):
        """Missing space after list marker should produce error."""
        lines = ["-Item without space"]
        report = self.create_report()
        validate_lists(lines, report)

        errors = [i for i in report.issues if i.severity == "error"]
        assert any("space" in e.message.lower() for e in errors)

    def test_horizontal_rule_not_flagged(self):
        """Horizontal rules should not be flagged as invalid lists."""
        lines = [
            "---",
            "***",
            "___"
        ]
        report = self.create_report()
        validate_lists(lines, report)

        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0

    def test_emphasis_not_flagged(self):
        """Emphasis markers should not be flagged as invalid lists."""
        lines = [
            "*emphasis*",
            "**bold**"
        ]
        report = self.create_report()
        validate_lists(lines, report)

        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0

    def test_lists_in_code_block_ignored(self):
        """Lists inside code blocks should be ignored."""
        lines = [
            "```",
            "-item",  # Would be invalid list item
            "```"
        ]
        report = self.create_report()
        validate_lists(lines, report)

        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0


# =============================================================================
# validate_tables Tests
# =============================================================================

class TestValidateTables:
    """Tests for the validate_tables function."""

    def create_report(self):
        return SyntaxReport(file_path=Path("test.md"))

    # Happy Path Tests

    def test_valid_table(self):
        """Valid table should not produce issues."""
        lines = [
            "| Header 1 | Header 2 |",
            "| -------- | -------- |",
            "| Cell 1   | Cell 2   |",
            "| Cell 3   | Cell 4   |"
        ]
        report = self.create_report()
        validate_tables(lines, report)

        assert len(report.issues) == 0

    # Error Cases

    def test_inconsistent_columns(self):
        """Table rows with inconsistent column counts should produce error."""
        lines = [
            "| Header 1 | Header 2 | Header 3 |",
            "| -------- | -------- | -------- |",
            "| Cell 1   | Cell 2   |"  # Missing third column
        ]
        report = self.create_report()
        validate_tables(lines, report)

        errors = [i for i in report.issues if i.severity == "error"]
        assert any("column" in e.message.lower() for e in errors)

    def test_table_in_code_block_ignored(self):
        """Tables inside code blocks should be ignored."""
        lines = [
            "```",
            "| Bad | Table |",
            "| x |",  # Inconsistent
            "```"
        ]
        report = self.create_report()
        validate_tables(lines, report)

        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0


# =============================================================================
# validate_emphasis Tests
# =============================================================================

class TestValidateEmphasis:
    """Tests for the validate_emphasis function."""

    def create_report(self):
        return SyntaxReport(file_path=Path("test.md"))

    # Happy Path Tests

    def test_matched_bold(self):
        """Matched bold markers should not produce warnings."""
        lines = ["This is **bold** text."]
        report = self.create_report()
        validate_emphasis(lines, report)

        assert len(report.issues) == 0

    def test_matched_underscore_bold(self):
        """Matched underscore bold should not produce warnings."""
        lines = ["This is __bold__ text."]
        report = self.create_report()
        validate_emphasis(lines, report)

        assert len(report.issues) == 0

    # Warning Cases

    def test_unmatched_bold(self):
        """Unmatched bold markers should produce warning."""
        lines = ["This is **bold without closing."]
        report = self.create_report()
        validate_emphasis(lines, report)

        warnings = [i for i in report.issues if i.severity == "warning"]
        assert any("bold" in w.message.lower() or "**" in w.message for w in warnings)

    def test_unmatched_underscore_bold(self):
        """Unmatched underscore bold should produce warning."""
        lines = ["This is __bold without closing."]
        report = self.create_report()
        validate_emphasis(lines, report)

        warnings = [i for i in report.issues if i.severity == "warning"]
        assert any("__" in w.message for w in warnings)

    def test_emphasis_in_code_ignored(self):
        """Emphasis markers inside inline code should be ignored."""
        lines = ["Use `**kwargs` for keyword arguments."]
        report = self.create_report()
        validate_emphasis(lines, report)

        # Should not flag **kwargs as unmatched bold
        assert len(report.issues) == 0

    def test_emphasis_in_code_block_ignored(self):
        """Emphasis markers inside code blocks should be ignored."""
        lines = [
            "```python",
            "def func(**kwargs):",
            "    pass",
            "```"
        ]
        report = self.create_report()
        validate_emphasis(lines, report)

        assert len(report.issues) == 0


# =============================================================================
# validate_inline_code Tests
# =============================================================================

class TestValidateInlineCode:
    """Tests for the validate_inline_code function."""

    def create_report(self):
        return SyntaxReport(file_path=Path("test.md"))

    # Happy Path Tests

    def test_matched_backticks(self):
        """Matched inline code backticks should not produce warnings."""
        lines = ["Use the `foo` function and `bar` method."]
        report = self.create_report()
        validate_inline_code(lines, report)

        assert len(report.issues) == 0

    def test_multiple_inline_code(self):
        """Multiple inline code segments should be fine."""
        lines = ["`one` `two` `three`"]
        report = self.create_report()
        validate_inline_code(lines, report)

        assert len(report.issues) == 0

    # Warning Cases

    def test_unmatched_backtick(self):
        """Unmatched backtick should produce warning."""
        lines = ["Use the `foo function without closing."]
        report = self.create_report()
        validate_inline_code(lines, report)

        warnings = [i for i in report.issues if i.severity == "warning"]
        assert any("backtick" in w.message.lower() for w in warnings)

    def test_backticks_in_code_block_ignored(self):
        """Backticks in code blocks should be ignored."""
        lines = [
            "```bash",
            "echo `date`",  # Shell backticks
            "```"
        ]
        report = self.create_report()
        validate_inline_code(lines, report)

        warnings = [i for i in report.issues if i.severity == "warning"]
        assert len(warnings) == 0


# =============================================================================
# validate_skill_structure Tests
# =============================================================================

class TestValidateSkillStructure:
    """Tests for the validate_skill_structure function."""

    def create_report(self):
        return SyntaxReport(file_path=Path("SKILL.md"))

    # Happy Path Tests

    def test_valid_skill_structure(self):
        """Valid skill structure should not produce warnings."""
        content = """---
name: my-skill
description: A skill
---

# My Skill

Content here.
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_skill_structure(content, lines, report, is_skill_file=True)

        warnings = [i for i in report.issues if i.severity == "warning"]
        assert len(warnings) == 0

    # Warning Cases

    def test_content_before_h1(self):
        """Content before H1 should produce warning."""
        content = """---
name: my-skill
description: A skill
---

Some content before the heading.

# My Skill
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_skill_structure(content, lines, report, is_skill_file=True)

        warnings = [i for i in report.issues if i.severity == "warning"]
        assert any("before" in w.message.lower() for w in warnings)

    def test_missing_h1(self):
        """Missing H1 heading should produce warning."""
        content = """---
name: my-skill
description: A skill
---

## Only H2 heading

Content here.
"""
        lines = content.split('\n')
        report = self.create_report()
        validate_skill_structure(content, lines, report, is_skill_file=True)

        warnings = [i for i in report.issues if i.severity == "warning"]
        assert any("h1" in w.message.lower() or "heading" in w.message.lower() for w in warnings)

    def test_non_skill_file_not_checked(self):
        """Non-SKILL.md files should not have skill structure checked."""
        content = "Just some content without frontmatter or headings."
        lines = content.split('\n')
        report = SyntaxReport(file_path=Path("other.md"))
        validate_skill_structure(content, lines, report, is_skill_file=False)

        assert len(report.issues) == 0


# =============================================================================
# validate_syntax Integration Tests
# =============================================================================

class TestValidateSyntaxIntegration:
    """Integration tests for the validate_syntax function."""

    def test_valid_skill_file(self):
        """A valid skill file should pass all checks."""
        content = """---
name: my-skill
description: A test skill
---

# My Skill

## Overview

This is a simple skill.

## Examples

- Item 1
- Item 2

```python
print("hello")
```
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False,
                                         prefix='SKILL') as f:
            f.write(content)
            f.flush()
            # Rename to SKILL.md
            skill_path = Path(f.name).parent / "SKILL.md"
            os.rename(f.name, skill_path)
            try:
                report = validate_syntax(skill_path)
                assert report.passed is True
            finally:
                os.unlink(skill_path)

    def test_file_with_errors(self):
        """A file with errors should fail."""
        content = """---
name: my-skill
---

# Heading

```python
# Unclosed code block
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False,
                                         prefix='SKILL') as f:
            f.write(content)
            f.flush()
            skill_path = Path(f.name).parent / "SKILL.md"
            os.rename(f.name, skill_path)
            try:
                report = validate_syntax(skill_path)
                assert report.passed is False
            finally:
                os.unlink(skill_path)

    def test_nonexistent_file(self):
        """Nonexistent file should exit with error."""
        with pytest.raises(SystemExit):
            validate_syntax(Path("/nonexistent/file.md"))


# =============================================================================
# validate_directory Integration Tests
# =============================================================================

class TestValidateDirectory:
    """Integration tests for the validate_directory function."""

    def test_validate_directory(self):
        """Should validate all markdown files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple .md files
            (Path(tmpdir) / "file1.md").write_text("# File 1\n\nContent.")
            (Path(tmpdir) / "file2.md").write_text("# File 2\n\nMore content.")

            reports = validate_directory(Path(tmpdir))
            assert len(reports) == 2

    def test_empty_directory(self):
        """Empty directory should return empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reports = validate_directory(Path(tmpdir))
            assert len(reports) == 0

    def test_directory_with_mixed_files(self):
        """Should only validate .md files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "readme.md").write_text("# README")
            (Path(tmpdir) / "script.py").write_text("print('hello')")
            (Path(tmpdir) / "data.json").write_text('{"key": "value"}')

            reports = validate_directory(Path(tmpdir))
            assert len(reports) == 1
            assert reports[0].file_path.name == "readme.md"


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================

class TestEdgeCases:
    """Edge cases and boundary condition tests."""

    def test_empty_file(self):
        """Empty file should be handled gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            f.flush()
            try:
                report = validate_syntax(Path(f.name))
                # Should not crash, may have issues
                assert report is not None
            finally:
                os.unlink(f.name)

    def test_only_whitespace(self):
        """File with only whitespace should be handled."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("   \n\n\t\t\n   ")
            f.flush()
            try:
                report = validate_syntax(Path(f.name))
                assert report is not None
            finally:
                os.unlink(f.name)

    def test_very_long_lines(self):
        """Very long lines should be handled."""
        content = "---\nname: test\ndescription: test\n---\n\n# H\n\n" + "x" * 10000
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False,
                                         prefix='SKILL') as f:
            f.write(content)
            f.flush()
            skill_path = Path(f.name).parent / "SKILL.md"
            os.rename(f.name, skill_path)
            try:
                report = validate_syntax(skill_path)
                assert report is not None
            finally:
                os.unlink(skill_path)

    def test_deeply_nested_headings(self):
        """H6 headings should be valid."""
        lines = [
            "# H1",
            "## H2",
            "### H3",
            "#### H4",
            "##### H5",
            "###### H6"
        ]
        report = SyntaxReport(file_path=Path("test.md"))
        validate_heading_hierarchy(lines, report)

        # No skipped levels
        assert len(report.issues) == 0

    def test_unicode_content(self):
        """Unicode content should be handled."""
        content = """---
name: test
description: A skill with unicode
---

# Cafe with accents

Content with emojis: 👍 🎉
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False,
                                         encoding='utf-8', prefix='SKILL') as f:
            f.write(content)
            f.flush()
            skill_path = Path(f.name).parent / "SKILL.md"
            os.rename(f.name, skill_path)
            try:
                report = validate_syntax(skill_path)
                assert report is not None
            finally:
                os.unlink(skill_path)

    def test_windows_line_endings(self):
        """Windows line endings should be handled."""
        content = "---\r\nname: test\r\ndescription: test\r\n---\r\n\r\n# Header\r\n"
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.md', delete=False) as f:
            f.write(content.encode('utf-8'))
            f.flush()
            try:
                report = validate_syntax(Path(f.name))
                assert report is not None
            finally:
                os.unlink(f.name)


# =============================================================================
# Security Tests - ReDoS Prevention
# =============================================================================

class TestReDoSPrevention:
    """Tests to ensure regex patterns don't cause catastrophic backtracking."""

    def create_report(self):
        return SyntaxReport(file_path=Path("test.md"))

    @pytest.mark.timeout(5)  # Should complete in under 5 seconds
    def test_deeply_nested_brackets_in_links(self):
        """Deeply nested brackets should not cause ReDoS."""
        # Pattern that could cause backtracking: [[[[[[[[[...]]]]]]]]]
        malicious_input = "[" * 50 + "text" + "]" * 50 + "(url)"
        lines = [malicious_input]
        report = self.create_report()

        # Should complete quickly, not hang
        validate_links(lines, report)
        assert report is not None

    @pytest.mark.timeout(5)
    def test_many_asterisks_in_emphasis(self):
        """Many asterisks should not cause ReDoS."""
        malicious_input = "*" * 100 + "text" + "*" * 100
        lines = [malicious_input]
        report = self.create_report()

        validate_emphasis(lines, report)
        assert report is not None

    @pytest.mark.timeout(5)
    def test_repeated_backticks(self):
        """Repeated backticks should not cause ReDoS."""
        malicious_input = "`" * 100 + "code" + "`" * 100
        lines = [malicious_input]
        report = self.create_report()

        validate_inline_code(lines, report)
        assert report is not None

    @pytest.mark.timeout(5)
    def test_long_table_with_many_pipes(self):
        """Long table rows with many pipes should not cause ReDoS."""
        # Create a table row with 100 columns
        malicious_input = "|" + " col |" * 100
        lines = [malicious_input, "|" + " --- |" * 100]
        report = self.create_report()

        validate_tables(lines, report)
        assert report is not None


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
