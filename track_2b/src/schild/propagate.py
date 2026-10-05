import re

from .spans import Span


def _pattern(value: str) -> re.Pattern | None:
    tokens = value.split()
    if len("".join(tokens)) < 2:
        return None
    body = r"\s+".join(re.escape(token) for token in tokens)
    return re.compile(rf"(?<!\w){body}(?!\w)", re.IGNORECASE)


def propagate(text: str, spans: list[Span], known: list[tuple[str, str]]) -> list[Span]:
    """Add a span for every other occurrence of a value already found or already in the session.

    The model and the rules may report a value only once, or only in one spelling. Once a value is
    known to be personal data, every occurrence is redacted, whatever its case or spacing.
    """
    values = [(s.type, s.text) for s in spans] + list(known)
    found = list(spans)
    seen = {(s.start, s.end) for s in spans}
    for type_, value in values:
        pattern = _pattern(value)
        if pattern is None:
            continue
        for m in pattern.finditer(text):
            if (m.start(), m.end()) not in seen:
                seen.add((m.start(), m.end()))
                found.append(Span(m.start(), m.end(), type_, m.group(0), "propagated"))
    return found
