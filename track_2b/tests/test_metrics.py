from bench.hard_cases import load_hard_cases, parse_marked
from bench.metrics import evaluate
from schild.rules import ahv_valid, iban_valid


def test_parse_marked():
    text, entities = parse_marked("Hoi [[PERSON:Röbi]], Tel. [[PHONE:044 123 45 67]].")
    assert text == "Hoi Röbi, Tel. 044 123 45 67."
    assert [(text[e["start"]:e["end"]], e["type"]) for e in entities] == [("Röbi", "PERSON"), ("044 123 45 67", "PHONE")]


def test_hard_cases_file_is_valid():
    docs = load_hard_cases()
    assert len(docs) == 20 and {d["lang"] for d in docs} == {"de", "fr", "it", "en"}
    for d in docs:
        assert "[[" not in d["text"] and d["entities"]
        for e in d["entities"]:
            value = d["text"][e["start"]:e["end"]]
            if e["type"] == "AHV":
                assert ahv_valid(value), value
            if e["type"] == "IBAN":
                assert iban_valid(value), value


DOC = {"id": "d1", "lang": "de", "text": "Anna Keller wohnt in Bern.",
       "entities": [{"start": 0, "end": 11, "type": "PERSON"}, {"start": 21, "end": 25, "type": "ADDRESS"}]}


def test_full_coverage_any_type_counts():
    preds = {"d1": [{"start": 0, "end": 11, "type": "ADDRESS"}, {"start": 21, "end": 25, "type": "ADDRESS"}]}
    r = evaluate([DOC], preds)
    assert r["recall"] == 1.0 and r["precision"] == 1.0 and r["leak_rate"] == 0.0 and r["f1"] == 1.0


def test_partial_coverage_is_a_leak():
    r = evaluate([DOC], {"d1": [{"start": 0, "end": 4, "type": "PERSON"}]})
    assert r["per_type"]["PERSON"] == 0.0 and r["leak_rate"] == 1.0


def test_false_positive_lowers_precision():
    preds = {"d1": [{"start": 0, "end": 11, "type": "PERSON"}, {"start": 12, "end": 17, "type": "PERSON"}]}
    r = evaluate([DOC], preds)
    assert r["precision"] == 0.5 and r["recall"] == 0.5


def test_no_predictions():
    r = evaluate([DOC], {})
    assert r["recall"] == 0.0 and r["n_pred"] == 0 and r["precision"] == 1.0
