from code_parser import FuncParser


class FuncCleaner:
    def __init__(self, parsed_func: FuncParser) -> None:
        self._parsed_func = parsed_func
        self._code_lines = parsed_func.code_lines.copy()

    def clean(
        self, docstring: bool = False, comments: bool = False, blank_lines: bool = False
    ) -> str:
        if docstring:
            self._remove_docstring()
        if comments:
            self._remove_comments()
        if blank_lines:
            self._remove_blank_lines()
        return "".join(self._code_lines)

    def _remove_docstring(self) -> None:
        func_range = self._parsed_func.range
        docstring_range = self._parsed_func.docstring_range
        if docstring_range is not None:
            del_lines = (
                docstring_range.start.line - func_range.start.line,
                docstring_range.end.line - func_range.start.line,
            )
            del self._code_lines[del_lines[0]:del_lines[1]+1]

    def _remove_comments(self) -> None:
        raise NotImplementedError

    def _remove_blank_lines(self) -> None:
        self._code_lines = [i for i in self._code_lines if i.strip()]
