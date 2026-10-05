"""Generate the labelled synthetic benchmark: python -m bench.generate"""

import json
import random
import re
import unicodedata
from pathlib import Path

from faker import Faker

from bench.templates import LISTS, TEMPLATES

SLOT_TYPES = {
    "name": "PERSON", "name2": "PERSON", "address": "ADDRESS", "ahv": "AHV", "iban": "IBAN",
    "phone": "PHONE", "email": "EMAIL", "dob": "DOB", "health": "HEALTH", "religion": "RELIGION",
    "ethnicity": "ETHNICITY", "criminal": "CRIMINAL", "social": "SOCIAL",
}
# Faker has no complete it_CH locale: Italian names and street names come from it_IT, and
# addresses are completed with Ticino postcodes and towns.
NAME_LOCALES = {"de": "de_CH", "fr": "fr_CH", "it": "it_IT", "en": "en_GB"}
ADDRESS_LOCALES = {"de": "de_CH", "fr": "fr_CH", "it": "it_IT", "en": "de_CH"}
TICINO = [("6900", "Lugano"), ("6500", "Bellinzona"), ("6600", "Locarno"), ("6850", "Mendrisio"),
          ("6830", "Chiasso"), ("6710", "Biasca"), ("6612", "Ascona")]
EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
             "September", "October", "November", "December"]
DOMAINS = ["bluewin.ch", "gmx.ch", "sunrise.ch", "proton.me", "hispeed.ch"]
SLOT_RE = re.compile(r"\{(\w+)\}")
OUT = Path(__file__).resolve().parent.parent / "data" / "benchmark.jsonl"


def ahv_number(rng: random.Random) -> str:
    body = "756" + "".join(str(rng.randrange(10)) for _ in range(9))
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(body))
    digits = body + str((10 - total % 10) % 10)
    style = rng.choice(["dots", "dots", "compact"])
    return digits if style == "compact" else f"{digits[:3]}.{digits[3:7]}.{digits[7:11]}.{digits[11:]}"


def iban_number(rng: random.Random) -> str:
    bban = "".join(str(rng.randrange(10)) for _ in range(17))
    check = 98 - int("".join(str(int(c, 36)) for c in bban + "CH00")) % 97
    compact = f"CH{check:02d}{bban}"
    if rng.random() < 0.3:
        return compact
    return " ".join(compact[i:i + 4] for i in range(0, len(compact), 4))


def phone_number(rng: random.Random) -> str:
    area = rng.choice(["21", "22", "31", "44", "61", "71", "91", "76", "77", "78", "79"])
    rest = f"{rng.randrange(100, 1000)} {rng.randrange(10, 100)} {rng.randrange(10, 100)}"
    return rng.choice([f"+41 {area} {rest}", f"0{area} {rest}", f"+41 (0){area} {rest}"])


def email_for(name: str, rng: random.Random) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    parts = [p for p in re.sub(r"[^a-z ]", "", ascii_name).split() if len(p) > 1]
    return ".".join(parts[-2:] or ["kontakt"]) + "@" + rng.choice(DOMAINS)


def birth_date(fake: Faker, lang: str, rng: random.Random) -> str:
    d = fake.date_of_birth(minimum_age=18, maximum_age=90)
    if lang == "en" and rng.random() < 0.5:
        return f"{d.day} {EN_MONTHS[d.month - 1]} {d.year}"
    return d.strftime("%d.%m.%Y")


def address_for(places: Faker, lang: str, rng: random.Random) -> str:
    if lang == "it":
        postcode, town = rng.choice(TICINO)
        return f"{places.street_name()} {rng.randrange(1, 120)}, {postcode} {town}"
    return places.address().replace("\n", ", ")


def make_values(names: Faker, places: Faker, lang: str, rng: random.Random) -> dict[str, str]:
    name = names.name()
    name2 = names.name()
    while name2 == name:
        name2 = names.name()
    values = {
        "name": name, "name2": name2,
        "address": address_for(places, lang, rng),
        "ahv": ahv_number(rng), "iban": iban_number(rng), "phone": phone_number(rng),
        "email": email_for(name, rng), "dob": birth_date(names, lang, rng),
    }
    for slot, by_lang in LISTS.items():
        values[slot] = rng.choice(by_lang[lang])
    return values


def fill(template: str, values: dict[str, str]) -> tuple[str, list[dict]]:
    parts: list[str] = []
    entities: list[dict] = []
    pos = 0
    length = 0
    for m in SLOT_RE.finditer(template):
        literal = template[pos:m.start()]
        parts.append(literal)
        length += len(literal)
        value = values[m.group(1)]
        entities.append({"start": length, "end": length + len(value), "type": SLOT_TYPES[m.group(1)]})
        parts.append(value)
        length += len(value)
        pos = m.end()
    parts.append(template[pos:])
    return "".join(parts), entities


def generate(per_template: int = 15, seed: int = 2026) -> list[dict]:
    rng = random.Random(seed)
    docs = []
    for lang, by_type in TEMPLATES.items():
        names = Faker(NAME_LOCALES[lang])
        names.seed_instance(seed)
        places = Faker(ADDRESS_LOCALES[lang])
        places.seed_instance(seed + 1)
        for doc_type, template in by_type.items():
            for i in range(per_template):
                text, entities = fill(template, make_values(names, places, lang, rng))
                docs.append({"id": f"{lang}-{doc_type}-{i:03d}", "lang": lang, "doc_type": doc_type,
                             "text": text, "entities": entities})
    return docs


def main() -> None:
    docs = generate()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"wrote {len(docs)} documents to {OUT}")


if __name__ == "__main__":
    main()
