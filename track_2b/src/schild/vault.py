import re
import threading
import uuid
from collections import OrderedDict

from .spans import Span

PLACEHOLDER_RE = re.compile(r"\[([A-Za-z]+)_(\d+)\]")
_ID_RE = re.compile(r"[A-Za-z0-9-]{1,64}")


def _normalise(value: str) -> str:
    return " ".join(value.split()).casefold()


def literal_placeholders(*texts: str) -> set[str]:
    """Placeholder-shaped strings already written in the input; Schild must not hand them out."""
    return {m.group(0).upper() for text in texts for m in PLACEHOLDER_RE.finditer(text)}


class Session:
    """Placeholder mapping for one conversation. Lives only in this process."""

    def __init__(self, session_id: str):
        self.id = session_id
        self._forward: dict[tuple[str, str], str] = {}
        self._reverse: dict[str, str] = {}
        self._counters: dict[str, int] = {}
        self._lock = threading.Lock()

    def placeholder_for(self, span_type: str, value: str, avoid=frozenset()) -> str:
        key = (span_type, _normalise(value))
        with self._lock:
            existing = self._forward.get(key)
            if existing is not None and existing not in avoid:
                return existing
            # New value, or its placeholder also appears literally in this input: give it a fresh
            # one, so one placeholder never stands for two different things upstream.
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

    def known(self) -> list[tuple[str, str]]:
        """(type, value) for every value this session has already replaced."""
        with self._lock:
            return [(span_type, self._reverse[ph]) for (span_type, _), ph in self._forward.items()]

    def original(self, placeholder: str) -> str | None:
        return self._reverse.get(placeholder.upper())


def apply(text: str, spans: list[Span], session: Session, avoid: set[str] | None = None) -> tuple[str, list[dict]]:
    """Replace spans with placeholders. `avoid` defaults to the placeholders written in `text`;
    pass the set for several texts (e.g. all chat messages) to keep them apart."""
    avoid = literal_placeholders(text) if avoid is None else avoid
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
        self._lock = threading.Lock()

    def get_or_create(self, session_id: str | None = None) -> Session:
        if session_id is not None and not _ID_RE.fullmatch(session_id):
            raise ValueError("invalid session_id")
        with self._lock:
            if session_id is not None and session_id in self._sessions:
                self._sessions.move_to_end(session_id)
                return self._sessions[session_id]
            session = Session(session_id or uuid.uuid4().hex)
            self._sessions[session.id] = session
            while len(self._sessions) > self._max:
                self._sessions.popitem(last=False)
            return session

    def get(self, session_id: str) -> Session | None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is not None:
                self._sessions.move_to_end(session_id)
            return session
