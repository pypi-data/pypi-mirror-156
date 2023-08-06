from functools import reduce
import sys
import docopt
import attr
from snail_dict.dict_modules import lexico_uk
from snail_dict.dictionary import PartOfSpeechFilter, WordDefinition, WordNotFound


@attr.define
class Query:
    word: str
    pos: PartOfSpeechFilter


CLI_HELP = """snail-dict

Usage:
    snail-dict <word> [<pos>...]

Options:
    -h --help     Show this screen.
    --version     Show version.
"""


def parse_args(args) -> Query:
    opts = docopt.docopt(CLI_HELP, args)
    pos = PartOfSpeechFilter.all
    if opts["<pos>"]:
        pos = reduce(PartOfSpeechFilter.__and__, map(PartOfSpeechFilter.from_name, pos))
    return Query(word=opts["<word>"], pos=pos)


def main():
    query = parse_args(sys.argv[1:])
    dictionary = lexico_uk.OxfordUKDictionary()
    match dictionary.query(query.word, query.pos):
        case WordDefinition(word=_, html=html):
            print(html)
        case WordNotFound(query=_, alternatives=[]):
            print("Word not found.")
        case WordNotFound(query=_, alternatives=alternatives):
            print("Word not found, here are some similar words:")
            for a in alternatives:
                print(a)


if __name__ == "__main__":
    main()
