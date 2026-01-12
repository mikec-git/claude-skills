#!/usr/bin/env python3
"""
Unit tests for check_terminology.py

Tests cover:
- Term extraction from markdown content
- Simple stemming function
- Levenshtein distance calculation
- Case variation detection
- Abbreviation detection
- Stem variation detection
- Hyphenation variant detection
- Compound variant detection
- Edit distance similarity detection
- Full terminology checking pipeline
- LLM output formatting
"""

import pytest
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from check_terminology import (
    simple_stem,
    normalize_compound,
    levenshtein_distance,
    get_current_section,
    get_sentence_context,
    extract_terms_with_context,
    extract_bigrams_with_context,
    find_case_variations,
    find_abbreviations,
    find_stem_variations,
    find_hyphenation_variants,
    find_compound_variants,
    find_levenshtein_similar,
    check_terminology,
    format_for_llm,
    load_config,
    CandidatePair,
    TermInfo,
    TermOccurrence,
    TerminologyConfig,
    STOPWORDS,
    KNOWN_ABBREVIATIONS,
)
from collections import Counter


# =============================================================================
# simple_stem Tests
# =============================================================================

class TestSimpleStem:
    """Tests for the simple_stem function."""

    # Happy Path Tests

    def test_stem_ing_suffix_with_doubled_consonant(self):
        """Words ending in -ing with doubled consonant should reduce."""
        assert simple_stem("running") == "run"
        assert simple_stem("stopping") == "stop"
        assert simple_stem("getting") == "get"

    def test_stem_ing_suffix_without_doubled_consonant(self):
        """Words ending in -ing without doubled consonant should stem correctly."""
        assert simple_stem("testing") == "test"
        assert simple_stem("helping") == "help"
        assert simple_stem("walking") == "walk"
        assert simple_stem("jumping") == "jump"

    def test_stem_ed_suffix(self):
        """Words ending in -ed should reduce."""
        assert simple_stem("tested") == "test"
        assert simple_stem("validated") == "validat"

    def test_stem_ied_suffix(self):
        """Words ending in -ied should convert to -y."""
        assert simple_stem("modified") == "modify"
        assert simple_stem("applied") == "apply"

    def test_stem_ies_suffix(self):
        """Words ending in -ies should convert to -y."""
        assert simple_stem("queries") == "query"
        assert simple_stem("applies") == "apply"

    def test_stem_s_suffix(self):
        """Words ending in -s should reduce (except -ss)."""
        assert simple_stem("files") == "file"
        assert simple_stem("tests") == "test"

    def test_stem_ss_preserved(self):
        """Words ending in -ss should not reduce."""
        assert simple_stem("less") == "less"
        assert simple_stem("class") == "class"

    # Edge Cases

    def test_stem_short_words_unchanged(self):
        """Short words should remain unchanged."""
        assert simple_stem("run") == "run"
        assert simple_stem("go") == "go"
        assert simple_stem("a") == "a"

    def test_stem_lowercase_conversion(self):
        """Stemming should convert to lowercase."""
        assert simple_stem("Running") == "run"

    def test_stem_lowercase_conversion_ing_suffix(self):
        """Uppercase words ending in -ing should stem correctly."""
        assert simple_stem("TESTING") == "test"
        assert simple_stem("HELPING") == "help"
        assert simple_stem("Walking") == "walk"

    def test_stem_word_without_suffix(self):
        """Words without recognized suffixes should be lowercased only."""
        assert simple_stem("python") == "python"
        assert simple_stem("code") == "code"

    def test_stem_ring_not_truncated(self):
        """Short -ing words like 'ring' should not be over-truncated."""
        # 'ring' is only 4 chars, so len > 5 check should prevent bad stemming
        assert simple_stem("ring") == "ring"

    def test_stem_empty_string(self):
        """Empty string should return empty."""
        assert simple_stem("") == ""


# =============================================================================
# normalize_compound Tests
# =============================================================================

class TestNormalizeCompound:
    """Tests for the normalize_compound function."""

    def test_remove_hyphen(self):
        """Hyphens should be removed."""
        assert normalize_compound("sub-agent") == "subagent"
        assert normalize_compound("well-known") == "wellknown"

    def test_remove_space(self):
        """Spaces should be removed."""
        assert normalize_compound("file path") == "filepath"
        assert normalize_compound("error message") == "errormessage"

    def test_lowercase(self):
        """Result should be lowercase."""
        assert normalize_compound("SubAgent") == "subagent"
        assert normalize_compound("File Path") == "filepath"

    def test_no_changes_needed(self):
        """Single words without hyphens should just be lowercased."""
        assert normalize_compound("filename") == "filename"


