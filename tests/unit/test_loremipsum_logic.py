from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.loremipsum.logic import (
    generate,
    generate_paragraph,
    generate_sentence,
    generate_words,
)


def test_generate_words_count():
    words = generate_words(10)
    assert len(words) == 10


def test_generate_words_starts_with_lorem_ipsum():
    words = generate_words(5, start_with_lorem=True)
    assert words[:5] == ["lorem", "ipsum", "dolor", "sit", "amet"]


def test_generate_words_without_lorem_start():
    words = generate_words(5, start_with_lorem=False)
    assert len(words) == 5


def test_generate_words_invalid_count_raises():
    with pytest.raises(ValidationError):
        generate_words(0)


def test_generate_sentence_capitalized_and_ends_with_period():
    sentence = generate_sentence()
    assert sentence[0].isupper()
    assert sentence.endswith(".")


def test_generate_paragraph_is_nonempty():
    paragraph = generate_paragraph()
    assert len(paragraph) > 0
    assert paragraph.endswith(".")


def test_generate_words_unit():
    result = generate(5, "Words")
    assert len(result.split()) == 5


def test_generate_sentences_unit():
    result = generate(2, "Sentences")
    assert result.count(".") >= 2


def test_generate_paragraphs_unit():
    result = generate(2, "Paragraphs")
    assert "\n\n" in result


def test_generate_starts_with_lorem_ipsum_phrase():
    result = generate(1, "Paragraphs", start_with_lorem=True)
    assert result.lower().startswith("lorem ipsum dolor sit amet")


def test_generate_unknown_unit_raises():
    with pytest.raises(ValidationError):
        generate(1, "Chapters")


def test_generate_invalid_count_raises():
    with pytest.raises(ValidationError):
        generate(0, "Words")
