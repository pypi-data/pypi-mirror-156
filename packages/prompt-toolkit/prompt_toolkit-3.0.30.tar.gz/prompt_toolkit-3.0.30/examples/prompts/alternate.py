#!/usr/bin/env python
from typing import Callable
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.formatted_text.base import StyleAndTextTuples
from prompt_toolkit.document import Document
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.key_binding.key_processor import KeyPressEvent


class AlternatingLexer(Lexer):
    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        lines = document.lines

        def get_line(lineno: int) -> StyleAndTextTuples:
            "Return the tokens for the given line."
            style = "ansired" if lineno % 2 == 0 else "ansigreen"
            try:
                return [(style, lines[lineno])]
            except IndexError:
                return []

        return get_line


def main() -> None:
    bindings = KeyBindings()

    @bindings.add("|")
    def _(event: KeyPressEvent) -> None:
        "Delimiter, inserts a newline."
        b = event.app.current_buffer
        b.insert_text("\n")

    print("Type something. Type '|' as a delimiter. Type alt+enter to accept")
    text = prompt(
        "Say something: ",
        key_bindings=bindings,
        lexer=AlternatingLexer(),
        multiline=True,
    )
    print("You said: %s" % text)


if __name__ == "__main__":
    main()