# =============================================================================
# levenshtein_distance Tests
# =============================================================================

class TestLevenshteinDistance:
    """Tests for the levenshtein_distance function."""

    # Simple Cases

    def test_identical_strings(self):
        """Identical strings should have distance 0."""
        assert levenshtein_distance("hello", "hello") == 0

    def test_empty_strings(self):
        """Two empty strings should have distance 0."""
        assert levenshtein_distance("", "") == 0

    def test_one_empty_string(self):
        """Distance to empty string equals length of other string."""
        assert levenshtein_distance("hello", "") == 5
        assert levenshtein_distance("", "world") == 5

    def test_single_insertion(self):
        """Single insertion should have distance 1."""
        assert levenshtein_distance("cat", "cats") == 1
        assert levenshtein_distance("test", "tests") == 1

    def test_single_deletion(self):
        """Single deletion should have distance 1."""
        assert levenshtein_distance("cats", "cat") == 1

    def test_single_substitution(self):
        """Single substitution should have distance 1."""
        assert levenshtein_distance("cat", "bat") == 1
        assert levenshtein_distance("hello", "hallo") == 1

    # More Complex Cases

    def test_multiple_operations(self):
        """Multiple operations should sum correctly."""
        assert levenshtein_distance("kitten", "sitting") == 3
        assert levenshtein_distance("saturday", "sunday") == 3

    def test_completely_different(self):
        """Completely different strings of same length."""
        assert levenshtein_distance("abc", "xyz") == 3

    def test_symmetry(self):
        """Distance should be symmetric."""
        assert levenshtein_distance("abc", "def") == levenshtein_distance("def", "abc")
        assert levenshtein_distance("hello", "world") == levenshtein_distance("world", "hello")

    # Edge Cases

    def test_case_sensitive(self):
        """Distance calculation is case sensitive."""
        assert levenshtein_distance("Hello", "hello") == 1

    def test_single_character_strings(self):
        """Single character comparisons."""
        assert levenshtein_distance("a", "a") == 0
        assert levenshtein_distance("a", "b") == 1


# =============================================================================
# get_current_section Tests
# =============================================================================

class TestGetCurrentSection:
    """Tests for the get_current_section function."""

    def test_finds_heading(self):
        """Should find the most recent heading."""
        lines = ["# Main", "", "Content", "## Section", "More content"]
        assert get_current_section(lines, 4) == "Section"

    def test_no_heading(self):
        """Should return placeholder when no heading found."""
        lines = ["Content", "More content"]
        assert get_current_section(lines, 1) == "(no section)"

    def test_heading_at_start(self):
        """Should find heading at line 0."""
        lines = ["# Title", "Content"]
        assert get_current_section(lines, 1) == "Title"


# =============================================================================
# get_sentence_context Tests
# =============================================================================

class TestGetSentenceContext:
    """Tests for the get_sentence_context function."""

    def test_finds_term_context(self):
        """Should extract context around term."""
        line = "This is a test of the function"
        context = get_sentence_context(line, "test")
        assert "test" in context

    def test_truncates_long_context(self):
        """Should truncate very long lines."""
        line = "A" * 100 + " term " + "B" * 100
        context = get_sentence_context(line, "term", max_chars=80)
        assert len(context) < len(line)

    def test_handles_missing_term(self):
        """Should return beginning of line if term not found."""
        line = "This line has no match"
        context = get_sentence_context(line, "xyz")
        assert context.startswith("This")


# =============================================================================
# extract_terms_with_context Tests
# =============================================================================

