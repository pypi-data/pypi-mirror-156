import typing as t
import enum
import attr


@enum.unique
class PartOfSpeechFilter(enum.Flag):
    noun = enum.auto()
    pronoun = enum.auto()
    verb = enum.auto()
    adjective = enum.auto()
    adverb = enum.auto()
    article = enum.auto()
    preposition = enum.auto()
    conjunction = enum.auto()
    interjection = enum.auto()
    abbreviation = enum.auto()
    other = enum.auto()
    all = (
        noun
        | pronoun
        | verb
        | adjective
        | adverb
        | article
        | preposition
        | conjunction
        | interjection
        | abbreviation
        | other
    )

    @classmethod
    def from_name(cls, name: str) -> "PartOfSpeechFilter":
        for v in cls:
            if v.name.startswith(name[:-1]):
                return v
        return cls.other


@attr.define
class WordDefinition:
    word: str
    html: str


@attr.define
class WordNotFound:
    query: str
    alternatives: list[str]


class Dictionary(t.Protocol):
    def query(
        self, word: str, pos: PartOfSpeechFilter = PartOfSpeechFilter.all
    ) -> WordDefinition | WordNotFound:
        ...
