#!/usr/bin/env python3
"""
Terminology Consistency Checker for Claude Code skills.

Extracts unique terms, finds similar candidates using deterministic heuristics,
and outputs pairs for LLM review. This hybrid approach combines:
1. Deterministic: Term extraction, counting, similarity detection
2. LLM judgment: Deciding whether similar terms should be unified

Usage:
    python check_terminology.py <skill_path>
    python check_terminology.py ./my-skill/SKILL.md
    python check_terminology.py ./my-skill/  # Checks all .md files
    python check_terminology.py ./my-skill/ --config ./custom_config.yaml

Output:
    JSON structure with candidate pairs for LLM to evaluate.
"""

import re
import sys
import json
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, asdict, field
from typing import Optional

# Try to import yaml, fall back gracefully
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Validator metadata
VALIDATOR_VERSION = "2.0.0"
CHECKS_PERFORMED = [
    "case_variation",
    "abbreviation",
    "stem_variation",
    "hyphenation_variant",
    "compound_variant",
    "levenshtein_distance"
]


# Common English stopwords to ignore
STOPWORDS = {
    # Articles and conjunctions
    'a', 'an', 'the', 'and', 'or', 'but', 'nor', 'yet', 'so',
    # Prepositions
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as',
    'into', 'onto', 'upon', 'out', 'up', 'down', 'about', 'over',
    'after', 'before', 'between', 'under', 'above', 'below', 'against',
    'through', 'during', 'within', 'without', 'along', 'across', 'behind',
    'beyond', 'toward', 'towards', 'among', 'around', 'beside', 'besides',
    # Verbs (common)
    'is', 'was', 'are', 'were', 'been', 'be', 'being', 'am',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'done',
    'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
    'can', 'need', 'get', 'got', 'getting', 'make', 'made', 'making',
    'let', 'keep', 'put', 'set', 'take', 'took', 'give', 'gave',
    # Pronouns
    'it', 'its', 'they', 'them', 'their', 'theirs', 'themselves',
    'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
    'he', 'she', 'him', 'her', 'his', 'hers', 'himself', 'herself',
    'i', 'me', 'my', 'mine', 'myself',
    # Demonstratives and determiners
    'this', 'that', 'these', 'those', 'all', 'any', 'each', 'every',
    'both', 'few', 'more', 'most', 'other', 'some', 'such', 'many',
    'much', 'several', 'enough', 'either', 'neither', 'another',
    # Adverbs
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also',
    'now', 'here', 'there', 'again', 'further', 'once', 'always', 'never',
    'often', 'still', 'already', 'ever', 'even', 'quite', 'rather',
    'almost', 'perhaps', 'maybe', 'really', 'actually', 'simply',
    # Question words
    'not', 'no', 'yes', 'if', 'then', 'else', 'when', 'where', 'how',
    'what', 'which', 'who', 'whom', 'whose', 'why', 'whether',
    # Common verbs in documentation
    'see', 'use', 'using', 'used', 'uses', 'like', 'want', 'wanted',
    'work', 'works', 'working', 'run', 'runs', 'running', 'call', 'called',
    # Python keywords
    'true', 'false', 'null', 'none', 'return', 'def', 'class', 'import',
    'elif', 'try', 'except', 'finally', 'raise', 'pass', 'break',
    'continue', 'lambda', 'yield', 'assert', 'global', 'nonlocal',
    'async', 'await', 'del', 'print',
    # JavaScript/TypeScript keywords
    'const', 'var', 'function', 'new', 'typeof', 'instanceof',
    'undefined', 'void', 'interface', 'type', 'enum', 'export', 'default',
    'extends', 'implements', 'private', 'public', 'protected', 'static',
    'readonly', 'abstract', 'declare', 'module', 'namespace', 'require',
    # Go keywords
    'func', 'struct', 'package', 'main', 'defer', 'chan', 'select',
    'case', 'switch', 'fallthrough', 'goto', 'range', 'map', 'slice',
    # Rust keywords
    'mut', 'impl', 'trait', 'self', 'pub', 'mod', 'crate', 'super',
    'unsafe', 'extern', 'ref', 'match', 'loop', 'move', 'box', 'dyn',
    # Common type names
    'int', 'str', 'bool', 'float', 'string', 'number', 'boolean',
    'array', 'list', 'dict', 'object', 'any', 'void',
}