class TestExtractTermsWithContext:
    """Tests for the extract_terms_with_context function."""

    # Happy Path Tests

    def test_extract_simple_terms(self):
        """Simple words should be extracted."""
        content = "This is a simple test document."
        term_counts, occurrences = extract_terms_with_context(content)
        assert "simple" in term_counts
        assert "test" in term_counts
        assert "document" in term_counts

    def test_stopwords_excluded(self):
        """Stopwords should be excluded from results."""
        content = "The quick brown fox jumps over the lazy dog."
        term_counts, _ = extract_terms_with_context(content)
        assert "the" not in term_counts
        assert "over" not in term_counts
        assert "quick" in term_counts
        assert "brown" in term_counts

    def test_short_words_excluded(self):
        """Words with 2 or fewer characters should be excluded."""
        content = "I am a fan of good code."
        term_counts, _ = extract_terms_with_context(content)
        assert "am" not in term_counts
        assert "fan" in term_counts
        assert "good" in term_counts
        assert "code" in term_counts

    def test_code_blocks_excluded(self):
        """Content in code blocks should be excluded."""
        content = """
Some text here.

```python
def variable_name():
    pass
```

More text here.
"""
        term_counts, _ = extract_terms_with_context(content)
        assert "variable_name" not in term_counts
        assert "def" not in term_counts
        assert "text" in term_counts

    def test_inline_code_excluded(self):
        """Inline code should be excluded."""
        content = "Use the `myFunction` method to process data."
        term_counts, _ = extract_terms_with_context(content)
        assert "myFunction" not in term_counts
        assert "method" in term_counts
        assert "process" in term_counts
        assert "data" in term_counts

    def test_urls_excluded(self):
        """URLs should be excluded."""
        content = "Visit https://example.com/page for more info."
        term_counts, _ = extract_terms_with_context(content)
        assert "https" not in term_counts
        assert "example" not in term_counts
        assert "Visit" in term_counts
        assert "info" in term_counts

    # Term Counting

    def test_term_counting(self):
        """Terms should be counted correctly."""
        content = "test test test code code"
        term_counts, _ = extract_terms_with_context(content)
        assert term_counts["test"] == 3
        assert term_counts["code"] == 2

    def test_returns_occurrences(self):
        """Should return occurrence information."""
        content = "# Section\n\nThis is a test."
        term_counts, occurrences = extract_terms_with_context(content)
        assert "test" in occurrences
        assert len(occurrences["test"]) > 0
        assert isinstance(occurrences["test"][0], TermOccurrence)

    # Edge Cases

    def test_hyphenated_words(self):
        """Hyphenated words should be extracted."""
        content = "Use the well-known pattern for real-time processing."
        term_counts, _ = extract_terms_with_context(content)
        assert "well-known" in term_counts
        assert "real-time" in term_counts

    def test_empty_content(self):
        """Empty content should return empty Counter."""
        term_counts, occurrences = extract_terms_with_context("")
        assert len(term_counts) == 0
        assert len(occurrences) == 0


# =============================================================================
# find_case_variations Tests
# =============================================================================

class TestFindCaseVariations:
    """Tests for the find_case_variations function."""

    def test_simple_case_variation(self):
        """Terms differing only in case should be detected."""
        term_counts = Counter({"Python": 3, "python": 2})
        occurrences = {"Python": [], "python": []}
        candidates = find_case_variations(term_counts, occurrences, [])

        assert len(candidates) == 1
        assert candidates[0].term1 == "Python"  # More common
        assert candidates[0].term2 == "python"
        assert candidates[0].reason == "case_variation"

    def test_multiple_case_variations(self):
        """Multiple case variants of same term."""
        term_counts = Counter({"PYTHON": 1, "Python": 3, "python": 2})
        occurrences = {"PYTHON": [], "Python": [], "python": []}
        candidates = find_case_variations(term_counts, occurrences, [])

        # Should find Python (most common) vs python and PYTHON
        assert len(candidates) == 2

    def test_no_case_variation(self):
        """No case variations should return empty list."""
        term_counts = Counter({"python": 3, "java": 2})
        occurrences = {"python": [], "java": []}
        candidates = find_case_variations(term_counts, occurrences, [])
        assert len(candidates) == 0

    def test_ignore_terms(self):
        """Ignored terms should not be reported."""
        term_counts = Counter({"Python": 3, "python": 2})
        occurrences = {"Python": [], "python": []}
        candidates = find_case_variations(term_counts, occurrences, ["python"])
        assert len(candidates) == 0


# =============================================================================
# find_abbreviations Tests
# =============================================================================

