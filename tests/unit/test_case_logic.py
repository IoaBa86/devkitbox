from __future__ import annotations

from app.tools.case.logic import (
    split_words,
    to_camel,
    to_constant,
    to_kebab,
    to_lower,
    to_pascal,
    to_sentence,
    to_snake,
    to_title,
    to_upper,
)


def test_split_words_handles_mixed_delimiters_and_camel_boundaries():
    assert split_words("hello_world-fooBar baz") == ["hello", "world", "foo", "Bar", "baz"]


def test_split_words_empty_string():
    assert split_words("") == []


def test_to_lower():
    assert to_lower("HeLLo") == "hello"


def test_to_upper():
    assert to_upper("HeLLo") == "HELLO"


def test_to_title():
    assert to_title("hello world_foo") == "Hello World Foo"


def test_to_sentence():
    assert to_sentence("hello WORLD") == "Hello world"


def test_to_sentence_empty():
    assert to_sentence("   ") == ""


def test_to_camel():
    assert to_camel("hello world foo") == "helloWorldFoo"


def test_to_camel_empty():
    assert to_camel("") == ""


def test_to_pascal():
    assert to_pascal("hello world foo") == "HelloWorldFoo"


def test_to_snake():
    assert to_snake("Hello World Foo") == "hello_world_foo"


def test_to_kebab():
    assert to_kebab("Hello World Foo") == "hello-world-foo"


def test_to_constant():
    assert to_constant("hello world foo") == "HELLO_WORLD_FOO"