# Common technical abbreviations and their expansions (built-in defaults)
KNOWN_ABBREVIATIONS = {
    # File and directory
    'config': 'configuration',
    'configs': 'configurations',
    'dir': 'directory',
    'dirs': 'directories',
    'doc': 'document',
    'docs': 'documents',
    'src': 'source',
    'dest': 'destination',
    'tmp': 'temporary',
    'temp': 'temporary',
    'bin': 'binary',
    'lib': 'library',
    'libs': 'libraries',
    'pkg': 'package',
    'pkgs': 'packages',
    'mod': 'module',
    'mods': 'modules',
    # Code elements
    'func': 'function',
    'funcs': 'functions',
    'fn': 'function',
    'arg': 'argument',
    'args': 'arguments',
    'param': 'parameter',
    'params': 'parameters',
    'attr': 'attribute',
    'attrs': 'attributes',
    'prop': 'property',
    'props': 'properties',
    'var': 'variable',
    'vars': 'variables',
    'val': 'value',
    'vals': 'values',
    'obj': 'object',
    'objs': 'objects',
    'str': 'string',
    'num': 'number',
    'int': 'integer',
    'bool': 'boolean',
    'arr': 'array',
    'elem': 'element',
    'elems': 'elements',
    'idx': 'index',
    'len': 'length',
    'ptr': 'pointer',
    'ref': 'reference',
    'refs': 'references',
    # Operations
    'init': 'initialize',
    'exec': 'execute',
    'impl': 'implementation',
    'eval': 'evaluate',
    'calc': 'calculate',
    'gen': 'generate',
    'del': 'delete',
    'rm': 'remove',
    'mv': 'move',
    'cp': 'copy',
    'cmp': 'compare',
    'concat': 'concatenate',
    'iter': 'iterate',
    'alloc': 'allocate',
    'dealloc': 'deallocate',
    # Communication
    'msg': 'message',
    'msgs': 'messages',
    'req': 'request',
    'reqs': 'requests',
    'res': 'response',
    'resp': 'response',
    'err': 'error',
    'errs': 'errors',
    'warn': 'warning',
    'warns': 'warnings',
    'info': 'information',
    'desc': 'description',
    'cmd': 'command',
    'cmds': 'commands',
    # System and environment
    'env': 'environment',
    'envs': 'environments',
    'proc': 'process',
    'procs': 'processes',
    'sys': 'system',
    'mem': 'memory',
    'cpu': 'processor',
    'db': 'database',
    'conn': 'connection',
    'conns': 'connections',
    'sess': 'session',
    'auth': 'authentication',
    'authz': 'authorization',
    'perms': 'permissions',
    'creds': 'credentials',
    # Repositories and versioning
    'repo': 'repository',
    'repos': 'repositories',
    'ver': 'version',
    'rev': 'revision',
    'prev': 'previous',
    'curr': 'current',
    'orig': 'original',
    # Sizing and limits
    'max': 'maximum',
    'min': 'minimum',
    'avg': 'average',
    'cnt': 'count',
    'qty': 'quantity',
    'sz': 'size',
    # Organizations and structure
    'org': 'organization',
    'orgs': 'organizations',
    'opt': 'option',
    'opts': 'options',
    'pref': 'preference',
    'prefs': 'preferences',
    # Development terms
    'dev': 'development',
    'prod': 'production',
    'stg': 'staging',
    'qa': 'quality',
    'util': 'utility',
    'utils': 'utilities',
    'spec': 'specification',
    'specs': 'specifications',
    'impls': 'implementations',
    'perf': 'performance',
    'async': 'asynchronous',
    'sync': 'synchronous',
    # Networking
    'addr': 'address',
    'addrs': 'addresses',
    'url': 'uniform',
    'http': 'hypertext',
    'api': 'interface',
    'rpc': 'remote',
    # UI terms
    'btn': 'button',
    'btns': 'buttons',
    'nav': 'navigation',
    'img': 'image',
    'imgs': 'images',
    'txt': 'text',
    'lbl': 'label',
    'ctx': 'context',
}

# Decision guidance for each reason type
DECISION_GUIDANCE = {
    "case_variation": {
        "description": "Same word with different capitalization (e.g., 'Config' vs 'config').",
        "typical_action": "COMBINE to consistent casing.",
        "exceptions": "Acronyms (API, URL) or proper nouns may have intentional casing.",
    },
    "abbreviation": {
        "description": "A shortened form and its expansion (e.g., 'config' vs 'configuration').",
        "typical_action": "COMBINE to one form consistently.",
        "exceptions": "Technical contexts may prefer abbreviations; user-facing docs may prefer expanded forms.",
    },
    "stem_variation": {
        "description": "Different grammatical forms of the same root (e.g., 'validate' vs 'validation').",
        "typical_action": "Often KEEP - different forms serve grammatical purposes.",
        "exceptions": "If used interchangeably as nouns, consider unifying.",
    },
    "hyphenation_variant": {
        "description": "Same compound word with different hyphenation (e.g., 'sub-agent' vs 'subagent').",
        "typical_action": "COMBINE to consistent form.",
        "exceptions": "Some style guides prefer specific forms; check project conventions.",
    },
    "compound_variant": {
        "description": "Same concept as one word vs two words (e.g., 'filepath' vs 'file path').",
        "typical_action": "COMBINE to consistent form.",
        "exceptions": "Technical terms often have canonical forms; check documentation standards.",
    },
    "levenshtein_distance_1": {
        "description": "Terms differing by one character - likely a typo.",
        "typical_action": "COMBINE to correct spelling.",
        "exceptions": "May be intentionally different terms (e.g., 'test' vs 'text').",
    },
    "levenshtein_distance_2": {
        "description": "Terms differing by two characters - possible typo or variant.",
        "typical_action": "Review carefully - higher false positive rate.",
        "exceptions": "Often false positives; verify semantic similarity before combining.",
    },
}

