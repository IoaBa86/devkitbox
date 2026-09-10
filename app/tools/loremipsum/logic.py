"""Pure Lorem Ipsum generation logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import random

from app.core.exceptions import ValidationError

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
    "magna",
    "aliqua",
    "enim",
    "ad",
    "minim",
    "veniam",
    "quis",
    "nostrud",
    "exercitation",
    "ullamco",
    "laboris",
    "nisi",
    "aliquip",
    "ex",
    "ea",
    "commodo",
    "consequat",
    "duis",
    "aute",
    "irure",
    "in",
    "reprehenderit",
    "voluptate",
    "velit",
    "esse",
    "cillum",
    "fugiat",
    "nulla",
    "pariatur",
    "excepteur",
    "sint",
    "occaecat",
    "cupidatat",
    "non",
    "proident",
    "sunt",
    "culpa",
    "qui",
    "officia",
    "deserunt",
    "mollit",
    "anim",
    "id",
    "est",
    "laborum",
)

_START_WORDS = ("lorem", "ipsum", "dolor", "sit", "amet")

UNITS = ("Words", "Sentences", "Paragraphs")


def generate_words(count: int, start_with_lorem: bool = True) -> list[str]:
    if count < 1:
        raise ValidationError("Word count must be at least 1")

    words: list[str] = []
    if start_with_lorem:
        words.extend(_START_WORDS[: min(count, len(_START_WORDS))])
    remaining = count - len(words)
    words.extend(random.choice(_WORDS) for _ in range(remaining))
    return words


def generate_sentence(min_words: int = 6, max_words: int = 14) -> str:
    count = random.randint(min_words, max_words)
    words = [random.choice(_WORDS) for _ in range(count)]
    words[0] = words[0].capitalize()
    return " ".join(words) + "."


def generate_paragraph(min_sentences: int = 3, max_sentences: int = 7) -> str:
    count = random.randint(min_sentences, max_sentences)
    return " ".join(generate_sentence() for _ in range(count))


def generate(count: int, unit: str, start_with_lorem: bool = True) -> str:
    if unit not in UNITS:
        raise ValidationError(f"Unknown unit: {unit}")
    if count < 1:
        raise ValidationError("Count must be at least 1")

    if unit == "Words":
        return " ".join(generate_words(count, start_with_lorem))

    if unit == "Sentences":
        sentences = [generate_sentence() for _ in range(count)]
        if start_with_lorem:
            sentences[0] = (
                "Lorem ipsum dolor sit amet, " + sentences[0][0].lower() + sentences[0][1:]
            )
        return " ".join(sentences)

    paragraphs = [generate_paragraph() for _ in range(count)]
    if start_with_lorem:
        paragraphs[0] = (
            "Lorem ipsum dolor sit amet, " + paragraphs[0][0].lower() + paragraphs[0][1:]
        )
    return "\n\n".join(paragraphs)
