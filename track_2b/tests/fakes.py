from schild.llm_detector import DetectorUnavailable, LlmResult, locate
from schild.spans import Span


class FakeLlm:
    """Finds the given (value, TYPE) pairs the way the real detector locates them."""

    def __init__(self, entities=(), fail=False):
        self.entities = list(entities)
        self.fail = fail
        self.calls = 0

    def detect(self, text):
        self.calls += 1
        if self.fail:
            raise DetectorUnavailable("fake outage")
        spans = []
        for value, type_ in self.entities:
            for start, end in locate(text, value):
                spans.append(Span(start, end, type_, text[start:end], "apertus"))
        return LlmResult(spans, 0)


class EchoUpstream:
    """Pretends to be an external model; records what it was sent."""

    def __init__(self):
        self.sent = None

    def complete(self, messages):
        self.sent = messages
        return {
            "object": "chat.completion",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "Reply about " + messages[-1]["content"]}}],
        }