# Confidence scores for each reason type (0.0 - 1.0)
# These represent the probability that a flagged pair is a TRUE inconsistency.
#
# =============================================================================
# CALIBRATION METHODOLOGY: Three-round expert council review
# =============================================================================
#
# Round 1 Experts: AI/ML Researcher, Statistician, Software Engineer,
#                  Computational Linguist, QA Engineer
#
# Round 2 Experts: Technical Writer, Search/IR Engineer, DevEx Engineer,
#                  Cognitive Scientist, Data Quality Specialist
#
# Round 3 Experts: UX Writer, Localization Engineer, Developer Advocate,
#                  Professional Copy Editor, Product Manager
#
# =============================================================================
# SCORE JUSTIFICATIONS
# =============================================================================
#
# case_variation: 0.68 (Initial: 0.90 -> R1: 0.75 -> R2: 0.70 -> R3: 0.68)
#   - Lowered due to legitimate variations: acronyms (API/api), proper nouns,
#     code vs prose context, headers vs body text
#   - DevEx/PM pushed for 0.60 (code-prose mixing is expected in API docs)
#   - Localization pushed for 0.77 (TM fragmentation concerns)
#   - 0.68 balances both concerns for general use
#
# abbreviation: 0.80 (Initial: 0.85 -> R1: 0.85 -> R2: 0.82 -> R3: 0.80)
#   - Dictionary collision concerns (DB, auth ambiguity)
#   - Localization strongly advocated for 0.90 (highest impact for TM/termbases)
#   - Copy Editor/DevAdv pushed for 0.76-0.78 (intentional register shifts)
#   - 0.80 is conservative middle ground; increase for localization workflows
#
# hyphenation_variant: 0.88 (Initial: 0.85 -> R1: 0.88 -> R2: 0.88 -> R3: 0.88)
#   - UNIVERSALLY VALIDATED across all 15 experts
#   - Called "hero feature" by PM - rarely intentional, always problematic
#   - Copy Editor suggested 0.90; keeping 0.88 as conservative
#   - Highest-confidence detection type after three rounds
#
# compound_variant: 0.76 (Initial: 0.80 -> R1: 0.80 -> R2: 0.80 -> R3: 0.76)
#   - Disputed: Cognitive scientist wanted 0.85 (word boundary disruption)
#   - DevEx/Copy Editor wanted 0.72-0.75 (verb/noun pairs like setup/set up)
#   - Localization wanted 0.85 (POS confusion degrades MT)
#   - 0.76 acknowledges legitimate grammatical variation while catching drift
#
# stem_variation: 0.40 (Initial: 0.50 -> R1: 0.40 -> R2: 0.40 -> R3: 0.40)
#   - VALIDATED across all rounds - grammatical usage is usually intentional
#   - validate/validation/validator are semantically distinct, not inconsistent
#   - Data Quality expert suggested 0.50 (concept consistency matters)
#   - Technical Writer suggested 0.35 (almost always intentional)
#   - 0.40 positions as "low confidence suggestion"
#
# levenshtein_distance_1: 0.48 (Initial: 0.70 -> R1: 0.60 -> R2: 0.55 -> R3: 0.48)
#   - Consistently lowered due to high false positive rate
#   - Common pairs: test/text, form/from, user/uses, path/patch, port/post
#   - DevAdv/PM recommend 0.45; IR Engineer suggested confusable-pairs blocklist
#   - 0.48 = "worth a glance" territory, not actionable without human review
#
# levenshtein_distance_2: 0.30 (Initial: 0.40 -> R1: 0.40 -> R2: 0.35 -> R3: 0.30)
#   - PM questioned whether to ship this at all in v1
#   - Copy Editor suggested 0.28; DevAdv suggested 0.25 or removal
#   - At distance 2, false positives dominate (server/service, handle/handler)
#   - 0.30 = "experimental/suggestion only" - consider hiding by default
#
# =============================================================================
# CONTEXT MODIFIERS (Recommended, not yet implemented)
# =============================================================================
#
# Multiple experts recommended adjusting scores based on context:
#   - Same paragraph: +0.10 (proximity increases confidence)
#   - Same section: +0.05
#   - 20+ paragraphs apart: -0.05 (distant terms may be intentional)
#   - Frequency imbalance > 10:1: +0.10 (rare term likely accidental)
#   - One term in code block: -0.15 (code identifiers differ from prose)
#   - One term in heading: -0.05 (headers use different style)
#   - Short term (< 5 chars) for Levenshtein: -0.10 (high false positive rate)
#   - First-mention expansion pattern: -0.20 (intentional, not inconsistent)
#
# =============================================================================
# DOMAIN-SPECIFIC ADJUSTMENTS
# =============================================================================
#
# For UI copy/microcopy: Increase case_variation to 0.85, abbreviation to 0.88
# For localization-bound content: Increase abbreviation to 0.90, compound to 0.85
# For API/developer docs: Decrease case_variation to 0.60, add code-context filter
#
# =============================================================================
# FUTURE CALIBRATION
# =============================================================================
#
# Track reviewer override rates and plot calibration curves after ~100 reviewed
# samples. Apply Platt scaling to recalibrate if predicted confidence diverges
# from observed accuracy.
#
CONFIDENCE_SCORES = {
    "case_variation": 0.68,
    "abbreviation": 0.80,
    "hyphenation_variant": 0.88,
    "compound_variant": 0.76,
    "stem_variation": 0.40,
    "levenshtein_distance_1": 0.48,
    "levenshtein_distance_2": 0.30,
}

# Context modifiers adjust confidence based on where/how terms appear
# These were recommended by 12/15 experts across three review rounds
#
# Usage: final_confidence = base_confidence + sum(applicable_modifiers)
# Clamped to [0.0, 1.0] range
CONTEXT_MODIFIERS = {
    # Proximity modifiers - closer terms are more likely true inconsistencies
    "same_paragraph": 0.10,       # Both terms appear in same paragraph
    "same_section": 0.05,         # Both terms appear under same heading
    "distant_sections": -0.05,   # Terms are 20+ paragraphs apart

    # Frequency modifiers - imbalanced usage suggests one is accidental
    "frequency_imbalance_high": 0.10,   # Ratio > 10:1 (e.g., 50 vs 3 occurrences)
    "frequency_imbalance_moderate": 0.05,  # Ratio > 5:1

    # Code context modifiers - code identifiers legitimately differ from prose
    "one_term_in_code": -0.15,    # One term appears in code block/backticks
    "both_terms_in_code": -0.05,  # Both in code - still worth flagging but lower confidence
    "one_term_in_heading": -0.05, # Headers often use different style than body

    # Term characteristics
    "short_term_levenshtein": -0.10,  # Terms < 5 chars have high false positive rate
    "first_mention_expansion": -0.20, # Pattern like "API (Application Programming Interface)"

    # Document structure
    "definition_context": -0.10,  # Term appears in glossary/definition section
}


