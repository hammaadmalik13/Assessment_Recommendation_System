from __future__ import annotations

import re


OFF_TOPIC_HINTS = {
    "salary",
    "labor law",
    "legal advice",
    "immigration",
    "resume tips",
    "cv writing",
    "interview questions",
    "tax",
}

INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"reveal\s+system\s+prompt",
    r"jailbreak",
    r"bypass\s+rules",
]


def is_prompt_injection(text: str) -> bool:
    normalized = text.lower()
    return any(re.search(pattern, normalized) for pattern in INJECTION_PATTERNS)


def is_off_topic_request(text: str) -> bool:
    normalized = text.lower()
    return any(hint in normalized for hint in OFF_TOPIC_HINTS)

