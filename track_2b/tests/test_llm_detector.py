import json

import httpx
import pytest

from schild.llm_detector import (
    DetectorUnavailable,
    LlmDetector,
    ParseError,
    chunk_text,
    parse_entities,
)


def reply(content, status=200):
    return httpx.Response(status, json={"choices": [{"message": {"role": "assistant", "content": content}}]})


def detector(handler, **kw):
    return LlmDetector("http://model/v1", "key", "apertus", transport=httpx.MockTransport(handler), **kw)


def entities_json(*pairs):
    return json.dumps({"entities": [{"text": t, "type": k} for t, k in pairs]})


def test_parse_plain_fenced_and_think():
    assert parse_entities(entities_json(("Anna", "PERSON"))) == [("Anna", "PERSON")]
    assert parse_entities("```json\n" + entities_json(("Anna", "person")) + "\n```") == [("Anna", "PERSON")]
    assert parse_entities("<think>hmm {x}</think>Sure: " + entities_json(("Bern", "ADDRESS"))) == [("Bern", "ADDRESS")]


def test_parse_drops_unknown_types_and_bad_items():
    content = json.dumps({"entities": [{"text": "Acme", "type": "ORG"}, "junk", {"text": 3, "type": "PERSON"}]})
    assert parse_entities(content) == []


def test_parse_rejects_non_json():
    with pytest.raises(ParseError):
        parse_entities("I could not find anything.")


def test_detect_locates_every_occurrence_and_counts_hallucinations():
    text = "Herr Müller ruft an. Müller hat Diabetes Typ 2."

    def handler(request):
        return reply(entities_json(("Müller", "PERSON"), ("Diabetes Typ 2", "HEALTH"), ("Peter Frei", "PERSON")))

    result = detector(handler).detect(text)
    got = [(s.start, s.end, s.type, s.text) for s in result.spans]
    assert (5, 11, "PERSON", "Müller") in got and (21, 27, "PERSON", "Müller") in got
    assert (32, 46, "HEALTH", "Diabetes Typ 2") in got
    assert result.hallucinated == 1
    assert all(s.source == "apertus" for s in result.spans)


def test_case_insensitive_fallback():
    def handler(request):
        return reply(entities_json(("anna keller", "PERSON")))

    span = detector(handler).detect("Anna Keller kommt.").spans[0]
    assert (span.start, span.end, span.text) == (0, 11, "Anna Keller")


def test_retries_once_on_bad_json_then_succeeds():
    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        return reply("no json here") if len(calls) == 1 else reply(entities_json(("Anna", "PERSON")))

    assert detector(handler).detect("Anna").spans[0].text == "Anna"
    assert len(calls) == 2
    assert "JSON object only" in calls[1]["messages"][1]["content"]


def test_bad_json_twice_is_unavailable():
    with pytest.raises(DetectorUnavailable):
        detector(lambda r: reply("nope")).detect("Anna")


def test_http_error_is_unavailable():
    with pytest.raises(DetectorUnavailable):
        detector(lambda r: httpx.Response(500, text="boom")).detect("Anna")


def test_timeout_is_unavailable():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(DetectorUnavailable):
        detector(handler).detect("Anna")


def test_json_mode_dropped_after_400():
    seen = []

    def handler(request):
        body = json.loads(request.content)
        seen.append("response_format" in body)
        return httpx.Response(400, text="unsupported") if "response_format" in body else reply(entities_json())

    d = detector(handler)
    d.detect("Anna")
    assert seen == [True, False] and d.json_mode is False


def test_request_shape():
    captured = {}

    def handler(request):
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("authorization")
        captured["body"] = json.loads(request.content)
        return reply(entities_json())

    detector(handler).detect("Anna")
    assert captured["url"] == "http://model/v1/chat/completions"
    assert captured["auth"] == "Bearer key"
    assert captured["body"]["model"] == "apertus" and captured["body"]["temperature"] == 0
    assert captured["body"]["messages"][0]["role"] == "system"


def test_chunk_text_prefers_paragraphs():
    text = "a" * 30 + "\n\n" + "b" * 30
    assert chunk_text(text, 40) == [(0, "a" * 30), (30, "\n\n" + "b" * 30)]


def test_long_text_is_chunked_with_offsets():
    paragraph = "Notiz ohne Namen. " * 10
    text = paragraph + "\n\nAnna Keller wohnt hier.\n\n" + paragraph + "\n\nMarco Rossi auch."
    asked = []

    def handler(request):
        chunk = json.loads(request.content)["messages"][1]["content"]
        asked.append(chunk)
        names = [n for n in ("Anna Keller", "Marco Rossi") if n in chunk]
        return reply(entities_json(*[(n, "PERSON") for n in names]))

    result = detector(handler, max_chunk_chars=200).detect(text)
    assert len(asked) > 1
    assert sorted(text[s.start:s.end] for s in result.spans) == ["Anna Keller", "Marco Rossi"]


def test_empty_text_makes_no_call():
    def handler(request):
        raise AssertionError("should not be called")

    assert detector(handler).detect("   ").spans == []


def test_second_prompt_adds_a_call_per_chunk_and_unions_results():
    from schild.llm_detector import SENSITIVE_PROMPT, SYSTEM_PROMPT

    asked = []

    def handler(request):
        system = json.loads(request.content)["messages"][0]["content"]
        asked.append(system)
        if system == SENSITIVE_PROMPT:
            return reply(entities_json(("Sozialhilfe", "SOCIAL")))
        return reply(entities_json(("Anna Keller", "PERSON")))

    d = LlmDetector("http://model/v1", None, "m", transport=httpx.MockTransport(handler),
                    prompts=(SYSTEM_PROMPT, SENSITIVE_PROMPT))
    result = d.detect("Anna Keller bezieht Sozialhilfe.")
    assert asked == [SYSTEM_PROMPT, SENSITIVE_PROMPT]
    assert sorted((s.type, s.text) for s in result.spans) == [("PERSON", "Anna Keller"), ("SOCIAL", "Sozialhilfe")]


def test_default_is_one_prompt():
    from schild.llm_detector import SYSTEM_PROMPT

    assert LlmDetector("http://m/v1", None, "m").prompts == (SYSTEM_PROMPT,)


def test_sensitive_pass_failure_is_unavailable():
    from schild.llm_detector import SENSITIVE_PROMPT, SYSTEM_PROMPT

    def handler(request):
        system = json.loads(request.content)["messages"][0]["content"]
        return httpx.Response(500) if system == SENSITIVE_PROMPT else reply(entities_json())

    d = LlmDetector("http://model/v1", None, "m", transport=httpx.MockTransport(handler),
                    prompts=(SYSTEM_PROMPT, SENSITIVE_PROMPT))
    with pytest.raises(DetectorUnavailable):
        d.detect("Anna")


def test_prompts_for_setting():
    from schild.llm_detector import SENSITIVE_PROMPT, SYSTEM_PROMPT, prompts_for

    assert prompts_for(False) == (SYSTEM_PROMPT,)
    assert prompts_for(True) == (SYSTEM_PROMPT, SENSITIVE_PROMPT)
