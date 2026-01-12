#!/usr/bin/env python3
"""
Unified Skill Validator - Runs all validation checks and produces a combined report.

This script orchestrates all skill validators:
1. validate_syntax.py - Markdown syntax validation
2. validate_skill.py - Structural and metadata validation
3. check_terminology.py - Terminology consistency checks

Usage:
    python validate_all.py <skill_path>
    python validate_all.py ./my-skill/SKILL.md
    python validate_all.py ./my-skill/
    python validate_all.py ./my-skill/ --json
    python validate_all.py ./my-skill/ --config ./custom_terminology.yaml

Output:
    Human-readable summary by default, or JSON with --json flag.
"""

import sys
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# Import the individual validators
from validate_syntax import validate_syntax, validate_directory, SyntaxReport
from validate_skill import validate_skill, ValidationReport
from check_terminology import check_terminology, format_for_llm as format_terminology


# Orchestrator metadata
ORCHESTRATOR_VERSION = "1.0.0"


@dataclass
class ValidatorSummary:
    """Summary of a single validator's results."""
    name: str
    version: str
    passed: bool
    error_count: int
    warning_count: int
    review_count: int = 0  # For terminology candidates


@dataclass
class UnifiedReport:
    """Combined report from all validators."""
    skill_path: str
    overall_passed: bool
    summaries: list[ValidatorSummary] = field(default_factory=list)
    syntax_issues: list[dict] = field(default_factory=list)
    skill_issues: list[dict] = field(default_factory=list)
    terminology_candidates: list[dict] = field(default_factory=list)
    terminology_guidance: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


def run_syntax_validation(skill_path: Path) -> tuple[ValidatorSummary, list[dict]]:
    """Run syntax validation and return summary + issues."""
    if skill_path.is_dir():
        reports = validate_directory(skill_path)
        all_issues = []
        total_errors = 0
        total_warnings = 0
        all_passed = True

        for report in reports:
            all_passed = all_passed and report.passed
            total_errors += len(report.errors)
            total_warnings += len(report.warnings)
            for issue in report.issues:
                all_issues.append({
                    "file": str(report.file_path),
                    "line": issue.line_number,
                    "category": issue.category,
                    "severity": issue.severity,
                    "message": issue.message,
                    "context": issue.context
                })

        summary = ValidatorSummary(
            name="validate_syntax.py",
            version="1.0.0",
            passed=all_passed,
            error_count=total_errors,
            warning_count=total_warnings
        )
        return summary, all_issues
    else:
        report = validate_syntax(skill_path)
        issues = []
        for issue in report.issues:
            issues.append({
                "file": str(report.file_path),
                "line": issue.line_number,
                "category": issue.category,
                "severity": issue.severity,
                "message": issue.message,
                "context": issue.context
            })

        summary = ValidatorSummary(
            name="validate_syntax.py",
            version="1.0.0",
            passed=report.passed,
            error_count=len(report.errors),
            warning_count=len(report.warnings)
        )
        return summary, issues


def run_skill_validation(skill_path: Path) -> tuple[ValidatorSummary, list[dict]]:
    """Run skill structure/metadata validation and return summary + issues."""
    report = validate_skill(skill_path)
    issues = []

    for result in report.results:
        if not result.passed:
            issues.append({
                "check": result.name,
                "severity": result.severity,
                "message": result.message
            })

    summary = ValidatorSummary(
        name="validate_skill.py",
        version="1.0.0",
        passed=report.passed,
        error_count=len(report.errors),
        warning_count=len(report.warnings)
    )
    return summary, issues


