from bench.generate import fill, generate
from schild.rules import ahv_valid, iban_valid


def test_fill_records_offsets():
    text, entities = fill("Hallo {name}, Tel. {phone}.", {"name": "Anna Keller", "phone": "044 123 45 67"})
    assert text == "Hallo Anna Keller, Tel. 044 123 45 67."
    assert [(text[e["start"]:e["end"]], e["type"]) for e in entities] == [("Anna Keller", "PERSON"), ("044 123 45 67", "PHONE")]


def test_generate_size_languages_and_labels():
    docs = generate()
    assert len(docs) == 300
    assert {d["lang"] for d in docs} == {"de", "fr", "it", "en"}
    assert len({d["id"] for d in docs}) == 300
    for d in docs:
        assert "{" not in d["text"]
        for e in d["entities"]:
            value = d["text"][e["start"]:e["end"]]
            assert value.strip() == value and value
            if e["type"] == "AHV":
                assert ahv_valid(value)
            if e["type"] == "IBAN":
                assert iban_valid(value)


def test_generate_is_deterministic():
    assert generate(per_template=2) == generate(per_template=2)


def test_italian_documents_use_ticino_addresses():
    docs = [d for d in generate(per_template=3) if d["lang"] == "it"]
    for d in docs:
        for e in d["entities"]:
            if e["type"] == "ADDRESS":
                address = d["text"][e["start"]:e["end"]]
                assert ", 6" in address and " CA " not in address, address
