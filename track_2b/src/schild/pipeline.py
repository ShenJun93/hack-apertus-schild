from dataclasses import dataclass

from .llm_detector import DetectorUnavailable
from .merge import merge_spans
from .rules import detect_rules
from .vault import Session, apply


@dataclass
class RedactionResult:
    session_id: str
    redacted_text: str
    entities: list[dict]
    degraded: bool
    hallucinated: int


def redact_text(text: str, session: Session, llm) -> RedactionResult:
    spans = detect_rules(text)
    degraded = llm is None
    hallucinated = 0
    if llm is not None:
        try:
            result = llm.detect(text)
            spans += result.spans
            hallucinated = result.hallucinated
        except DetectorUnavailable:
            degraded = True
    redacted, entities = apply(text, merge_spans(spans, text), session)
    return RedactionResult(session.id, redacted, entities, degraded, hallucinated)
