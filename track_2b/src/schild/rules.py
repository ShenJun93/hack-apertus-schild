import re

from .spans import Span


def ahv_valid(number: str) -> bool:
    """Swiss social security number: 13 digits, prefix 756, EAN-13 check digit."""
    digits = re.sub(r"\D", "", number)
    if len(digits) != 13 or not digits.startswith("756"):
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
    return (10 - total % 10) % 10 == int(digits[12])


def iban_valid(iban: str) -> bool:
    """Swiss IBAN: CH + 2 check digits + 17 alphanumerics, ISO 13616 mod-97."""
    compact = re.sub(r"\s", "", iban).upper()
    if not re.fullmatch(r"CH\d{2}[0-9A-Z]{17}", compact):
        return False
    rearranged = compact[4:] + compact[:4]
    return int("".join(str(int(c, 36)) for c in rearranged)) % 97 == 1


_AHV = re.compile(r"(?<!\d)756[.\s]?\d{4}[.\s]?\d{4}[.\s]?\d{2}(?!\d)")
_IBAN = re.compile(r"(?<![0-9A-Za-z])CH\d{2}(?:\s?[0-9A-Za-z]){17}(?![0-9A-Za-z])", re.IGNORECASE)
_PHONE = re.compile(r"(?<![\d+])(?:(?:\+|00)41[\s.-]?(?:\(0\)[\s.-]?)?|0)[1-9]\d(?:[\s.-]?\d){7}(?!\d)")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

_MONTHS = (
    "januar|februar|märz|maerz|april|mai|juni|juli|august|september|oktober|november|dezember|"
    "janvier|février|fevrier|mars|avril|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre|"
    "gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|dicembre|"
    "january|february|march|may|june|july|october|december"
)
_DATE = rf"(?:\d{{1,2}}[./-]\d{{1,2}}[./-]\d{{4}}|\d{{1,2}}\.?\s(?:{_MONTHS})\s\d{{4}})"
_DOB_KEY = (
    r"(?:geboren(?:\s+am)?|geb\.|geburtsdatum|n[ée]e?(?:\(e\))?\s+le|date\s+de\s+naissance|"
    r"nat[oa](?:/a)?\s+il|data\s+di\s+nascita|born(?:\s+on)?|date\s+of\s+birth|dob)"
)
_DOB = re.compile(rf"{_DOB_KEY}[\s:,]*({_DATE})", re.IGNORECASE)


def detect_rules(text: str) -> list[Span]:
    spans: list[Span] = []
    for m in _AHV.finditer(text):
        if ahv_valid(m.group(0)):
            spans.append(Span(m.start(), m.end(), "AHV", m.group(0), "rules"))
    for m in _IBAN.finditer(text):
        if iban_valid(m.group(0)):
            spans.append(Span(m.start(), m.end(), "IBAN", m.group(0), "rules"))
    for m in _PHONE.finditer(text):
        spans.append(Span(m.start(), m.end(), "PHONE", m.group(0), "rules"))
    for m in _EMAIL.finditer(text):
        spans.append(Span(m.start(), m.end(), "EMAIL", m.group(0), "rules"))
    for m in _DOB.finditer(text):
        spans.append(Span(m.start(1), m.end(1), "DOB", m.group(1), "rules"))
    return sorted(spans, key=lambda s: s.start)
