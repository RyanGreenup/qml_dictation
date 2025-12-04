"""Fuzzy string matching module inspired by fzf/fzy algorithms.

This module provides high-performance fuzzy matching optimized for
path-like strings. It uses subsequence matching with scoring based on:
- Consecutive character matches
- Word boundary matches (after /, _, -, ., space, camelCase)
- Position bonuses (matches at start)
- Gap penalties (skipped characters)
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

# Scoring constants (tuned for path matching)
SCORE_CONSECUTIVE = 16
SCORE_WORD_BOUNDARY = 32
SCORE_FIRST_CHAR = 16
SCORE_GAP_PENALTY = -3

# Characters that define word boundaries in paths
WORD_BOUNDARY_CHARS = frozenset("/_-. ")


@dataclass(frozen=True, slots=True)
class FuzzyMatch:
    """Result of fuzzy matching with score and match positions."""

    score: int
    positions: tuple[int, ...]


def _is_word_boundary(target: str, index: int) -> bool:
    """Check if position is at a word boundary."""
    if index == 0:
        return True
    prev_char = target[index - 1]
    if prev_char in WORD_BOUNDARY_CHARS:
        return True
    # CamelCase: lowercase followed by uppercase
    curr_char = target[index]
    if prev_char.islower() and curr_char.isupper():
        return True
    return False


def fuzzy_match(query: str, target: str) -> FuzzyMatch | None:
    """
    Perform fzf-style fuzzy matching.

    Returns None if query doesn't match target as a subsequence.
    Otherwise returns FuzzyMatch with score and matched positions.

    The algorithm finds the best scoring alignment of query characters
    within target, preferring:
    - Consecutive matches
    - Matches at word boundaries
    - Earlier matches
    """
    if not query:
        return FuzzyMatch(score=0, positions=())

    query_lower = query.lower()
    target_lower = target.lower()
    query_len = len(query)
    target_len = len(target)

    # Quick check: query can't be longer than target
    if query_len > target_len:
        return None

    # Find all possible positions for each query character
    # This enables finding the optimal alignment
    positions: list[int] = []
    score = 0
    target_idx = 0
    prev_match_idx = -1

    for query_idx, query_char in enumerate(query_lower):
        # Find next occurrence of query_char in target
        found = False
        while target_idx < target_len:
            if target_lower[target_idx] == query_char:
                positions.append(target_idx)

                # Score this match
                if query_idx == 0 and target_idx == 0:
                    score += SCORE_FIRST_CHAR

                if _is_word_boundary(target, target_idx):
                    score += SCORE_WORD_BOUNDARY

                if prev_match_idx >= 0:
                    gap = target_idx - prev_match_idx - 1
                    if gap == 0:
                        score += SCORE_CONSECUTIVE
                    else:
                        score += gap * SCORE_GAP_PENALTY

                prev_match_idx = target_idx
                target_idx += 1
                found = True
                break
            target_idx += 1

        if not found:
            return None

    return FuzzyMatch(score=score, positions=tuple(positions))


def fuzzy_score(query: str, target: str) -> int | None:
    """
    Simplified fuzzy matching returning only the score.

    Slightly faster than fuzzy_match() when positions aren't needed.
    Returns None if no match, otherwise the match score.
    """
    if not query:
        return 0

    query_lower = query.lower()
    target_lower = target.lower()
    query_len = len(query)
    target_len = len(target)

    if query_len > target_len:
        return None

    score = 0
    target_idx = 0
    prev_match_idx = -1

    for query_idx, query_char in enumerate(query_lower):
        found = False
        while target_idx < target_len:
            if target_lower[target_idx] == query_char:
                if query_idx == 0 and target_idx == 0:
                    score += SCORE_FIRST_CHAR

                if _is_word_boundary(target, target_idx):
                    score += SCORE_WORD_BOUNDARY

                if prev_match_idx >= 0:
                    gap = target_idx - prev_match_idx - 1
                    if gap == 0:
                        score += SCORE_CONSECUTIVE
                    else:
                        score += gap * SCORE_GAP_PENALTY

                prev_match_idx = target_idx
                target_idx += 1
                found = True
                break
            target_idx += 1

        if not found:
            return None

    return score


def rank_matches[T](
    query: str,
    items: Sequence[T],
    key: Callable[[T], str],
    limit: int = 50,
) -> list[tuple[T, int]]:
    """
    Rank items by fuzzy match score.

    Args:
        query: The search query string
        items: Sequence of items to search
        key: Function to extract the string to match against from each item
        limit: Maximum number of results to return

    Returns:
        List of (item, score) tuples, sorted by score descending.
        Only includes items that match the query.
    """
    if not query:
        # Return first `limit` items with score 0 if no query
        return [(item, 0) for item in items[:limit]]

    scored: list[tuple[T, int]] = []

    for item in items:
        target = key(item)
        score = fuzzy_score(query, target)
        if score is not None:
            scored.append((item, score))

    # Sort by score descending, then by key alphabetically for ties
    scored.sort(key=lambda x: (-x[1], key(x[0])))

    return scored[:limit]


def build_sql_pattern(query: str) -> str:
    """
    Build a SQL LIKE pattern for pre-filtering candidates.

    Converts query "abc" to "%a%b%c%" to ensure the subsequence
    exists in the database before applying full fuzzy scoring.
    """
    if not query:
        return "%"
    # Escape SQL LIKE special characters
    escaped = query.replace("%", r"\%").replace("_", r"\_")
    # Build pattern with wildcards between each character
    return "%" + "%".join(escaped.lower()) + "%"
