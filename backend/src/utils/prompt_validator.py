import re

BLOCKED_PATTERNS = [
    r"ignore (previous|all) instructions",
    r"system\s*:",
    r"<script>",
    # Add more patterns as needed
]

def validate_prompt(prompt: str) -> str:
    """
    Validates the user's prompt to prevent prompt injection.

    Args:
        prompt: The user's prompt.

    Returns:
        The validated prompt.

    Raises:
        ValueError: If the prompt contains a blocked pattern.
    """
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            raise ValueError("Prompt contains a blocked pattern.")
    return prompt
