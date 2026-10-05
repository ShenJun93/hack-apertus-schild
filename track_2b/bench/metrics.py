from collections import defaultdict


def _ratio(hit: int, total: int, empty: float) -> float:
    return hit / total if total else empty


def evaluate(docs: list[dict], predictions: dict[str, list[dict]]) -> dict:
    """Privacy-oriented scores.

    An entity counts as protected only if every non-space character of it lies inside some
    predicted span, whatever type that span carries. A predicted span is correct if it overlaps
    any gold entity.
    """
    per_type = defaultdict(lambda: [0, 0])
    per_lang = defaultdict(lambda: [0, 0])
    leaked_docs = n_pred = n_true = 0
    for doc in docs:
        text = doc["text"]
        preds = predictions.get(doc["id"], [])
        covered = [False] * len(text)
        for p in preds:
            for i in range(p["start"], p["end"]):
                covered[i] = True
        leaked = False
        for g in doc["entities"]:
            protected = all(covered[i] for i in range(g["start"], g["end"]) if not text[i].isspace())
            per_type[g["type"]][0] += protected
            per_type[g["type"]][1] += 1
            per_lang[doc["lang"]][0] += protected
            per_lang[doc["lang"]][1] += 1
            leaked |= not protected
        leaked_docs += leaked
        for p in preds:
            n_pred += 1
            n_true += any(p["start"] < g["end"] and g["start"] < p["end"] for g in doc["entities"])
    hit = sum(v[0] for v in per_type.values())
    n_gold = sum(v[1] for v in per_type.values())
    recall = _ratio(hit, n_gold, 0.0)
    precision = _ratio(n_true, n_pred, 1.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "n_docs": len(docs), "n_gold": n_gold, "n_pred": n_pred,
        "recall": recall, "precision": precision, "f1": f1,
        "leak_rate": _ratio(leaked_docs, len(docs), 0.0),
        "per_type": {t: _ratio(*v, 0.0) for t, v in sorted(per_type.items())},
        "per_lang": {lang: _ratio(*v, 0.0) for lang, v in sorted(per_lang.items())},
    }
