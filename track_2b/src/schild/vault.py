import re
import uuid
from collections import OrderedDict

from .spans import Span

PLACEHOLDER_RE = re.compile(r"\[([A-Za-z]+)_(\d+)\]")
_ID_RE = re.compile(r"[A-Za-z0-9-]{1,64}")


def _normalise(value: str) -> str:
    return " ".join(value.split()).casefold()


class Session:
    """Placeholder mapping for one conversation. Lives only in this process."""

    def __init__(self, session_id: str):
        self.id = session_id
        self._forward: dict[tuple[str, str], str] = {}
        self._reverse: dict[str, str] = {}
        self._counters: dict[str, int] = {}

    def placeholder_for(self, span_type: str, value: str, avoid=frozenset()) -> str:
        key = (span_type, _normalise(value))
        if key in self._forward:
            return self._forward[key]
        n = self._counters.get(span_type, 0)
        while True:
            n += 1
            candidate = f"[{span_type}_{n}]"
            if candidate not in avoid and candidate not in self._reverse:
                break
        self._counters[span_type] = n
        self._forward[key] = candidate
        self._reverse[candidate] = value
        return candidate

    def original(self, placeholder: str) -> str | None:
        return self._reverse.get(placeholder.upper())


def apply(text: str, spans: list[Span], session: Session) -> tuple[str, list[dict]]:
    avoid = {m.group(0).upper() for m in PLACEHOLDER_RE.finditer(text)}
    parts: list[str] = []
    entities: list[dict] = []
    pos = 0
    for span in sorted(spans, key=lambda s: s.start):
        placeholder = session.placeholder_for(span.type, span.text, avoid)
        parts.append(text[pos:span.start])
        parts.append(placeholder)
        pos = span.end
        entities.append(
            {"type": span.type, "placeholder": placeholder, "start": span.start, "end": span.end, "source": span.source}
        )
    parts.append(text[pos:])
    return "".join(parts), entities


def restore(text: str, session: Session) -> str:
    def swap(match: re.Match) -> str:
        value = session.original(match.group(0))
        return value if value is not None else match.group(0)

    return PLACEHOLDER_RE.sub(swap, text)


class SessionStore:
    def __init__(self, max_sessions: int = 1000):
        self._sessions: OrderedDict[str, Session] = OrderedDict()
        self._max = max_sessions

    def get_or_create(self, session_id: str | None = None) -> Session:
        if session_id is not None and not _ID_RE.fullmatch(session_id):
            raise ValueError("invalid session_id")
        if session_id is not None and session_id in self._sessions:
            self._sessions.move_to_end(session_id)
            return self._sessions[session_id]
        session = Session(session_id or uuid.uuid4().hex)
        self._sessions[session.id] = session
        while len(self._sessions) > self._max:
            self._sessions.popitem(last=False)
        return session

    def get(self, session_id: str) -> Session | None:
        session = self._sessions.get(session_id)
        if session is not None:
            self._sessions.move_to_end(session_id)
        return session
