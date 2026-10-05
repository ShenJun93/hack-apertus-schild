import json
from dataclasses import asdict
from importlib import resources

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from .config import load_settings
from .llm_detector import LlmDetector, prompts_for
from .pipeline import redact_text
from .upstream import Upstream, UpstreamError
from .vault import SessionStore, restore

MAX_CHARS = 200_000


class RedactIn(BaseModel):
    text: str = Field(max_length=MAX_CHARS)
    session_id: str | None = None


class RestoreIn(BaseModel):
    session_id: str
    text: str = Field(max_length=MAX_CHARS)


def create_app(llm=None, upstream=None, store: SessionStore | None = None) -> FastAPI:
    app = FastAPI(title="Schild", version="0.1.0")
    store = store or SessionStore()

    def session_for(session_id):
        try:
            return store.get_or_create(session_id)
        except ValueError:
            raise HTTPException(422, "invalid session_id")

    @app.get("/", response_class=HTMLResponse)
    def index():
        return resources.files("schild").joinpath("static/index.html").read_text(encoding="utf-8")

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "llm_configured": llm is not None, "upstream_configured": upstream is not None}

    @app.post("/v1/redact")
    def redact(body: RedactIn):
        return asdict(redact_text(body.text, session_for(body.session_id), llm))

    @app.post("/v1/restore")
    def restore_text(body: RestoreIn):
        session = store.get(body.session_id)
        if session is None:
            raise HTTPException(404, "unknown session_id")
        return {"text": restore(body.text, session)}

    @app.post("/v1/chat/completions")
    def chat(body: dict):
        messages = body.get("messages")
        if not isinstance(messages, list) or not messages:
            raise HTTPException(400, "messages must be a non-empty list")
        session = store.get_or_create()
        outgoing = []
        count = 0
        for message in messages:
            if not isinstance(message, dict) or not isinstance(message.get("content"), str):
                raise HTTPException(400, "Only string message content is supported.")
            if len(message["content"]) > MAX_CHARS:
                raise HTTPException(413, "message too long")
            result = redact_text(message["content"], session, llm)
            if result.degraded:
                return JSONResponse(
                    status_code=503,
                    content={"error": {"type": "schild_degraded", "message": "The Apertus pass did not run, so nothing was forwarded."}},
                )
            count += len(result.entities)
            outgoing.append({"role": message.get("role", "user"), "content": result.redacted_text})
        meta = {"session_id": session.id, "entities_redacted": count}
        if upstream is None:
            preview = json.dumps(outgoing, ensure_ascii=False, indent=2)
            return {
                "object": "chat.completion",
                "model": "schild-preview",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": "No upstream model is configured. This is exactly what would be sent:\n" + preview},
                    }
                ],
                "schild": {**meta, "forwarded": False},
            }
        try:
            answer = upstream.complete(outgoing)
        except UpstreamError as exc:
            raise HTTPException(502, f"upstream error: {exc}")
        for choice in answer.get("choices", []):
            message = choice.get("message") or {}
            if isinstance(message.get("content"), str):
                message["content"] = restore(message["content"], session)
        answer["schild"] = {**meta, "forwarded": True}
        return answer

    return app


def create_app_from_env() -> FastAPI:
    s = load_settings()
    llm = (
        LlmDetector(s.llm_base_url, s.llm_api_key, s.llm_name, timeout=s.llm_timeout, prompts=prompts_for(s.sensitive_pass))
        if s.llm_base_url
        else None
    )
    upstream = (
        Upstream(s.upstream_base_url, s.upstream_api_key, s.upstream_model or s.llm_name, timeout=s.llm_timeout)
        if s.upstream_base_url
        else None
    )
    return create_app(llm=llm, upstream=upstream)


app = create_app_from_env()
