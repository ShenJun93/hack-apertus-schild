"""Run the benchmark: python -m bench.run [--limit N] [--no-llm] [--one-pass]"""

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

from bench.hard_cases import load_hard_cases
from bench.metrics import evaluate
from schild.config import load_settings
from schild.llm_detector import DetectorUnavailable, LlmDetector, prompts_for
from schild.merge import merge_spans
from schild.rules import detect_rules
from schild.spans import Span

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = ROOT / "data" / "benchmark.jsonl"
CACHE = ROOT / "data" / "llm_outputs.jsonl"
RESULTS_JSON = ROOT / "docs" / "results.json"
RESULTS_MD = ROOT / "docs" / "results.md"
SYSTEMS = ("rules", "apertus", "schild")


def cache_key(model: str, prompt: str) -> str:
    """Model outputs are cached per model and per prompt version."""
    return f"{model}|prompt-{hashlib.sha256(prompt.encode()).hexdigest()[:8]}"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _as_dict(span: Span) -> dict:
    return {"start": span.start, "end": span.end, "type": span.type, "text": span.text}


def collect_llm(docs: list[dict], llm, model: str, cache_path: Path) -> dict[str, dict]:
    """Return model outputs per document, calling the model only for documents not cached yet.

    With llm=None nothing is called and only cached outputs are returned.
    """
    cached = {}
    if cache_path.exists():
        for row in load_jsonl(cache_path):
            if row["model"] == model:
                cached[row["id"]] = row["output"]
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("a", encoding="utf-8", newline="\n") as f:
        for n, doc in enumerate(docs, 1):
            if doc["id"] in cached or llm is None:
                continue
            started = time.perf_counter()
            try:
                result = llm.detect(doc["text"])
                output = {"spans": [_as_dict(s) for s in result.spans], "hallucinated": result.hallucinated, "error": None}
            except DetectorUnavailable as exc:
                output = {"spans": [], "hallucinated": 0, "error": str(exc)}
            output["latency_s"] = round(time.perf_counter() - started, 3)
            cached[doc["id"]] = output
            f.write(json.dumps({"id": doc["id"], "model": model, "output": output}, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{n}/{len(docs)}] {doc['id']} {output['latency_s']}s {'ERROR ' + output['error'] if output['error'] else ''}",
                  file=sys.stderr)
    return {doc["id"]: cached[doc["id"]] for doc in docs if doc["id"] in cached}


def run_benchmark(docs: list[dict], llm_outputs: dict[str, dict]) -> dict[str, dict]:
    preds = {name: {} for name in SYSTEMS}
    for doc in docs:
        rule_spans = detect_rules(doc["text"])
        output = llm_outputs.get(doc["id"], {"spans": [], "error": "not run"})
        llm_spans = [Span(s["start"], s["end"], s["type"], s["text"], "apertus") for s in output["spans"]]
        preds["rules"][doc["id"]] = [_as_dict(s) for s in rule_spans]
        preds["apertus"][doc["id"]] = [_as_dict(s) for s in llm_spans]
        preds["schild"][doc["id"]] = [_as_dict(s) for s in merge_spans(rule_spans + llm_spans, doc["text"])]
    results = {name: evaluate(docs, preds[name]) for name in SYSTEMS}
    latencies = sorted(o["latency_s"] for o in llm_outputs.values() if "latency_s" in o)
    results["_llm"] = {
        "documents": len(llm_outputs),
        "failures": sum(1 for o in llm_outputs.values() if o.get("error")),
        "hallucinated": sum(o.get("hallucinated", 0) for o in llm_outputs.values()),
        "latency_median_s": statistics.median(latencies) if latencies else None,
        "latency_p90_s": latencies[int(0.9 * (len(latencies) - 1))] if latencies else None,
    }
    return results


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def render_markdown(results: dict[str, dict]) -> str:
    lines = ["# Benchmark results", ""]
    for set_name, res in results.items():
        lines += [f"## {set_name}", "", "| System | Recall | Precision | F1 | Leak rate (docs) |", "|---|---|---|---|---|"]
        for name in SYSTEMS:
            r = res[name]
            lines.append(f"| {name} | {_pct(r['recall'])} | {_pct(r['precision'])} | {_pct(r['f1'])} | {_pct(r['leak_rate'])} |")
        types = sorted({t for name in SYSTEMS for t in res[name]["per_type"]})
        lines += ["", "| Type | " + " | ".join(SYSTEMS) + " |", "|---|" + "---|" * len(SYSTEMS)]
        for t in types:
            lines.append(f"| {t} | " + " | ".join(_pct(res[n]["per_type"].get(t, 0.0)) for n in SYSTEMS) + " |")
        langs = sorted(res["schild"]["per_lang"])
        lines += ["", "| Language | " + " | ".join(SYSTEMS) + " |", "|---|" + "---|" * len(SYSTEMS)]
        for lang in langs:
            lines.append(f"| {lang} | " + " | ".join(_pct(res[n]["per_lang"].get(lang, 0.0)) for n in SYSTEMS) + " |")
        llm = res["_llm"]
        lines += ["", f"Apertus calls: {llm['documents']} documents, {llm['failures']} failures, "
                      f"{llm['hallucinated']} hallucinated entities, median latency {llm['latency_median_s']} s, "
                      f"p90 {llm['latency_p90_s']} s.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--one-pass", action="store_true", help="skip the second, sensitive-data prompt")
    args = parser.parse_args()
    sets = {"synthetic": load_jsonl(BENCHMARK), "hard": load_hard_cases()}
    if args.limit:
        sets = {k: v[: args.limit] for k, v in sets.items()}
    settings = load_settings()
    prompts = prompts_for(settings.sensitive_pass and not args.one_pass)
    key = cache_key(settings.llm_name, "\n---\n".join(prompts))
    if not args.no_llm and not settings.llm_base_url:
        print("LLM_BASE_URL is not set: using cached model outputs only.", file=sys.stderr)
    llm = None if args.no_llm or not settings.llm_base_url else LlmDetector(
        settings.llm_base_url, settings.llm_api_key, settings.llm_name, timeout=settings.llm_timeout, prompts=prompts
    )
    results = {}
    for name, docs in sets.items():
        outputs = {} if args.no_llm else collect_llm(docs, llm, key, CACHE)
        results[name] = run_benchmark(docs, outputs)
    results["_meta"] = {"model": settings.llm_name, "prompt": key, "passes": len(prompts), "llm": not args.no_llm}
    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    RESULTS_MD.write_text(render_markdown({k: v for k, v in results.items() if not k.startswith("_")}), encoding="utf-8")
    print(RESULTS_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