def run_terminology_check(skill_path: Path, config_path: Optional[Path] = None) -> tuple[ValidatorSummary, list[dict], dict]:
    """Run terminology checks and return summary + candidates + guidance."""
    result = check_terminology(skill_path, config_path)

    if "error" in result:
        summary = ValidatorSummary(
            name="check_terminology.py",
            version=result.get("metadata", {}).get("version", "unknown"),
            passed=False,
            error_count=1,
            warning_count=0
        )
        return summary, [{"error": result["error"]}], {}

    candidates = result.get("candidates_for_review", [])
    guidance = result.get("decision_guidance", {})

    # Terminology check "passes" if there are no candidates
    # But it's not a failure if there are candidates - they need review
    summary = ValidatorSummary(
        name="check_terminology.py",
        version=result.get("metadata", {}).get("version", "2.0.0"),
        passed=True,  # Terminology issues are warnings, not failures
        error_count=0,
        warning_count=0,
        review_count=len(candidates)
    )

    return summary, candidates, guidance


def format_human_readable(report: UnifiedReport) -> str:
    """Format the unified report for human reading."""
    output = []

    # Header
    output.append("=" * 70)
    output.append("UNIFIED SKILL VALIDATION REPORT")
    output.append("=" * 70)
    output.append(f"Skill: {report.skill_path}")
    output.append(f"Orchestrator: validate_all.py v{ORCHESTRATOR_VERSION}")
    output.append("")

    # Quick summary
    output.append("SUMMARY")
    output.append("-" * 70)
    overall_status = "PASS" if report.overall_passed else "FAIL"
    output.append(f"Overall Status: {overall_status}")
    output.append("")

    for summary in report.summaries:
        status = "PASS" if summary.passed else "FAIL"
        review_note = f", {summary.review_count} for review" if summary.review_count > 0 else ""
        output.append(f"  {summary.name}: {status} ({summary.error_count} errors, {summary.warning_count} warnings{review_note})")

    output.append("")

    # Detailed issues by validator
    if report.syntax_issues:
        output.append("SYNTAX ISSUES")
        output.append("-" * 70)
        for issue in report.syntax_issues:
            icon = "[ERROR]" if issue["severity"] == "error" else "[WARN]"
            output.append(f"  {icon} {issue['file']}:{issue['line']} - {issue['category']}")
            output.append(f"         {issue['message']}")
            if issue.get("context"):
                ctx = issue["context"][:50] + "..." if len(issue["context"]) > 50 else issue["context"]
                output.append(f"         Context: {ctx}")
        output.append("")

    if report.skill_issues:
        output.append("SKILL STRUCTURE ISSUES")
        output.append("-" * 70)
        for issue in report.skill_issues:
            icon = "[ERROR]" if issue["severity"] == "error" else "[WARN]"
            output.append(f"  {icon} {issue['check']}")
            output.append(f"         {issue['message']}")
        output.append("")

    if report.terminology_candidates:
        output.append("TERMINOLOGY CANDIDATES FOR REVIEW")
        output.append("-" * 70)
        output.append("The following term pairs may need consistency review.")
        output.append("Confidence: 0.80+ HIGH (likely needs action), 0.50-0.79 MEDIUM, <0.50 LOW")
        output.append("")

        for i, candidate in enumerate(report.terminology_candidates, 1):
            suggestion = f" (suggested: {candidate['suggestion']})" if candidate.get('suggestion') else ""
            output.append(f"  {i}. \"{candidate['term1']}\" ({candidate['term1_count']}x) vs \"{candidate['term2']}\" ({candidate['term2_count']}x)")
            output.append(f"     Reason: {candidate['reason']}{suggestion}")

            # Show confidence scores
            base_conf = candidate.get('base_confidence', 0.0)
            adj_conf = candidate.get('adjusted_confidence', 0.0)
            modifiers = candidate.get('modifiers_applied', [])

            if adj_conf >= 0.80:
                conf_label = "HIGH"
            elif adj_conf >= 0.50:
                conf_label = "MEDIUM"
            else:
                conf_label = "LOW"

            output.append(f"     Confidence: {adj_conf:.2f} ({conf_label})")
            if modifiers:
                modifier_delta = adj_conf - base_conf
                sign = "+" if modifier_delta >= 0 else ""
                output.append(f"       Base: {base_conf:.2f}, Adjusted: {sign}{modifier_delta:.2f} from: {', '.join(modifiers)}")

            # Show occurrences
            if candidate.get('term1_occurrences'):
                output.append(f"     \"{candidate['term1']}\" appears in:")
                for occ in candidate['term1_occurrences'][:2]:
                    output.append(f"       - Line {occ['line_number']} ({occ['section']}): {occ['sentence'][:50]}...")

            if candidate.get('term2_occurrences'):
                output.append(f"     \"{candidate['term2']}\" appears in:")
                for occ in candidate['term2_occurrences'][:2]:
                    output.append(f"       - Line {occ['line_number']} ({occ['section']}): {occ['sentence'][:50]}...")

            output.append("")

        # Decision guidance
        output.append("DECISION GUIDANCE")
        output.append("-" * 70)
        for reason, info in report.terminology_guidance.items():
            output.append(f"  {reason}:")
            output.append(f"    {info.get('description', '')}")
            output.append(f"    Action: {info.get('typical_action', '')}")
            output.append(f"    Exceptions: {info.get('exceptions', '')}")
            output.append("")

    # Final verdict
    output.append("=" * 70)
    output.append(f"FINAL VERDICT: {overall_status}")
    if not report.overall_passed:
        output.append("Fix all errors before proceeding.")
    if report.terminology_candidates:
        output.append(f"Review {len(report.terminology_candidates)} terminology candidates for consistency.")
    output.append("=" * 70)

    return "\n".join(output)


