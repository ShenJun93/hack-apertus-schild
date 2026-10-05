import pytest

from schild.rules import ahv_valid, detect_rules, iban_valid


@pytest.mark.parametrize("number", ["756.1234.5678.97", "7569876543217", "756 0000 1111 28"])
def test_valid_ahv(number):
    assert ahv_valid(number)


@pytest.mark.parametrize("number", ["756.1234.5678.98", "755.1234.5678.97", "756.1234.5678"])
def test_invalid_ahv(number):
    assert not ahv_valid(number)


@pytest.mark.parametrize("iban", ["CH93 0076 2011 6238 5295 7", "CH9300762011623852957", "ch24 0483 5035 2181 7200 a"])
def test_valid_iban(iban):
    assert iban_valid(iban)


@pytest.mark.parametrize("iban", ["CH93 0076 2011 6238 5295 8", "DE89 3704 0044 0532 0130 00", "CH93 0076"])
def test_invalid_iban(iban):
    assert not iban_valid(iban)


def kinds(text):
    return [(s.type, s.text) for s in detect_rules(text)]


def test_detects_ahv_and_skips_bad_checksum():
    assert kinds("AHV 756.1234.5678.97, alt 756.1234.5678.98") == [("AHV", "756.1234.5678.97")]


def test_detects_iban_lowercase_and_spaced():
    assert ("IBAN", "ch24 0483 5035 2181 7200 a") in kinds("Konto ch24 0483 5035 2181 7200 a bitte")


@pytest.mark.parametrize("phone", ["+41 44 123 45 67", "044 123 45 67", "0041 79 555 12 34", "+41 (0)21 345 67 89"])
def test_detects_phone_formats(phone):
    assert ("PHONE", phone) in kinds(f"Tel. {phone}.")


def test_phone_does_not_fire_on_dates_or_ahv():
    assert [t for t, _ in kinds("am 01.02.1985, AHV 756.1234.5678.97")] == ["AHV"]


def test_detects_email():
    assert ("EMAIL", "pa.favre@bluewin.ch") in kinds("Mail: pa.favre@bluewin.ch.")


@pytest.mark.parametrize(
    "text, date",
    [
        ("geboren am 12.03.1985", "12.03.1985"),
        ("(geb. 1.2.1960)", "1.2.1960"),
        ("Geburtsdatum: 05.11.1979", "05.11.1979"),
        ("née le 3 avril 1958", "3 avril 1958"),
        ("né(e) le 07.07.1970", "07.07.1970"),
        ("nato il 14.07.1971", "14.07.1971"),
        ("Data di nascita: 2 maggio 1966", "2 maggio 1966"),
        ("born on 9 March 1990", "9 March 1990"),
        ("(DOB 02/11/1990)", "02/11/1990"),
    ],
)
def test_detects_dates_of_birth(text, date):
    assert ("DOB", date) in kinds(text)


def test_plain_dates_are_not_dob():
    assert kinds("Termin am 12.03.2026") == []


def test_offsets_point_at_the_text():
    text = "Zürich, Tel. 044 123 45 67"
    span = detect_rules(text)[0]
    assert text[span.start:span.end] == span.text == "044 123 45 67"
    assert span.source == "rules"


@pytest.mark.parametrize("phone", ["079/123 45 67", "044/123 45 67"])
def test_detects_phone_with_slash(phone):
    assert ("PHONE", phone) in kinds(f"Tel. {phone}.")
