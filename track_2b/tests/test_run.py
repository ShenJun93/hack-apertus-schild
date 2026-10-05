from fakes import FakeLlm

from bench.run import collect_llm, render_markdown, run_benchmark

DOCS = [
    {"id": "a", "lang": "de", "doc_type": "x", "text": "Anna Keller, AHV 756.1234.5678.97",
     "entities": [{"start": 0, "end": 11, "type": "PERSON"}, {"start": 17, "end": 33, "type": "AHV"}]},
    {"id": "b", "lang": "fr", "doc_type": "x", "text": "Marc Favre, tél. 021 345 67 89",
     "entities": [{"start": 0, "end": 10, "type": "PERSON"}, {"start": 17, "end": 30, "type": "PHONE"}]},
]


def test_three_systems_and_cache(tmp_path):
    llm = FakeLlm([("Anna Keller", "PERSON"), ("Marc Favre", "PERSON")])
    cache = tmp_path / "cache.jsonl"
    outputs = collect_llm(DOCS, llm, "m", cache)
    assert llm.calls == 2
    results = run_benchmark(DOCS, outputs)
    assert results["rules"]["recall"] == 0.5
    assert results["apertus"]["recall"] == 0.5
    assert results["schild"]["recall"] == 1.0 and results["schild"]["leak_rate"] == 0.0
    again = collect_llm(DOCS, llm, "m", cache)
    assert llm.calls == 2 and again == outputs


def test_failures_are_recorded_and_schild_falls_back_to_rules(tmp_path):
    outputs = collect_llm(DOCS, FakeLlm(fail=True), "m", tmp_path / "c.jsonl")
    assert all(o["error"] for o in outputs.values())
    results = run_benchmark(DOCS, outputs)
    assert results["schild"]["recall"] == results["rules"]["recall"]
    assert results["_llm"]["failures"] == 2


def test_markdown_has_all_systems(tmp_path):
    outputs = collect_llm(DOCS, FakeLlm(), "m", tmp_path / "c.jsonl")
    md = render_markdown({"synthetic": run_benchmark(DOCS, outputs)})
    assert "| rules |" in md and "| apertus |" in md and "| schild |" in md


def test_cache_key_changes_with_the_prompt():
    from bench.run import cache_key

    assert cache_key("m", "prompt A") != cache_key("m", "prompt B")
    assert cache_key("m", "prompt A") == cache_key("m", "prompt A")
    assert cache_key("m", "prompt A").startswith("m|prompt-")


def test_without_a_model_only_cached_outputs_are_used(tmp_path):
    cache = tmp_path / "c.jsonl"
    collect_llm(DOCS[:1], FakeLlm([("Anna Keller", "PERSON")]), "m", cache)
    outputs = collect_llm(DOCS, None, "m", cache)
    assert list(outputs) == ["a"]
