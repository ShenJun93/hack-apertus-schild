from dataclasses import dataclass

RULE_TYPES = ("AHV", "IBAN", "PHONE", "EMAIL", "DOB")
LLM_TYPES = ("PERSON", "ADDRESS", "HEALTH", "RELIGION", "ETHNICITY", "CRIMINAL", "SOCIAL")
CHECKSUM_TYPES = frozenset({"AHV", "IBAN"})


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    type: str
    text: str
    source: str  # "rules", "apertus" or "both"