def calculate_confidence_modifiers(
    term1: str,
    term2: str,
    term1_occurrences: list,
    term2_occurrences: list,
    reason: str
) -> tuple[float, list[str]]:
    """
    Calculate context-based confidence modifiers for a candidate pair.

    Returns:
        tuple of (total_modifier, list of applied modifier names)
    """
    modifiers_applied = []
    total_modifier = 0.0

    # Skip if no occurrence data
    if not term1_occurrences or not term2_occurrences:
        return 0.0, []

    # Get sections and line numbers
    t1_sections = {occ.get("section", "") for occ in term1_occurrences if isinstance(occ, dict)}
    t2_sections = {occ.get("section", "") for occ in term2_occurrences if isinstance(occ, dict)}
    t1_lines = [occ.get("line_number", 0) for occ in term1_occurrences if isinstance(occ, dict)]
    t2_lines = [occ.get("line_number", 0) for occ in term2_occurrences if isinstance(occ, dict)]

    # Proximity: same section check
    shared_sections = t1_sections & t2_sections
    if shared_sections - {"(no section)", ""}:
        modifiers_applied.append("same_section")
        total_modifier += CONTEXT_MODIFIERS["same_section"]

        # Check for same paragraph (lines within 5 of each other)
        for l1 in t1_lines:
            for l2 in t2_lines:
                if abs(l1 - l2) <= 5:
                    modifiers_applied.append("same_paragraph")
                    total_modifier += CONTEXT_MODIFIERS["same_paragraph"]
                    break
            else:
                continue
            break

    # Distant sections check
    if t1_lines and t2_lines:
        min_distance = min(abs(l1 - l2) for l1 in t1_lines for l2 in t2_lines)
        if min_distance > 100:  # More than ~100 lines apart
            modifiers_applied.append("distant_sections")
            total_modifier += CONTEXT_MODIFIERS["distant_sections"]

    # Frequency imbalance
    count1 = len(term1_occurrences)
    count2 = len(term2_occurrences)
    if count1 > 0 and count2 > 0:
        ratio = max(count1, count2) / min(count1, count2)
        if ratio > 10:
            modifiers_applied.append("frequency_imbalance_high")
            total_modifier += CONTEXT_MODIFIERS["frequency_imbalance_high"]
        elif ratio > 5:
            modifiers_applied.append("frequency_imbalance_moderate")
            total_modifier += CONTEXT_MODIFIERS["frequency_imbalance_moderate"]

    # Short term check for Levenshtein
    if "levenshtein" in reason:
        if len(term1) < 5 or len(term2) < 5:
            modifiers_applied.append("short_term_levenshtein")
            total_modifier += CONTEXT_MODIFIERS["short_term_levenshtein"]

    # Code context check (look for backticks or code indicators in sentence)
    t1_in_code = any(
        "`" in occ.get("sentence", "") or "```" in occ.get("sentence", "")
        for occ in term1_occurrences if isinstance(occ, dict)
    )
    t2_in_code = any(
        "`" in occ.get("sentence", "") or "```" in occ.get("sentence", "")
        for occ in term2_occurrences if isinstance(occ, dict)
    )

    if t1_in_code and t2_in_code:
        modifiers_applied.append("both_terms_in_code")
        total_modifier += CONTEXT_MODIFIERS["both_terms_in_code"]
    elif t1_in_code or t2_in_code:
        modifiers_applied.append("one_term_in_code")
        total_modifier += CONTEXT_MODIFIERS["one_term_in_code"]

    return total_modifier, modifiers_applied


def get_adjusted_confidence(reason: str, modifier: float = 0.0) -> float:
    """
    Get confidence score for a reason type, adjusted by context modifiers.
    Clamps result to [0.0, 1.0] range.
    """
    # Handle levenshtein variants
    base_reason = reason
    if reason.startswith("levenshtein_distance_"):
        if "1" in reason:
            base_reason = "levenshtein_distance_1"
        else:
            base_reason = "levenshtein_distance_2"

    base_confidence = CONFIDENCE_SCORES.get(base_reason, 0.50)
    adjusted = base_confidence + modifier

    # Clamp to valid range
    return max(0.0, min(1.0, adjusted))


@dataclass
class TermOccurrence:
    """A single occurrence of a term with context."""
    line_number: int
    sentence: str
    section: str


@dataclass
class TermInfo:
    """Information about a term's usage."""
    term: str
    count: int
    normalized: str
    occurrences: list[TermOccurrence] = field(default_factory=list)


@dataclass
class CandidatePair:
    """A pair of terms that might be inconsistent."""
    term1: str
    term1_count: int
    term2: str
    term2_count: int
    reason: str
    term1_occurrences: list[dict] = field(default_factory=list)
    term2_occurrences: list[dict] = field(default_factory=list)
    suggestion: Optional[str] = None
    base_confidence: float = 0.0
    adjusted_confidence: float = 0.0
    modifiers_applied: list[str] = field(default_factory=list)


@dataclass
class TerminologyConfig:
    """Configuration loaded from YAML file."""
    version: str = "1.0"
    domain_abbreviations: dict = field(default_factory=dict)
    compound_equivalents: list = field(default_factory=list)
    ignore_terms: list = field(default_factory=list)
    severity_overrides: dict = field(default_factory=dict)


def load_config(config_path: Optional[Path] = None) -> TerminologyConfig:
    """Load configuration from YAML file."""
    config = TerminologyConfig()

    if config_path is None:
        # Look for default config in same directory as script
        script_dir = Path(__file__).parent
        config_path = script_dir / "terminology_config.yaml"

    if not config_path.exists():
        return config

    if not HAS_YAML:
        print(f"Warning: PyYAML not installed. Cannot load config from {config_path}", file=sys.stderr)
        return config

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f)
            if data:
                config.version = data.get("version", "1.0")
                config.domain_abbreviations = data.get("domain_abbreviations", {})
                config.compound_equivalents = data.get("compound_equivalents", [])
                config.ignore_terms = [t.lower() for t in data.get("ignore_terms", [])]
                config.severity_overrides = data.get("severity_overrides", {})
    except Exception as e:
        print(f"Warning: Failed to load config: {e}", file=sys.stderr)

    return config


