"""Prompt validation utilities to prevent prompt injection attacks."""

import re
import logging
from typing import Pattern

logger = logging.getLogger(__name__)

# Blocked patterns that indicate potential prompt injection attempts
BLOCKED_PATTERNS: list[Pattern[str]] = [
    re.compile(r"ignore\s+(previous|all|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(previous|all|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"forget\s+(previous|all|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*:", re.IGNORECASE),
    re.compile(r"<script>", re.IGNORECASE),
    re.compile(r"</script>", re.IGNORECASE),
    re.compile(r"<iframe>", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"onerror\s*=", re.IGNORECASE),
    re.compile(r"onload\s*=", re.IGNORECASE),
    re.compile(r"you\s+are\s+now", re.IGNORECASE),
    re.compile(r"new\s+role", re.IGNORECASE),
    re.compile(r"pretend\s+you\s+are", re.IGNORECASE),
    re.compile(r"act\s+as\s+if", re.IGNORECASE),
    re.compile(r"override\s+your", re.IGNORECASE),
]


def validate_prompt(prompt: str) -> str:
    """
    Validate a user prompt to prevent prompt injection attacks.
    
    Args:
        prompt: The user-provided prompt to validate
        
    Returns:
        The validated prompt (stripped of leading/trailing whitespace)
        
    Raises:
        ValueError: If the prompt contains blocked patterns
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    prompt_stripped = prompt.strip()
    
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(prompt_stripped):
            logger.warning(
                "Blocked potentially malicious prompt. Pattern: %s, Preview: %s",
                pattern.pattern,
                prompt_stripped[:100],
            )
            raise ValueError(
                f"Prompt contains potentially malicious pattern: {pattern.pattern}"
            )
    
    return prompt_stripped


def is_safe_prompt(prompt: str) -> bool:
    """
    Check if a prompt is safe without raising an exception.
    
    Args:
        prompt: The user-provided prompt to check
        
    Returns:
        True if the prompt is safe, False otherwise
    """
    try:
        validate_prompt(prompt)
        return True
    except ValueError:
        return False
