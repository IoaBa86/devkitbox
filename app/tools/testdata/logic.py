"""Pure random test-data generation logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import csv
import io
import json
import random
import uuid
from collections.abc import Callable
from dataclasses import dataclass

_FIRST_NAMES = (
    "James",
    "Mary",
    "Robert",
    "Patricia",
    "John",
    "Jennifer",
    "Michael",
    "Linda",
    "William",
    "Elizabeth",
    "David",
    "Barbara",
    "Richard",
    "Susan",
    "Joseph",
    "Jessica",
)
_LAST_NAMES = (
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
)
_DOMAINS = ("example.com", "mail.com", "test.org", "sample.net")
_STREETS = ("Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St")
_CITIES = ("Springfield", "Riverside", "Franklin", "Georgetown", "Clinton", "Madison")
_COMPANIES = (
    "Globex",
    "Initech",
    "Umbrella Corp",
    "Stark Industries",
    "Wayne Enterprises",
    "Acme Co",
)
_WORDS = (
    "lorem",
    "ipsum",
    "dolor",
    "sit",
    "amet",
    "consectetur",
    "adipiscing",
    "elit",
    "sed",
    "do",
    "eiusmod",
    "tempor",
    "incididunt",
    "ut",
    "labore",
    "et",
    "dolore",
)


def _full_name() -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def _email() -> str:
    first = random.choice(_FIRST_NAMES).lower()
    last = random.choice(_LAST_NAMES).lower()
    return f"{first}.{last}@{random.choice(_DOMAINS)}"


def _phone() -> str:
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def _address() -> str:
    return f"{random.randint(1, 9999)} {random.choice(_STREETS)}, {random.choice(_CITIES)}"


def _company() -> str:
    return random.choice(_COMPANIES)


def _boolean() -> bool:
    return random.choice([True, False])


def _integer() -> int:
    return random.randint(0, 1000)


def _float_value() -> float:
    return round(random.uniform(0, 1000), 2)


def _uuid_value() -> str:
    return str(uuid.uuid4())


def _date() -> str:
    year = random.randint(2000, 2025)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"


def _sentence() -> str:
    length = random.randint(6, 12)
    words = [random.choice(_WORDS) for _ in range(length)]
    words[0] = words[0].capitalize()
    return " ".join(words) + "."


FIELD_GENERATORS: dict[str, Callable[[], object]] = {
    "Full Name": _full_name,
    "Email": _email,
    "Phone": _phone,
    "Address": _address,
    "Company": _company,
    "Boolean": _boolean,
    "Integer": _integer,
    "Float": _float_value,
    "UUID": _uuid_value,
    "Date": _date,
    "Sentence": _sentence,
}


@dataclass(frozen=True, slots=True)
class FieldSpec:
    name: str
    field_type: str


def generate_records(fields: list[FieldSpec], count: int) -> list[dict[str, object]]:
    if count < 0:
        raise ValueError("Count must be non-negative")
    for field in fields:
        if field.field_type not in FIELD_GENERATORS:
            raise ValueError(f"Unknown field type: {field.field_type}")

    records = []
    for _ in range(count):
        record = {field.name: FIELD_GENERATORS[field.field_type]() for field in fields}
        records.append(record)
    return records


def to_json(records: list[dict[str, object]]) -> str:
    return json.dumps(records, indent=2)


def to_csv(records: list[dict[str, object]], fieldnames: list[str]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)
    return buffer.getvalue()