def simple_stem(word: str) -> str:
    """
    Conservative stemming - only handles obvious cases.
    Avoids aggressive transformations that cause false positives.
    """
    word = word.lower()

    # Only handle clear-cut suffixes
    if word.endswith('ing') and len(word) > 5:
        base = word[:-3]
        # Remove doubled consonant (e.g., "running" -> "runn" -> "run")
        if len(base) >= 2 and base[-1] == base[-2] and base[-1] not in 'aeiou':
            return base[:-1]
        return base
    if word.endswith('ied') and len(word) > 4:
        return word[:-3] + 'y'
    if word.endswith('ies') and len(word) > 4:
        return word[:-3] + 'y'
    if word.endswith('ed') and len(word) > 4:
        return word[:-2]
    if word.endswith('s') and len(word) > 3 and not word.endswith('ss'):
        return word[:-1]

    return word


def normalize_compound(term: str) -> str:
    """
    Normalize a term by removing hyphens and spaces.
    'sub-agent' -> 'subagent'
    'file path' -> 'filepath'
    """
    return term.lower().replace('-', '').replace(' ', '')


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein (edit) distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def get_current_section(lines: list[str], line_idx: int) -> str:
    """Find the most recent heading before the given line."""
    for i in range(line_idx - 1, -1, -1):
        line = lines[i].strip()
        if line.startswith('#'):
            # Extract heading text
            return re.sub(r'^#+\s*', '', line)
    return "(no section)"


def get_sentence_context(line: str, term: str, max_chars: int = 80) -> str:
    """Extract sentence context around a term occurrence."""
    # Find the term in the line (case-insensitive)
    match = re.search(re.escape(term), line, re.IGNORECASE)
    if not match:
        return line[:max_chars].strip()

    start = match.start()
    end = match.end()

    # Expand to include surrounding context
    context_start = max(0, start - 30)
    context_end = min(len(line), end + 30)

    context = line[context_start:context_end].strip()

    # Add ellipsis if truncated
    if context_start > 0:
        context = "..." + context
    if context_end < len(line):
        context = context + "..."

    return context


def extract_terms_with_context(content: str) -> tuple[Counter, dict[str, list[TermOccurrence]]]:
    """
    Extract meaningful terms from skill content with occurrence context.
    Returns term counts and a mapping of terms to their occurrences.
    """
    lines = content.split('\n')

    # Remove code blocks and track line mappings
    in_code_block = False
    processed_lines = []
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            processed_lines.append('')
            continue
        if in_code_block:
            processed_lines.append('')
        else:
            # Remove inline code
            cleaned = re.sub(r'`[^`]+`', '', line)
            # Remove URLs
            cleaned = re.sub(r'https?://\S+', '', cleaned)
            # Remove file paths
            cleaned = re.sub(r'[\w/]+\.\w+', '', cleaned)
            processed_lines.append(cleaned)

    term_counts = Counter()
    term_occurrences: dict[str, list[TermOccurrence]] = {}

    for line_idx, line in enumerate(processed_lines):
        if not line.strip():
            continue

        # Extract words
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]\b|\b[a-zA-Z]\b', line)

        for word in words:
            lower = word.lower()
            if lower not in STOPWORDS and len(lower) > 2:
                term_counts[word] += 1

                # Track occurrence
                if word not in term_occurrences:
                    term_occurrences[word] = []

                occurrence = TermOccurrence(
                    line_number=line_idx + 1,
                    sentence=get_sentence_context(lines[line_idx], word),
                    section=get_current_section(lines, line_idx)
                )
                term_occurrences[word].append(occurrence)

    return term_counts, term_occurrences


def extract_bigrams_with_context(content: str) -> tuple[Counter, dict[str, list[TermOccurrence]]]:
    """
    Extract word bigrams (consecutive pairs) with occurrence context.
    Used for detecting compound term variants.
    """
    lines = content.split('\n')

    in_code_block = False
    processed_lines = []
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            processed_lines.append('')
            continue
        if in_code_block:
            processed_lines.append('')
        else:
            cleaned = re.sub(r'`[^`]+`', '', line)
            cleaned = re.sub(r'https?://\S+', '', cleaned)
            cleaned = re.sub(r'[\w/]+\.\w+', '', cleaned)
            processed_lines.append(cleaned)

    bigram_counts = Counter()
    bigram_occurrences: dict[str, list[TermOccurrence]] = {}

    for line_idx, line in enumerate(processed_lines):
        if not line.strip():
            continue

        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', line)
        words = [w for w in words if w.lower() not in STOPWORDS and len(w) > 2]

        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            bigram_counts[bigram] += 1

            if bigram not in bigram_occurrences:
                bigram_occurrences[bigram] = []

            occurrence = TermOccurrence(
                line_number=line_idx + 1,
                sentence=get_sentence_context(lines[line_idx], bigram),
                section=get_current_section(lines, line_idx)
            )
            bigram_occurrences[bigram].append(occurrence)

    return bigram_counts, bigram_occurrences


def find_case_variations(
    term_counts: Counter,
    term_occurrences: dict[str, list[TermOccurrence]],
    ignore_terms: list[str]
) -> list[CandidatePair]:
    """Find terms that differ only in casing."""
    candidates = []

    by_lower: dict[str, list[tuple[str, int]]] = {}
    for term, count in term_counts.items():
        if term.lower() in ignore_terms:
            continue
        lower = term.lower()
        if lower not in by_lower:
            by_lower[lower] = []
        by_lower[lower].append((term, count))

    for lower, variants in by_lower.items():
        if len(variants) > 1:
            variants.sort(key=lambda x: x[1], reverse=True)
            most_common = variants[0][0]

            for term, count in variants[1:]:
                candidates.append(CandidatePair(
                    term1=most_common,
                    term1_count=variants[0][1],
                    term1_occurrences=[asdict(o) for o in term_occurrences.get(most_common, [])[:3]],
                    term2=term,
                    term2_count=count,
                    term2_occurrences=[asdict(o) for o in term_occurrences.get(term, [])[:3]],
                    reason="case_variation",
                    suggestion=most_common
                ))

    return candidates


