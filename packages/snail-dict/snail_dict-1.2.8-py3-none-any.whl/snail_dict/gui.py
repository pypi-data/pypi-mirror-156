import traceback
from snail_dict import qt
import shlex
from snail_dict.dictionary import (
    Dictionary,
    WordDefinition,
    WordNotFound,
)
from snail_dict.dict_modules import OxfordUKDictionary
from snail_dict.conf import LOG, RES_DIR
from snail_dict.cli import parse_args


with open(RES_DIR / "sanitize.css") as file:
    CSS_BASE = file.read()

with open(RES_DIR / "css_light.css") as file:
    CSS_LIGHT = file.read()

with open(RES_DIR / "html_template.html") as file:
    TEMPLATE = file.read()


class MainWindow(qt.QWidget):
    def __init__(self, parent=None, flags=qt.WindowType.Window):
        super().__init__(parent=parent, flags=flags)
        self.dictionary: Dictionary = OxfordUKDictionary()

        LOG.info("Creating the window")
        layout = qt.QVBoxLayout()
        self.input = qt.QLineEdit()
        self.output = qt.QWebEngineView()
        layout.addWidget(self.input)
        layout.addWidget(self.output, stretch=1)
        self.setLayout(layout)
        self.output.page().setBackgroundColor(qt.Qt.GlobalColor.transparent)
        self.output.page().settings().setAttribute(
            qt.QWebEngineSettings.WebAttribute.JavascriptEnabled, False
        )
        self.input.editingFinished.connect(self.search)

    @qt.slot()
    def search(self):
        query_text: str = self.input.text().strip()
        if query_text == "":
            return

        args = parse_args(shlex.split(query_text))
        future = qt.QThreadFuture(self.dictionary.query, args.word, args.pos)
        future.done.connect(self.on_result)
        future.fail.connect(lambda e: LOG.error("Failed to make the request: %s", "".join(traceback.format_exception(e))))
        future.submit()

    @qt.slot(object)
    def on_result(self, result: WordDefinition | WordNotFound):
        match result:
            case WordDefinition(word=word, html=html):
                mimedata = qt.QMimeData()
                mimedata.setText(html)
                mimedata.setHtml(html)
                qt.QApplication.instance().clipboard().setMimeData(mimedata)
                self.output.setHtml(self._format_html(html))

            case WordNotFound(query=query, alternatives=[]):
                self.output.setHtml(self._format_html(f"<h1>'{query}' not found</h1>"))
            case WordNotFound(query=query, alternatives=alternatives):
                html = (
                    f"<h1>'{query}' not found. Similar queries:</h1><ul>"
                    + "\n".join(
                        f"<li>{alternative}</li>" for alternative in alternatives
                    )
                    + "</ul>"
                )
                self.output.setHtml(self._format_html(html))

    def closeEvent(self, e):
        LOG.info("Shutting down.")
        e.accept()

    def _format_html(self, content: str) -> str:
        return TEMPLATE.format(content=content, style=CSS_LIGHT)


def main():
    app = qt.QApplication(["snail-dict"])
    app.setDesktopFileName("snail-dict.desktop")
    window = MainWindow()
    window.resize(640, 900)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
