from fakes import FakeLlm

from schild.pipeline import redact_text
from schild.vault import Session, restore

TEXT = "Anna Keller, AHV 756.1234.5678.97, leidet an Epilepsie. Anna Keller ruft an: 044 123 45 67."


def test_rules_and_model_combined():
    llm = FakeLlm([("Anna Keller", "PERSON"), ("Epilepsie", "HEALTH")])
    result = redact_text(TEXT, Session("s"), llm)
    assert result.redacted_text == "[PERSON_1], AHV [AHV_1], leidet an [HEALTH_1]. [PERSON_1] ruft an: [PHONE_1]."
    assert result.degraded is False and result.session_id == "s"


def test_repeated_name_redacted_everywhere():
    result = redact_text(TEXT, Session("s"), FakeLlm([("Anna Keller", "PERSON")]))
    assert "Anna Keller" not in result.redacted_text


def test_model_outage_gives_rules_only_and_degraded():
    result = redact_text(TEXT, Session("s"), FakeLlm(fail=True))
    assert result.degraded is True
    assert "[AHV_1]" in result.redacted_text and "Anna Keller" in result.redacted_text


def test_no_model_configured_is_degraded():
    assert redact_text(TEXT, Session("s"), None).degraded is True


def test_round_trip():
    session = Session("s")
    result = redact_text(TEXT, session, FakeLlm([("Anna Keller", "PERSON"), ("Epilepsie", "HEALTH")]))
    assert restore(result.redacted_text, session) == TEXT