def find_abbreviations(
    term_counts: Counter,
    term_occurrences: dict[str, list[TermOccurrence]],
    config: TerminologyConfig
) -> list[CandidatePair]:
    """Find abbreviation/expansion pairs."""
    candidates = []
    terms = {t.lower(): (t, c) for t, c in term_counts.items()}

    # Combine built-in and domain-specific abbreviations
    all_abbreviations = {**KNOWN_ABBREVIATIONS, **config.domain_abbreviations}

    for abbrev, expansion in all_abbreviations.items():
        abbrev_lower = abbrev.lower()
        expansion_lower = expansion.lower()

        if abbrev_lower in terms and expansion_lower in terms:
            abbrev_term, abbrev_count = terms[abbrev_lower]
            exp_term, exp_count = terms[expansion_lower]

            suggestion = abbrev_term if abbrev_count > exp_count else exp_term

            candidates.append(CandidatePair(
                term1=abbrev_term,
                term1_count=abbrev_count,
                term1_occurrences=[asdict(o) for o in term_occurrences.get(abbrev_term, [])[:3]],
                term2=exp_term,
                term2_count=exp_count,
                term2_occurrences=[asdict(o) for o in term_occurrences.get(exp_term, [])[:3]],
                reason="abbreviation",
                suggestion=suggestion
            ))

    return candidates


def find_stem_variations(
    term_counts: Counter,
    term_occurrences: dict[str, list[TermOccurrence]],
    ignore_terms: list[str]
) -> list[CandidatePair]:
    """Find terms with the same stem but different forms."""
    candidates = []

    by_stem: dict[str, list[tuple[str, int]]] = {}
    for term, count in term_counts.items():
        if term.lower() in ignore_terms:
            continue
        stem = simple_stem(term.lower())
        if len(stem) >= 3:
            if stem not in by_stem:
                by_stem[stem] = []
            by_stem[stem].append((term, count))

    for stem, variants in by_stem.items():
        if len(variants) > 1:
            variants.sort(key=lambda x: x[1], reverse=True)

            lowers = {v[0].lower() for v in variants}
            if len(lowers) == 2:
                l = list(lowers)
                if l[0] + 's' == l[1] or l[1] + 's' == l[0]:
                    continue

            most_common = variants[0][0]
            for term, count in variants[1:]:
                if term.lower() == most_common.lower() + 's':
                    continue
                if most_common.lower() == term.lower() + 's':
                    continue

                candidates.append(CandidatePair(
                    term1=most_common,
                    term1_count=variants[0][1],
                    term1_occurrences=[asdict(o) for o in term_occurrences.get(most_common, [])[:3]],
                    term2=term,
                    term2_count=count,
                    term2_occurrences=[asdict(o) for o in term_occurrences.get(term, [])[:3]],
                    reason="stem_variation",
                    suggestion=None
                ))

    return candidates


def find_hyphenation_variants(
    term_counts: Counter,
    term_occurrences: dict[str, list[TermOccurrence]],
    ignore_terms: list[str]
) -> list[CandidatePair]:
    """
    Find terms that differ only in hyphenation.
    E.g., 'sub-agent' vs 'subagent'
    """
    candidates = []

    # Group terms by normalized form (no hyphens)
    by_normalized: dict[str, list[tuple[str, int]]] = {}
    for term, count in term_counts.items():
        if term.lower() in ignore_terms:
            continue
        # Only consider terms that contain hyphens or could be hyphenated
        if '-' in term or len(term) > 6:
            normalized = normalize_compound(term)
            if normalized not in by_normalized:
                by_normalized[normalized] = []
            by_normalized[normalized].append((term, count))

    for normalized, variants in by_normalized.items():
        # Filter to only include terms that actually differ in hyphenation
        hyphenated = [(t, c) for t, c in variants if '-' in t]
        non_hyphenated = [(t, c) for t, c in variants if '-' not in t]

        if hyphenated and non_hyphenated:
            # We have both hyphenated and non-hyphenated forms
            all_variants = hyphenated + non_hyphenated
            all_variants.sort(key=lambda x: x[1], reverse=True)
            most_common = all_variants[0][0]

            for term, count in all_variants[1:]:
                # Skip if same term
                if term.lower() == most_common.lower():
                    continue

                candidates.append(CandidatePair(
                    term1=most_common,
                    term1_count=all_variants[0][1],
                    term1_occurrences=[asdict(o) for o in term_occurrences.get(most_common, [])[:3]],
                    term2=term,
                    term2_count=count,
                    term2_occurrences=[asdict(o) for o in term_occurrences.get(term, [])[:3]],
                    reason="hyphenation_variant",
                    suggestion=most_common
                ))

    return candidates


