"""Text processing utilities for sentiment analysis.

This module provides functions for cleaning, normalizing and processing
text data before sentiment analysis.
"""

import re
from typing import List, Optional

# Common regex patterns
URL_PATTERN = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\."
    r"[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
)
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
EMOJI_PATTERN = re.compile(
    r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]"
)


def clean_text(
    text: str,
    remove_urls: bool = True,
    remove_emails: bool = True,
    remove_emojis: bool = False,
) -> str:
    """Clean text by removing unwanted elements.

    Args:
        text: Input text to clean
        remove_urls: Whether to remove URLs
        remove_emails: Whether to remove email addresses
        remove_emojis: Whether to remove emoji characters

    Returns:
        Cleaned text
    """
    if remove_urls:
        text = URL_PATTERN.sub(" ", text)

    if remove_emails:
        text = EMAIL_PATTERN.sub(" ", text)

    if remove_emojis:
        text = EMOJI_PATTERN.sub(" ", text)

    # Remove extra whitespace
    text = " ".join(text.split())

    return text


def normalize_text(text: str) -> str:
    """Normalize text for consistent processing.

    Args:
        text: Input text to normalize

    Returns:
        Normalized text
    """
    # Convert to lowercase
    text = text.lower()

    # Replace multiple punctuation with single
    text = re.sub(r"([!?.]){2,}", r"\1", text)

    # Normalize whitespace
    text = " ".join(text.split())

    return text


def split_into_sentences(text: str, max_length: Optional[int] = None) -> List[str]:
    """Split text into sentences.

    Args:
        text: Input text to split
        max_length: Maximum length for each sentence

    Returns:
        List of sentences
    """
    # Basic sentence splitting on punctuation
    sentences = re.split(r"(?<=[.!?])\s+", text)

    if max_length is not None:
        # Further split long sentences
        result = []
        for sentence in sentences:
            if len(sentence) > max_length:
                # Split on commas or other natural breaks
                parts = re.split(r",\s+", sentence)
                result.extend(parts)
            else:
                result.append(sentence)
        return result

    return sentences
