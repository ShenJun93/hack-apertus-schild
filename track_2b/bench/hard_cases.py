import re
from pathlib import Path

_MARK_RE = re.compile(r"\[\[([A-Z]+):(.+?)\]\]")


def parse_marked(marked: str) -> tuple[str, list[dict]]:
    parts: list[str] = []
    entities: list[dict] = []
    pos = 0
    length = 0
    for m in _MARK_RE.finditer(marked):
        literal = marked[pos:m.start()]
        parts.append(literal)
        length += len(literal)
        value = m.group(2)
        entities.append({"start": length, "end": length + len(value), "type": m.group(1)})
        parts.append(value)
        length += len(value)
        pos = m.end()
    parts.append(marked[pos:])
    return "".join(parts), entities


def load_hard_cases(path: Path = Path("bench/hard_cases.txt")) -> list[dict]:
    docs = []
    for block in path.read_text(encoding="utf-8").split("=== ")[1:]:
        header, _, body = block.partition("\n")
        doc_id = header.strip()
        text, entities = parse_marked(body.strip())
        docs.append({"id": doc_id, "lang": doc_id[:2], "doc_type": "hard", "text": text, "entities": entities})
    return docs