def find_compound_variants(
    term_counts: Counter,
    term_occurrences: dict[str, list[TermOccurrence]],
    bigram_counts: Counter,
    bigram_occurrences: dict[str, list[TermOccurrence]],
    config: TerminologyConfig
) -> list[CandidatePair]:
    """
    Find compound term variants: single words vs bigrams.
    E.g., 'filepath' vs 'file path'
    """
    candidates = []
    seen = set()

    # Check configured compound equivalents
    for equivalents in config.compound_equivalents:
        found_forms = []
        for form in equivalents:
            normalized = normalize_compound(form)
            # Check if this form exists in our terms
            if ' ' in form:
                # It's a bigram
                if form.lower() in {b.lower() for b in bigram_counts}:
                    for bigram in bigram_counts:
                        if bigram.lower() == form.lower():
                            found_forms.append((bigram, bigram_counts[bigram], "bigram"))
                            break
            else:
                # It's a single term
                if form.lower() in {t.lower() for t in term_counts}:
                    for term in term_counts:
                        if term.lower() == form.lower():
                            found_forms.append((term, term_counts[term], "term"))
                            break

        if len(found_forms) >= 2:
            found_forms.sort(key=lambda x: x[1], reverse=True)
            most_common = found_forms[0]

            for form, count, form_type in found_forms[1:]:
                pair_key = tuple(sorted([most_common[0].lower(), form.lower()]))
                if pair_key in seen:
                    continue
                seen.add(pair_key)

                # Get occurrences based on type
                if most_common[2] == "bigram":
                    occ1 = bigram_occurrences.get(most_common[0], [])
                else:
                    occ1 = term_occurrences.get(most_common[0], [])

                if form_type == "bigram":
                    occ2 = bigram_occurrences.get(form, [])
                else:
                    occ2 = term_occurrences.get(form, [])

                candidates.append(CandidatePair(
                    term1=most_common[0],
                    term1_count=most_common[1],
                    term1_occurrences=[asdict(o) for o in occ1[:3]],
                    term2=form,
                    term2_count=count,
                    term2_occurrences=[asdict(o) for o in occ2[:3]],
                    reason="compound_variant",
                    suggestion=most_common[0]
                ))

    # Also check for bigrams that match single compound words
    for bigram, bigram_count in bigram_counts.items():
        normalized = normalize_compound(bigram)
        if len(normalized) < 6:
            continue

        for term, term_count in term_counts.items():
            if normalize_compound(term) == normalized and term.lower() != bigram.lower().replace(' ', ''):
                pair_key = tuple(sorted([bigram.lower(), term.lower()]))
                if pair_key in seen:
                    continue

                # Verify they're actually compound variants (not coincidental)
                bigram_parts = bigram.lower().split()
                if len(bigram_parts) == 2 and bigram_parts[0] + bigram_parts[1] == term.lower():
                    seen.add(pair_key)

                    suggestion = bigram if bigram_count > term_count else term

                    candidates.append(CandidatePair(
                        term1=bigram,
                        term1_count=bigram_count,
                        term1_occurrences=[asdict(o) for o in bigram_occurrences.get(bigram, [])[:3]],
                        term2=term,
                        term2_count=term_count,
                        term2_occurrences=[asdict(o) for o in term_occurrences.get(term, [])[:3]],
                        reason="compound_variant",
                        suggestion=suggestion
                    ))

    return candidates


def find_levenshtein_similar(
    term_counts: Counter,
    term_occurrences: dict[str, list[TermOccurrence]],
    ignore_terms: list[str],
    max_distance: int = 2
) -> list[CandidatePair]:
    """Find terms within edit distance (typos, minor variations)."""
    candidates = []
    terms = list(term_counts.items())

    seen = set()
    for i, (term1, count1) in enumerate(terms):
        if term1.lower() in ignore_terms:
            continue
        for term2, count2 in terms[i+1:]:
            if term2.lower() in ignore_terms:
                continue
            if term1.lower() == term2.lower():
                continue
            if abs(len(term1) - len(term2)) > max_distance:
                continue
            if len(term1) < 4 or len(term2) < 4:
                continue

            distance = levenshtein_distance(term1.lower(), term2.lower())
            if 0 < distance <= max_distance:
                pair_key = tuple(sorted([term1.lower(), term2.lower()]))
                if pair_key not in seen:
                    seen.add(pair_key)
                    candidates.append(CandidatePair(
                        term1=term1,
                        term1_count=count1,
                        term1_occurrences=[asdict(o) for o in term_occurrences.get(term1, [])[:3]],
                        term2=term2,
                        term2_count=count2,
                        term2_occurrences=[asdict(o) for o in term_occurrences.get(term2, [])[:3]],
                        reason=f"levenshtein_distance_{distance}",
                        suggestion=None
                    ))

    return candidates


