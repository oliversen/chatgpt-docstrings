import re
from functools import cached_property
from typing import NamedTuple, Union

import jedi


class Position(NamedTuple):
    line: int
    character: int


class Range(NamedTuple):
    start: Position
    end: Position


class NotFuncException(Exception):
    pass


class FuncParser:
    def __init__(self, source: str, cursor: Position) -> None:
        self._source = source
        self._cursor = cursor
        self._script = jedi.Interpreter(self._source, namespaces=[])
        self._context = self._script.get_context(*self._cursor)
        self._tree_node = self._context._name._value.tree_node
        self.is_func = self._context.type == "function"
        if not self.is_func:
            raise NotFuncException

    @cached_property
    def range(self) -> Range:
        start = self._context.get_definition_start_position()
        end = self._context.get_definition_end_position()
        return Range(Position(*start), Position(*end))

    @cached_property
    def code(self) -> str:
        source_lines = self._source.splitlines(keepends=True)
        return "".join(source_lines[self.range.start.line-1:self.range.end.line])

    @cached_property
    def docstring_range(self) -> Union[Range, None]:
        if doc_node := self._tree_node.get_doc_node():
            return Range(Position(*doc_node.start_pos), Position(*doc_node.end_pos))
        else:
            return None

    @cached_property
    def suite(self) -> Position:
        return Position(*self._tree_node.get_suite().start_pos)

    @cached_property
    def indent_level(self) -> int:
        indent_level = 0
        pattern = r"^\s+"
        match = re.match(pattern, self.code)
        if match:
            indent_count = len(match.group())
            indent_level = indent_count // 4
        return indent_level