class TestFindAbbreviations:
    """Tests for the find_abbreviations function."""

    def test_known_abbreviation_pair(self):
        """Known abbreviation and expansion should be detected."""
        term_counts = Counter({"config": 5, "configuration": 3})
        occurrences = {"config": [], "configuration": []}
        config = TerminologyConfig()
        candidates = find_abbreviations(term_counts, occurrences, config)

        assert len(candidates) == 1
        assert candidates[0].reason == "abbreviation"
        assert {candidates[0].term1.lower(), candidates[0].term2.lower()} == {"config", "configuration"}

    def test_no_abbreviation_pair(self):
        """No abbreviation pairs should return empty list."""
        term_counts = Counter({"python": 3, "java": 2})
        occurrences = {"python": [], "java": []}
        config = TerminologyConfig()
        candidates = find_abbreviations(term_counts, occurrences, config)
        assert len(candidates) == 0

    def test_suggestion_prefers_more_common(self):
        """Suggestion should prefer the more common term."""
        term_counts = Counter({"config": 10, "configuration": 2})
        occurrences = {"config": [], "configuration": []}
        config = TerminologyConfig()
        candidates = find_abbreviations(term_counts, occurrences, config)

        assert len(candidates) == 1
        assert candidates[0].suggestion.lower() == "config"

    def test_domain_abbreviations_from_config(self):
        """Domain-specific abbreviations from config should be detected."""
        term_counts = Counter({"api": 3, "interface": 2})
        occurrences = {"api": [], "interface": []}
        config = TerminologyConfig()
        # Note: "api" -> "interface" is in KNOWN_ABBREVIATIONS
        candidates = find_abbreviations(term_counts, occurrences, config)
        assert len(candidates) == 1


# =============================================================================
# find_stem_variations Tests
# =============================================================================

class TestFindStemVariations:
    """Tests for the find_stem_variations function."""

    def test_plural_ignored(self):
        """Simple singular/plural pairs should be ignored."""
        term_counts = Counter({"file": 5, "files": 3})
        occurrences = {"file": [], "files": []}
        candidates = find_stem_variations(term_counts, occurrences, [])

        # Singular/plural should not be flagged
        assert len(candidates) == 0

    def test_no_stem_variation(self):
        """Unrelated terms should return empty list."""
        term_counts = Counter({"python": 3, "java": 2})
        occurrences = {"python": [], "java": []}
        candidates = find_stem_variations(term_counts, occurrences, [])
        assert len(candidates) == 0


# =============================================================================
# find_hyphenation_variants Tests
# =============================================================================

class TestFindHyphenationVariants:
    """Tests for the find_hyphenation_variants function."""

    def test_hyphen_vs_no_hyphen(self):
        """Should detect 'sub-agent' vs 'subagent'."""
        term_counts = Counter({"sub-agent": 3, "subagent": 2})
        occurrences = {"sub-agent": [], "subagent": []}
        candidates = find_hyphenation_variants(term_counts, occurrences, [])

        assert len(candidates) == 1
        assert candidates[0].reason == "hyphenation_variant"

    def test_no_hyphenation_variant(self):
        """No hyphenation variants should return empty list."""
        term_counts = Counter({"python": 3, "java": 2})
        occurrences = {"python": [], "java": []}
        candidates = find_hyphenation_variants(term_counts, occurrences, [])
        assert len(candidates) == 0


# =============================================================================
# find_levenshtein_similar Tests
# =============================================================================

class TestFindLevenshteinSimilar:
    """Tests for the find_levenshtein_similar function."""

    def test_single_char_difference(self):
        """Terms with single character difference should be detected."""
        term_counts = Counter({"test": 3, "text": 2})
        occurrences = {"test": [], "text": []}
        candidates = find_levenshtein_similar(term_counts, occurrences, [], max_distance=1)

        assert len(candidates) == 1
        assert "levenshtein" in candidates[0].reason

    def test_typo_detection(self):
        """Common typos should be detected."""
        term_counts = Counter({"function": 5, "funciton": 2})
        occurrences = {"function": [], "funciton": []}
        candidates = find_levenshtein_similar(term_counts, occurrences, [], max_distance=2)

        assert len(candidates) == 1

    def test_max_distance_respected(self):
        """Terms beyond max distance should not be detected."""
        term_counts = Counter({"hello": 3, "world": 2})
        occurrences = {"hello": [], "world": []}
        candidates = find_levenshtein_similar(term_counts, occurrences, [], max_distance=2)

        # hello and world have distance > 2
        assert len(candidates) == 0

    def test_short_terms_ignored(self):
        """Terms shorter than 4 characters should be ignored."""
        term_counts = Counter({"cat": 3, "bat": 2})
        occurrences = {"cat": [], "bat": []}
        candidates = find_levenshtein_similar(term_counts, occurrences, [], max_distance=1)

        # Both are 3 chars, should be ignored
        assert len(candidates) == 0

    def test_same_lowercase_ignored(self):
        """Terms that are same when lowercased should be ignored."""
        term_counts = Counter({"Test": 3, "test": 2})
        occurrences = {"Test": [], "test": []}
        candidates = find_levenshtein_similar(term_counts, occurrences, [], max_distance=1)

        # Case variations are handled by find_case_variations
        assert len(candidates) == 0


