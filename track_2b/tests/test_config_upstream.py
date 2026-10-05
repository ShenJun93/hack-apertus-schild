import httpx
import pytest

from schild.config import load_settings
from schild.upstream import Upstream, UpstreamError


def test_defaults_when_env_empty():
    s = load_settings({})
    assert s.llm_base_url is None and s.upstream_base_url is None
    assert s.llm_name == "swiss-ai/Apertus-v1.5-8B" and s.llm_timeout == 120.0


def test_reads_env_and_strips_blanks():
    s = load_settings({"LLM_BASE_URL": " http://m/v1 ", "LLM_API_KEY": "", "LLM_NAME": "x", "LLM_TIMEOUT": "30"})
    assert s.llm_base_url == "http://m/v1" and s.llm_api_key is None and s.llm_name == "x" and s.llm_timeout == 30.0


def test_upstream_posts_and_returns_json():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["body"] = request.content
        return httpx.Response(200, json={"choices": []})

    up = Upstream("http://up/v1/", "k", "big", transport=httpx.MockTransport(handler))
    assert up.complete([{"role": "user", "content": "hi"}]) == {"choices": []}
    assert seen["url"] == "http://up/v1/chat/completions" and b'"model":"big"' in seen["body"].replace(b" ", b"")


def test_upstream_errors():
    up = Upstream("http://up/v1", None, "m", transport=httpx.MockTransport(lambda r: httpx.Response(503)))
    with pytest.raises(UpstreamError):
        up.complete([{"role": "user", "content": "hi"}])


def test_sensitive_pass_setting():
    assert load_settings({}).sensitive_pass is False
    assert load_settings({"SCHILD_SENSITIVE_PASS": "1"}).sensitive_pass is True
    assert load_settings({"SCHILD_SENSITIVE_PASS": "0"}).sensitive_pass is False
