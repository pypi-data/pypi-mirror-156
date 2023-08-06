import typing as t
from snail_dict import cache
from selectolax.lexbor import LexborHTMLParser, LexborNode as Node
from snail_dict.dictionary import PartOfSpeechFilter, WordDefinition, WordNotFound
from snail_dict import util as u

MAX_EXAMPLE = 3


class OxfordUKDictionary:
    def __init__(self):
        self.client = cache.CachedWebSession()

    def query(
        self, word: str, pos: PartOfSpeechFilter = PartOfSpeechFilter.all
    ) -> WordDefinition | WordNotFound:
        content = self.client.get_content(f"https://www.lexico.com/definition/{word}")

        page = LexborHTMLParser(content)
        root = page.css_first(".entryWrapper")
        if root is None:
            raise RuntimeError("Parser Error: .entryWrapper not found")

        word_e = root.css_first("div.entryHead")
        if word_e is None:
            if alternatives := root.css_first(".similar-results"):
                return WordNotFound(word, parse_alternatives(alternatives))
            else:
                return WordNotFound(word, [])

        content = "".join(parse_definition(root, pos))
        return WordDefinition(word, content)


def parse_alternatives(node: Node) -> list[str]:
    return [element.text(strip=True, deep=False) for element in node.css("ul li a")]


def parse_definition(root: Node, pos: PartOfSpeechFilter) -> t.Iterable[str]:
    for tag in root.iter():
        if tag.tag == "div" and "entryHead" in tag.attrs["class"]:
            yield "<h1>{}</h1>\n".format(tag.css_first("h2 span").html)
        elif tag.tag == "section" and "gramb" in tag.attrs["class"]:
            yield from parse_sense_group(tag, pos)
        elif tag.tag == "section" and pos == PartOfSpeechFilter.all:
            yield tag.html


def parse_sense_group(root: Node, pos_filter: PartOfSpeechFilter) -> t.Iterable[str]:
    pos_element = root.css_first("h3.pos")
    pos = pos_element.css_first("span.pos").text(strip=False, separator="", deep=False)

    if not (PartOfSpeechFilter.from_name(pos) & pos_filter):
        return

    yield f"<h3><span class='pos'>{pos}</span> \n"

    if transitivity := root.css_first(".transitivity"):
        if content := transitivity.text(strip=True):
            yield f"<span class='transitivity'>{content}</span>\n"

    if grammatical_note := root.css_first(".grammatical_note"):
        if grammatical_note.parent is root:
            yield f"<span class='grammatical_note'>{grammatical_note.text(strip=True)}</span>\n"

    if inflections := pos_element.css("span.pos-inflections>span>span"):
        yield "(" + ",".join(
            e.text(strip=True, separator="", deep=False) for e in inflections
        ) + ")\n"

    yield "</h3>\n"

    yield "<ol>\n"
    for element in root.css(".semb>li>div"):
        yield from parse_sense(element)
    yield "</ol>\n"


def parse_sense(root: Node) -> t.Iterable[str]:
    yield "<li>\n<p>"
    for n in root.iter():
        if (cls := n.attrs.get("class", "")) in {
            "grammatical_note",
            "form-groups",
            "sense-registers",
            "sense-regions",
        }:
            yield f"<span class='{cls}'>{n.text(strip=True)}</span>"

    if element := root.css_first("span.ind"):
        yield element.text(strip=True)  # Definition

    if element := root.css_first("div.crossReference"):
        yield element.text(strip=True, separator=" ")

    yield "</p>\n"

    if paragraph := root.css_first(".trg"):
        yield f"<p>{paragraph.text(separator=' ', deep=True, strip=True)}</p>\n"

    if examples := root.css(".ex"):
        shown, hidden = examples[:MAX_EXAMPLE], examples[MAX_EXAMPLE:]

        yield "<span>"
        yield " | ".join(u.flatten(parse_example(tag) for tag in shown))
        yield "</span>\n"

        if hidden:
            yield "<details>\n"
            yield "<summary>More Examples</summary>"
            yield "<ul>\n"
            for ex in hidden:
                yield "<li>\n"
                yield from parse_example(ex)
                yield "</li>\n"
            yield "</ul\n>"
            yield "</details>\n"

    if synonyms := root.css_first(".synonyms"):
        yield f"<h4>Synonyms</h4>\n"
        yield f"<p>{synonyms.text(separator=' ')}</p>\n"

    yield "</li>\n"

    if sub_senses := root.css(".subSense"):
        yield "<ol>\n"
        for s in sub_senses:
            yield from parse_sense(s)
        yield "</ol>\n"


def parse_example(n: Node) -> t.Iterable[str]:
    example_text = n.text(separator=" ", strip=True).strip(" |‘|’")
    yield f"<span class='example'>{example_text}</span>"
