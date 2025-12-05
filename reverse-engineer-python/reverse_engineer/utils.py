"""
Utility functions for the reverse engineering tool.
"""

import sys
from pathlib import Path
from typing import Optional


def find_repo_root(start_dir: Path) -> Optional[Path]:
    """
    Find the repository root by looking for .git or .specify directories.

    Args:
        start_dir: Directory to start searching from

    Returns:
        Path to repository root or None if not found
    """
    current = start_dir.resolve()

    while current != current.parent:
        if (current / ".git").exists() or (current / ".specify").exists():
            return current
        current = current.parent

    return None


def log_info(message: str, verbose: bool = True):
    """
    Log an informational message if verbose mode is enabled.

    Args:
        message: Message to log
        verbose: Whether to actually print the message
    """
    if verbose:
        print(f"[INFO] {message}", file=sys.stderr)


def log_section(title: str):
    """
    Print a section header for better visual organization.

    Args:
        title: Section title
    """
    print("\n═══════════════════════════════════════════════════════════════════", file=sys.stderr)
    print(f"  {title}", file=sys.stderr)
    print("═══════════════════════════════════════════════════════════════════", file=sys.stderr)


def extract_intent_context(description: str) -> dict:
    """
    Extract action verbs and key nouns from project description.

    Args:
        description: Project description string

    Returns:
        Dictionary with 'verbs' and 'nouns' keys containing lists
    """
    if not description:
        return {"verbs": [], "nouns": []}

    desc_lower = description.lower()

    # Common action verbs in software contexts
    action_verbs = [
        "forecast",
        "predict",
        "estimate",
        "analyze",
        "calculate",
        "browse",
        "search",
        "filter",
        "manage",
        "track",
        "monitor",
        "coordinate",
        "schedule",
        "process",
        "deliver",
        "purchase",
        "order",
        "sell",
        "book",
        "reserve",
        "plan",
        "organize",
        "create",
        "update",
        "delete",
        "view",
        "list",
        "import",
        "export",
        "generate",
        "validate",
        "verify",
        "notify",
        "send",
        "publish",
        "subscribe",
        "authenticate",
        "authorize",
        "approve",
        "reject",
        "assign",
        "allocate",
        "measure",
        "assess",
        "evaluate",
        "compare",
        "recommend",
        "suggest",
        "optimize",
        "improve",
        "enhance",
        "report",
        "visualize",
        "display",
        "present",
        "share",
        "collaborate",
        "communicate",
        "integrate",
        "sync",
        "backup",
        "restore",
        "archive",
        "audit",
        "log",
        "alert",
        "remind",
    ]

    # Common words to filter out
    common_words = {
        "this",
        "that",
        "with",
        "from",
        "into",
        "about",
        "using",
        "based",
        "have",
        "been",
        "will",
        "should",
        "could",
        "would",
        "their",
        "there",
        "where",
        "which",
        "when",
        "then",
        "than",
        "them",
        "these",
        "those",
        "what",
        "some",
        "more",
        "most",
        "very",
        "only",
        "just",
        "also",
        "well",
        "even",
        "much",
        "such",
        "both",
        "each",
        "other",
        "another",
        "between",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "under",
    }

    # Extract matching verbs
    found_verbs = [verb for verb in action_verbs if verb in desc_lower.split()]

    # Extract key nouns (words 4+ chars that aren't common words or verbs)
    words = desc_lower.split()
    key_nouns = [
        word.strip(".,!?;:")
        for word in words
        if len(word) >= 4 and word not in common_words and word not in action_verbs
    ]

    return {"verbs": found_verbs, "nouns": key_nouns}


def format_model_name(name: str) -> str:
    """
    Format a model name for display (e.g., CamelCase to Title Case).

    Args:
        name: Model name in CamelCase

    Returns:
        Formatted name with spaces
    """
    import re

    # Insert space before capital letters
    return re.sub(r"([A-Z])", r" \1", name).strip()


def format_project_name(name: str) -> str:
    """
    Format a project name for display.

    Args:
        name: Project name (may contain dashes or underscores)

    Returns:
        Formatted name with proper capitalization
    """
    # Replace dashes and underscores with spaces
    formatted = name.replace("-", " ").replace("_", " ")
    # Capitalize each word
    return " ".join(word.capitalize() for word in formatted.split())
