from schild.merge import merge_spans
from schild.spans import Span

TEXT = "Anna Keller, Bahnhofstrasse 5, 3011 Bern, AHV 756.1234.5678.97"


def span(start, end, type_, source="apertus"):
    return Span(start, end, type_, TEXT[start:end], source)


def test_disjoint_spans_unchanged():
    a, b = span(0, 11, "PERSON"), span(13, 40, "ADDRESS")
    assert merge_spans([b, a], TEXT) == [a, b]


def test_nested_span_absorbed_by_longer():
    outer, inner = span(0, 40, "ADDRESS"), span(0, 11, "PERSON")
    merged = merge_spans([inner, outer], TEXT)
    assert [(m.start, m.end, m.type) for m in merged] == [(0, 40, "ADDRESS")]


def test_partial_overlap_is_joined():
    a, b = span(0, 20, "PERSON"), span(13, 40, "ADDRESS")
    merged = merge_spans([a, b], TEXT)
    assert [(m.start, m.end) for m in merged] == [(0, 40)]
    assert merged[0].text == TEXT[0:40]
    assert merged[0].type == "ADDRESS"  # longest wins when no checksum span


def test_checksum_rule_span_sets_the_type():
    ahv = span(46, 62, "AHV", source="rules")
    wide = span(42, 62, "PERSON")
    merged = merge_spans([wide, ahv], TEXT)
    assert [(m.start, m.end, m.type, m.source) for m in merged] == [(42, 62, "AHV", "both")]


def test_identical_duplicates_collapse():
    a = span(0, 11, "PERSON")
    assert merge_spans([a, a], TEXT) == [a]


def test_adjacent_spans_stay_separate():
    a, b = span(0, 4, "PERSON"), span(4, 11, "PERSON")
    assert len(merge_spans([a, b], TEXT)) == 2


def test_empty():
    assert merge_spans([], TEXT) == []
