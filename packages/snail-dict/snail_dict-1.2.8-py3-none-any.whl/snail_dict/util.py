from typing import Optional, TypeVar, Callable, Type
import typing as t

T = TypeVar("T")
R = TypeVar("R")


POS_TO_ABBR = {
    "adjective": "adj.",
    "noun": "n.",
    "verb": "v.",
    "adverb": "adv.",
    "conjunction": "conj.",
    "pronoun": "pron.",
    "preposition": "prep.",
}
ABBR_TO_POS = {v: k for k, v in POS_TO_ABBR.items()}


def flatten(i: t.Iterable[t.Iterable[T]]) -> t.Iterable[T]:
    for ii in i:
        yield from ii
