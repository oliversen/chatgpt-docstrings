from __future__ import annotations

import re

import jedi
import lsprotocol.types as lsp


class NotFuncException(Exception):
    pass


class FuncParser:
    def __init__(self, source: str, cursor: lsp.Position) -> None:
        self._source = source
        self._cursor = cursor
        self._script = jedi.Interpreter(self._source, namespaces=[])
        self._context = self._script.get_context(
            self._cursor.line + 1, self._cursor.character
        )
        self._tree_node = self._context._name._value.tree_node
        self.is_func = self._context.type == "function"
        if not self.is_func:
            raise NotFuncException

    @property
    def range(self) -> lsp.Range:  # noqa
        start = self._context.get_definition_start_position()
        end = self._context.get_definition_end_position()
        return lsp.Range(lsp.Position(*start), lsp.Position(*end))

    @property
    def code_lines(self) -> list:
        source_lines = self._source.splitlines(keepends=True)
        return source_lines[self.range.start.line - 1 : self.range.end.line]

    @property
    def code(self) -> str:
        return "".join(self.code_lines)

    @property
    def docstring_range(self) -> lsp.Range | None:
        if doc_node := self._tree_node.get_doc_node():
            return lsp.Range(
                lsp.Position(*doc_node.start_pos),
                lsp.Position(*doc_node.end_pos),
            )
        else:
            return None

    @property
    def suite(self) -> lsp.Position:
        return lsp.Position(*self._tree_node.get_suite().start_pos)

    @property
    def indent_level(self) -> int:
        indent_level = 0
        pattern = r"^\s+"
        match = re.match(pattern, self.code)
        if match:
            indent_count = len(match.group())
            indent_level = indent_count // 4
        return indent_level
