import pytest

from schild.spans import Span
from schild.vault import Session, SessionStore, apply, restore


def spans_for(text, *pairs):
    out = []
    for value, type_ in pairs:
        start = 0
        while (i := text.find(value, start)) != -1:
            out.append(Span(i, i + len(value), type_, value, "apertus"))
            start = i + len(value)
    return sorted(out, key=lambda s: s.start)


def test_same_value_same_placeholder_case_and_spacing():
    s = Session("t")
    assert s.placeholder_for("PERSON", "Anna Keller") == "[PERSON_1]"
    assert s.placeholder_for("PERSON", "anna  keller") == "[PERSON_1]"
    assert s.placeholder_for("PERSON", "Marco Rossi") == "[PERSON_2]"
    assert s.placeholder_for("IBAN", "CH93 0076") == "[IBAN_1]"


def test_apply_and_restore_round_trip():
    text = "Anna Keller (Tel. 044 123 45 67) schrieb an Marco Rossi. Anna Keller wartet."
    spans = spans_for(text, ("Anna Keller", "PERSON"), ("Marco Rossi", "PERSON"), ("044 123 45 67", "PHONE"))
    session = Session("t")
    redacted, entities = apply(text, spans, session)
    assert redacted == "[PERSON_1] (Tel. [PHONE_1]) schrieb an [PERSON_2]. [PERSON_1] wartet."
    assert [e["placeholder"] for e in entities] == ["[PERSON_1]", "[PHONE_1]", "[PERSON_2]", "[PERSON_1]"]
    assert entities[0] == {"type": "PERSON", "placeholder": "[PERSON_1]", "start": 0, "end": 11, "source": "apertus"}
    assert restore(redacted, session) == text


def test_restore_tolerates_case_change():
    session = Session("t")
    session.placeholder_for("PERSON", "Anna Keller")
    assert restore("Dear [person_1],", session) == "Dear Anna Keller,"


def test_unknown_placeholders_are_left_alone():
    assert restore("see [PERSON_9]", Session("t")) == "see [PERSON_9]"


def test_placeholder_already_in_input_is_not_reused():
    text = "Template [PERSON_1] belongs to Anna Keller."
    session = Session("t")
    redacted, _ = apply(text, spans_for(text, ("Anna Keller", "PERSON")), session)
    assert redacted == "Template [PERSON_1] belongs to [PERSON_2]."
    assert restore(redacted, session) == text


def test_store_creates_reuses_and_evicts():
    store = SessionStore(max_sessions=2)
    a = store.get_or_create()
    assert store.get_or_create(a.id) is a
    b = store.get_or_create("b")
    store.get_or_create("c")
    assert store.get(a.id) is None and store.get("b") is b


def test_store_rejects_bad_ids():
    with pytest.raises(ValueError):
        SessionStore().get_or_create("../etc/passwd")