def check_terminology(skill_path: Path, config_path: Optional[Path] = None) -> dict:
    """
    Run terminology checks and return structured results for LLM review.
    """
    # Load configuration
    config = load_config(config_path)

    # Handle directory vs file path
    if skill_path.is_dir():
        md_files = list(skill_path.glob("*.md"))
    else:
        md_files = [skill_path]

    if not md_files:
        return {"error": f"No markdown files found at {skill_path}"}

    # Combine content from all files
    all_content = ""
    for f in md_files:
        all_content += f.read_text() + "\n"

    # Extract terms with context
    term_counts, term_occurrences = extract_terms_with_context(all_content)

    # Extract bigrams for compound detection
    bigram_counts, bigram_occurrences = extract_bigrams_with_context(all_content)

    # Find candidates using different heuristics
    all_candidates = []
    all_candidates.extend(find_case_variations(term_counts, term_occurrences, config.ignore_terms))
    all_candidates.extend(find_abbreviations(term_counts, term_occurrences, config))
    all_candidates.extend(find_stem_variations(term_counts, term_occurrences, config.ignore_terms))
    all_candidates.extend(find_hyphenation_variants(term_counts, term_occurrences, config.ignore_terms))
    all_candidates.extend(find_compound_variants(
        term_counts, term_occurrences,
        bigram_counts, bigram_occurrences,
        config
    ))
    all_candidates.extend(find_levenshtein_similar(term_counts, term_occurrences, config.ignore_terms))

    # Deduplicate
    seen = set()
    unique_candidates = []
    for c in all_candidates:
        pair_key = tuple(sorted([c.term1.lower(), c.term2.lower()]))
        if pair_key not in seen:
            seen.add(pair_key)
            unique_candidates.append(c)

    # Calculate confidence scores with context modifiers
    for candidate in unique_candidates:
        # Get base confidence for this reason type
        candidate.base_confidence = get_adjusted_confidence(candidate.reason, 0.0)

        # Calculate context modifiers
        modifier, modifiers_applied = calculate_confidence_modifiers(
            candidate.term1,
            candidate.term2,
            candidate.term1_occurrences,
            candidate.term2_occurrences,
            candidate.reason
        )

        candidate.adjusted_confidence = get_adjusted_confidence(candidate.reason, modifier)
        candidate.modifiers_applied = modifiers_applied

    # Sort by adjusted confidence (highest first), then by total count
    unique_candidates.sort(
        key=lambda c: (c.adjusted_confidence, c.term1_count + c.term2_count),
        reverse=True
    )

    # Build result with metadata
    result = {
        "metadata": {
            "validator": "check_terminology.py",
            "version": VALIDATOR_VERSION,
            "checks_performed": CHECKS_PERFORMED,
            "config_loaded": config_path.name if config_path and config_path.exists() else "terminology_config.yaml (default)",
            "thresholds": {
                "levenshtein_max_distance": 2,
                "min_term_length": 3,
                "min_stem_length": 3,
            }
        },
        "skill_path": str(skill_path),
        "files_checked": [str(f) for f in md_files],
        "total_unique_terms": len(term_counts),
        "total_bigrams_extracted": len(bigram_counts),
        "candidates_for_review": [asdict(c) for c in unique_candidates],
        "decision_guidance": DECISION_GUIDANCE,
        "term_counts": dict(term_counts.most_common(50)),
    }

    return result


def format_for_llm(result: dict) -> str:
    """Format results as a prompt for LLM review."""
    if "error" in result:
        return f"Error: {result['error']}"

    candidates = result.get("candidates_for_review", [])
    metadata = result.get("metadata", {})
    guidance = result.get("decision_guidance", {})

    output = []
    output.append("=" * 60)
    output.append("TERMINOLOGY CONSISTENCY CHECK")
    output.append("=" * 60)
    output.append("")

    # Metadata section
    output.append("VALIDATION METADATA")
    output.append("-" * 40)
    output.append(f"Validator: {metadata.get('validator', 'unknown')} v{metadata.get('version', '?')}")
    output.append(f"Config: {metadata.get('config_loaded', 'none')}")
    output.append(f"Checks: {', '.join(metadata.get('checks_performed', []))}")
    output.append(f"Files: {', '.join(result.get('files_checked', []))}")
    output.append(f"Total unique terms: {result.get('total_unique_terms', 0)}")
    output.append(f"Total bigrams: {result.get('total_bigrams_extracted', 0)}")
    output.append(f"Candidate pairs: {len(candidates)}")
    output.append("")

    # Decision guidance section
    output.append("DECISION GUIDANCE")
    output.append("-" * 40)
    for reason, info in guidance.items():
        output.append(f"  {reason}:")
        output.append(f"    {info.get('description', '')}")
        output.append(f"    Action: {info.get('typical_action', '')}")
        output.append(f"    Exception: {info.get('exceptions', '')}")
        output.append("")

    if not candidates:
        output.append("No terminology inconsistencies detected.")
        return "\n".join(output)

    # Candidates section
    output.append("CANDIDATES FOR REVIEW")
    output.append("-" * 40)
    output.append("For each pair, determine:")
    output.append("  - COMBINE [preferred term]: Should unify to one term")
    output.append("  - KEEP: Intentionally different meanings")
    output.append("")
    output.append("Confidence scores: Higher = more likely a true inconsistency")
    output.append("  0.80+ = High confidence - likely needs action")
    output.append("  0.50-0.79 = Medium confidence - review recommended")
    output.append("  < 0.50 = Low confidence - may be false positive")
    output.append("")

    for i, c in enumerate(candidates, 1):
        suggestion_hint = f" (suggested: {c.get('suggestion')})" if c.get('suggestion') else ""
        output.append(f"{i}. \"{c['term1']}\" ({c['term1_count']}x) vs \"{c['term2']}\" ({c['term2_count']}x)")
        output.append(f"   Reason: {c['reason']}{suggestion_hint}")

        # Show confidence scores
        base_conf = c.get('base_confidence', 0.0)
        adj_conf = c.get('adjusted_confidence', 0.0)
        modifiers = c.get('modifiers_applied', [])

        if adj_conf >= 0.80:
            conf_label = "HIGH"
        elif adj_conf >= 0.50:
            conf_label = "MEDIUM"
        else:
            conf_label = "LOW"

        output.append(f"   Confidence: {adj_conf:.2f} ({conf_label})")
        if modifiers:
            modifier_delta = adj_conf - base_conf
            sign = "+" if modifier_delta >= 0 else ""
            output.append(f"     Base: {base_conf:.2f}, Adjusted: {sign}{modifier_delta:.2f} from: {', '.join(modifiers)}")

        # Show occurrences for term1
        if c.get('term1_occurrences'):
            output.append(f"   \"{c['term1']}\" appears in:")
            for occ in c['term1_occurrences'][:2]:
                output.append(f"     - Line {occ['line_number']} ({occ['section']}): {occ['sentence']}")

        # Show occurrences for term2
        if c.get('term2_occurrences'):
            output.append(f"   \"{c['term2']}\" appears in:")
            for occ in c['term2_occurrences'][:2]:
                output.append(f"     - Line {occ['line_number']} ({occ['section']}): {occ['sentence']}")

        output.append("")

    return "\n".join(output)


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

    result = check_terminology(skill_path, config_path)

    # Check for --json flag
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(format_for_llm(result))


if __name__ == "__main__":
    main()
