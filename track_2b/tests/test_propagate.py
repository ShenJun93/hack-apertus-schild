from fakes import FakeLlm

from schild.pipeline import redact_text
from schild.propagate import propagate
from schild.spans import Span
from schild.vault import Session


def test_case_and_spacing_variants_are_redacted():
    text = "Anna Keller kam heute. Später rief ANNA KELLER an. anna  keller ist krank."
    result = redact_text(text, Session("s"), FakeLlm([("Anna Keller", "PERSON")]))
    assert result.redacted_text == "[PERSON_1] kam heute. Später rief [PERSON_1] an. [PERSON_1] ist krank."


def test_values_known_to_the_session_are_redacted_in_later_texts():
    session = Session("s")
    redact_text("Patientin Anna Keller.", session, FakeLlm([("Anna Keller", "PERSON")]))
    later = redact_text("Was weisst du über Anna Keller?", session, FakeLlm())
    assert later.redacted_text == "Was weisst du über [PERSON_1]?"


def test_propagation_respects_word_boundaries():
    result = redact_text("Lea kommt. Leasing ist teuer. LEA bleibt.", Session("s"), FakeLlm([("Lea", "PERSON")]))
    assert result.redacted_text == "[PERSON_1] kommt. Leasing ist teuer. [PERSON_1] bleibt."


def test_propagate_adds_spans_with_the_known_type():
    text = "x ANNA KELLER y"
    spans = propagate(text, [], [("PERSON", "Anna Keller")])
    assert [(s.start, s.end, s.type, s.text) for s in spans] == [(2, 13, "PERSON", "ANNA KELLER")]


def test_one_character_values_are_not_propagated():
    assert propagate("a b a", [Span(0, 1, "PERSON", "a", "apertus")], []) == [Span(0, 1, "PERSON", "a", "apertus")]