def validate_all(skill_path: Path, config_path: Optional[Path] = None) -> UnifiedReport:
    """Run all validators and produce a unified report."""
    report = UnifiedReport(
        skill_path=str(skill_path),
        overall_passed=True,
        metadata={
            "orchestrator": "validate_all.py",
            "version": ORCHESTRATOR_VERSION,
            "validators": ["validate_syntax.py", "validate_skill.py", "check_terminology.py"]
        }
    )

    # Run syntax validation
    syntax_summary, syntax_issues = run_syntax_validation(skill_path)
    report.summaries.append(syntax_summary)
    report.syntax_issues = syntax_issues
    if not syntax_summary.passed:
        report.overall_passed = False

    # Run skill structure validation
    skill_summary, skill_issues = run_skill_validation(skill_path)
    report.summaries.append(skill_summary)
    report.skill_issues = skill_issues
    if not skill_summary.passed:
        report.overall_passed = False

    # Run terminology checks
    term_summary, term_candidates, term_guidance = run_terminology_check(skill_path, config_path)
    report.summaries.append(term_summary)
    report.terminology_candidates = term_candidates
    report.terminology_guidance = term_guidance
    # Terminology doesn't fail the overall check - candidates are for review

    return report


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    skill_path = Path(sys.argv[1])

    if not skill_path.exists():
        print(f"Error: Path not found: {skill_path}")
        sys.exit(1)

    # Check for --config flag
    config_path = None
    if "--config" in sys.argv:
        config_idx = sys.argv.index("--config")
        if config_idx + 1 < len(sys.argv):
            config_path = Path(sys.argv[config_idx + 1])

    # Run all validations
    report = validate_all(skill_path, config_path)

    # Output format
    if "--json" in sys.argv:
        # Convert to JSON-serializable dict
        output = {
            "skill_path": report.skill_path,
            "overall_passed": report.overall_passed,
            "summaries": [asdict(s) for s in report.summaries],
            "syntax_issues": report.syntax_issues,
            "skill_issues": report.skill_issues,
            "terminology_candidates": report.terminology_candidates,
            "terminology_guidance": report.terminology_guidance,
            "metadata": report.metadata
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human_readable(report))

    # Exit with appropriate code
    sys.exit(0 if report.overall_passed else 1)


if __name__ == "__main__":
    main()