# =============================================================================
# check_terminology Integration Tests
# =============================================================================

class TestCheckTerminologyIntegration:
    """Integration tests for the check_terminology function."""

    def test_check_single_file(self):
        """Check terminology on a single markdown file."""
        content = """
# Test Document

This config and configuration should be flagged.
The Config variant should also be noted.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            try:
                result = check_terminology(Path(f.name))
                assert "error" not in result
                assert "candidates_for_review" in result
                assert result["total_unique_terms"] > 0
            finally:
                os.unlink(f.name)

    def test_check_directory(self):
        """Check terminology on a directory of markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple .md files
            (Path(tmpdir) / "file1.md").write_text("The config setting is important.")
            (Path(tmpdir) / "file2.md").write_text("Update the configuration here.")

            result = check_terminology(Path(tmpdir))
            assert len(result["files_checked"]) == 2

    def test_empty_directory(self):
        """Empty directory should return error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_terminology(Path(tmpdir))
            assert "error" in result

    def test_nonexistent_path(self):
        """Nonexistent path raises FileNotFoundError.

        Note: The function doesn't handle nonexistent files gracefully -
        it attempts to read the file and raises FileNotFoundError.
        """
        with pytest.raises(FileNotFoundError):
            check_terminology(Path("/nonexistent/path/file.md"))

    def test_top_terms_included(self):
        """Result should include top terms."""
        content = "Python Python Python Java Java code code code code code"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            try:
                result = check_terminology(Path(f.name))
                assert "term_counts" in result
                assert result["term_counts"]["code"] == 5
            finally:
                os.unlink(f.name)

    def test_metadata_included(self):
        """Result should include metadata."""
        content = "Some test content here."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            try:
                result = check_terminology(Path(f.name))
                assert "metadata" in result
                assert "version" in result["metadata"]
                assert "checks_performed" in result["metadata"]
            finally:
                os.unlink(f.name)


# =============================================================================
# format_for_llm Tests
# =============================================================================

class TestFormatForLLM:
    """Tests for the format_for_llm function."""

    def test_format_with_error(self):
        """Error result should format as error message."""
        result = {"error": "No markdown files found"}
        output = format_for_llm(result)
        assert "Error:" in output
        assert "No markdown files found" in output

    def test_format_no_candidates(self):
        """No candidates should indicate no inconsistencies."""
        result = {
            "candidates_for_review": [],
            "files_checked": ["test.md"],
            "total_unique_terms": 50,
            "total_bigrams_extracted": 30,
            "metadata": {"validator": "test", "version": "1.0", "checks_performed": [], "config_loaded": "none"},
            "decision_guidance": {}
        }
        output = format_for_llm(result)
        assert "No terminology inconsistencies" in output

    def test_format_with_candidates(self):
        """Candidates should be formatted for LLM review."""
        result = {
            "candidates_for_review": [
                {
                    "term1": "config",
                    "term1_count": 5,
                    "term2": "configuration",
                    "term2_count": 3,
                    "reason": "abbreviation",
                    "suggestion": "config",
                    "term1_occurrences": [],
                    "term2_occurrences": []
                }
            ],
            "files_checked": ["test.md"],
            "total_unique_terms": 50,
            "total_bigrams_extracted": 30,
            "metadata": {"validator": "test", "version": "1.0", "checks_performed": [], "config_loaded": "none"},
            "decision_guidance": {}
        }
        output = format_for_llm(result)
        assert "TERMINOLOGY CONSISTENCY CHECK" in output
        assert "config" in output
        assert "configuration" in output
        assert "abbreviation" in output
        assert "suggested: config" in output

    def test_format_includes_instructions(self):
        """Output should include instructions for LLM."""
        result = {
            "candidates_for_review": [
                {
                    "term1": "a",
                    "term1_count": 1,
                    "term2": "b",
                    "term2_count": 1,
                    "reason": "test",
                    "suggestion": None,
                    "term1_occurrences": [],
                    "term2_occurrences": []
                }
            ],
            "files_checked": ["test.md"],
            "total_unique_terms": 10,
            "total_bigrams_extracted": 5,
            "metadata": {"validator": "test", "version": "1.0", "checks_performed": [], "config_loaded": "none"},
            "decision_guidance": {}
        }
        output = format_for_llm(result)
        assert "COMBINE" in output
        assert "KEEP" in output


# =============================================================================
# load_config Tests
# =============================================================================

class TestLoadConfig:
    """Tests for the load_config function."""

    def test_default_config(self):
        """Should return default config when no file exists."""
        config = load_config(Path("/nonexistent/config.yaml"))
        assert isinstance(config, TerminologyConfig)
        assert config.version == "1.0"
        assert config.domain_abbreviations == {}

    def test_config_structure(self):
        """Config should have expected structure."""
        config = TerminologyConfig()
        assert hasattr(config, "version")
        assert hasattr(config, "domain_abbreviations")
        assert hasattr(config, "compound_equivalents")
        assert hasattr(config, "ignore_terms")
        assert hasattr(config, "severity_overrides")


# =============================================================================
# CandidatePair Tests
# =============================================================================

class TestCandidatePair:
    """Tests for the CandidatePair dataclass."""

    def test_create_candidate_pair(self):
        """CandidatePair should store all fields."""
        pair = CandidatePair(
            term1="config",
            term1_count=5,
            term2="configuration",
            term2_count=3,
            reason="abbreviation",
            suggestion="config"
        )
        assert pair.term1 == "config"
        assert pair.term1_count == 5
        assert pair.term2 == "configuration"
        assert pair.term2_count == 3
        assert pair.reason == "abbreviation"
        assert pair.suggestion == "config"

    def test_candidate_pair_no_suggestion(self):
        """CandidatePair can have no suggestion."""
        pair = CandidatePair(
            term1="test",
            term1_count=2,
            term2="text",
            term2_count=1,
            reason="levenshtein_distance_1"
        )
        assert pair.suggestion is None


# =============================================================================
# Constants Tests
# =============================================================================

class TestConstants:
    """Tests for constants."""

    def test_stopwords_not_empty(self):
        """STOPWORDS should contain common words."""
        assert len(STOPWORDS) > 0
        assert "the" in STOPWORDS
        assert "and" in STOPWORDS
        assert "is" in STOPWORDS

    def test_stopwords_lowercase(self):
        """STOPWORDS should all be lowercase."""
        assert all(word == word.lower() for word in STOPWORDS)

    def test_known_abbreviations_not_empty(self):
        """KNOWN_ABBREVIATIONS should have entries."""
        assert len(KNOWN_ABBREVIATIONS) > 0
        assert "config" in KNOWN_ABBREVIATIONS
        assert KNOWN_ABBREVIATIONS["config"] == "configuration"

    def test_known_abbreviations_lowercase(self):
        """KNOWN_ABBREVIATIONS keys should be lowercase."""
        assert all(key == key.lower() for key in KNOWN_ABBREVIATIONS)


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================

class TestEdgeCases:
    """Edge cases and boundary condition tests."""

    def test_unicode_content(self):
        """Unicode content should be handled."""
        content = "The cafe has excellent code."
        term_counts, _ = extract_terms_with_context(content)
        assert "cafe" in term_counts
        assert "excellent" in term_counts
        assert "code" in term_counts

    def test_mixed_content(self):
        """Content with mixed elements should be handled."""
        content = """
# Header

Regular text with `code` and [links](url).

```python
# code block
def foo():
    pass
```

More text.
"""
        term_counts, _ = extract_terms_with_context(content)
        assert "Header" in term_counts
        assert "Regular" in term_counts
        assert "text" in term_counts
        # Code and inline code should be excluded
        assert "foo" not in term_counts

    def test_large_term_counts(self):
        """Large term counts should be handled."""
        content = " ".join(["word"] * 10000)
        term_counts, _ = extract_terms_with_context(content)
        assert term_counts["word"] == 10000


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
