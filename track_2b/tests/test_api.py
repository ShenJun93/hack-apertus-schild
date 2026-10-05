from fakes import EchoUpstream, FakeLlm
from fastapi.testclient import TestClient

from schild.api import create_app

LLM = FakeLlm([("Anna Keller", "PERSON"), ("Epilepsie", "HEALTH")])
TEXT = "Anna Keller leidet an Epilepsie. Tel. 044 123 45 67"


def client(llm=LLM, upstream=None):
    return TestClient(create_app(llm=llm, upstream=upstream))


def test_index_and_health():
    c = client()
    assert "Schild" in c.get("/").text
    assert c.get("/healthz").json() == {"ok": True, "llm_configured": True, "upstream_configured": False}


def test_redact_then_restore():
    c = client()
    body = c.post("/v1/redact", json={"text": TEXT}).json()
    assert body["redacted_text"] == "[PERSON_1] leidet an [HEALTH_1]. Tel. [PHONE_1]"
    assert body["degraded"] is False and len(body["entities"]) == 3
    back = c.post("/v1/restore", json={"session_id": body["session_id"], "text": "Hallo [PERSON_1]"}).json()
    assert back == {"text": "Hallo Anna Keller"}


def test_redact_keeps_session_across_calls():
    c = client()
    first = c.post("/v1/redact", json={"text": "Anna Keller"}).json()
    second = c.post("/v1/redact", json={"text": "Wieder Anna Keller", "session_id": first["session_id"]}).json()
    assert second["redacted_text"] == "Wieder [PERSON_1]"


def test_restore_unknown_session_404():
    assert client().post("/v1/restore", json={"session_id": "nope", "text": "x"}).status_code == 404


def test_redact_unknown_session_id_404():
    c = client()
    assert c.post("/v1/redact", json={"text": "x", "session_id": "demo"}).status_code == 404
    assert c.post("/v1/redact", json={"text": "x", "session_id": "a/b"}).status_code == 404
    assert c.post("/v1/restore", json={"session_id": "demo", "text": "[PERSON_1]"}).status_code == 404


def test_chat_refuses_unknown_roles():
    up = EchoUpstream()
    for role in ("Anna Keller AHV 756.1234.5678.97", {"x": "Anna Keller"}):
        r = client(upstream=up).post("/v1/chat/completions", json={"messages": [{"role": role, "content": "hi"}]})
        assert r.status_code == 400
    assert up.sent is None


def test_chat_accepts_standard_roles():
    up = EchoUpstream()
    msgs = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}, {"role": "assistant", "content": "a"}]
    assert client(upstream=up).post("/v1/chat/completions", json={"messages": msgs}).status_code == 200


def test_chat_forwards_redacted_and_restores_answer():
    up = EchoUpstream()
    r = client(upstream=up).post("/v1/chat/completions", json={"messages": [{"role": "user", "content": TEXT}]})
    assert r.status_code == 200
    assert up.sent == [{"role": "user", "content": "[PERSON_1] leidet an [HEALTH_1]. Tel. [PHONE_1]"}]
    assert r.json()["choices"][0]["message"]["content"] == "Reply about " + TEXT
    assert r.json()["schild"]["forwarded"] is True


def test_chat_fails_closed_when_model_down():
    up = EchoUpstream()
    r = client(llm=FakeLlm(fail=True), upstream=up).post(
        "/v1/chat/completions", json={"messages": [{"role": "user", "content": TEXT}]}
    )
    assert r.status_code == 503 and up.sent is None


def test_chat_without_upstream_returns_preview():
    r = client().post("/v1/chat/completions", json={"messages": [{"role": "user", "content": TEXT}]})
    content = r.json()["choices"][0]["message"]["content"]
    assert "[PERSON_1]" in content and "Anna Keller" not in content
    assert r.json()["schild"]["forwarded"] is False


def test_chat_drops_extra_message_fields():
    up = EchoUpstream()
    client(upstream=up).post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "name": "Anna Keller", "content": "hi", "tool_calls": []}]},
    )
    assert up.sent == [{"role": "user", "content": "hi"}]


def test_chat_refuses_non_string_content():
    up = EchoUpstream()
    r = client(upstream=up).post(
        "/v1/chat/completions", json={"messages": [{"role": "user", "content": [{"type": "text", "text": TEXT}]}]}
    )
    assert r.status_code == 400 and up.sent is None


def test_chat_requires_messages():
    assert client().post("/v1/chat/completions", json={}).status_code == 400
