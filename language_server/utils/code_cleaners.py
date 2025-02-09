from __future__ import annotations

from typing import Callable, Iterable

from .code_analyzers import base


class CodeCleaner:
    """A class responsible for cleaning code by applying various cleaning methods.

    This class provides functionality to clean source code by removing docstrings,
    comments, blank lines, etc.

    Attributes:
        _code_entity: The code entity (class, function, or module) to clean.
        _cleaned_code_lines: A list of the cleaned source code lines.
    """

    _code_entity: "base.CodeEntity"
    _cleaned_code_lines: list[str]

    def clean(
        self, code_entity: "base.CodeEntity", *, skip: Iterable[str] | None = None
    ) -> str:
        """Applies all cleaning methods to the code, except the ones specified in `skip`.

        Args:
            code_entity: The code entity (class, function, or module) to clean.
            skip: A list of cleaning method names to skip.
                  If None, all methods will be applied.
        """
        self._code_entity = code_entity
        self._cleaned_code_lines = code_entity.code_lines.copy()
        available_cleaners = set(self.supported_cleaning_methods.keys())

        if skip is not None:
            unsupported_methods = set(skip) - available_cleaners
            if unsupported_methods:
                raise AttributeError(
                    f"Unsupported cleaning methods: {', '.join(unsupported_methods)}."
                )
            available_cleaners -= set(skip)

        for cleaner in available_cleaners:
            self.supported_cleaning_methods[cleaner]()

        return "\n".join(self._cleaned_code_lines)

    @property
    def supported_cleaning_methods(self) -> dict[str, Callable]:
        """Returns a dictionary of supported cleaning methods.

        The keys of the dictionary are method names derived from method names
        prefixed with '_remove_', and the values are the corresponding callable methods.
        """
        return {
            method_name.split("_remove_")[1]: getattr(self, method_name)
            for method_name in dir(self)
            if method_name.startswith("_remove_")
        }

    def _remove_docstring(self) -> None:
        """Removes docstring from the source code."""
        docstring_range = self._code_entity.docstring_range
        if not docstring_range:
            return None
        start_line = self._code_entity.to_relative_position(docstring_range.start).line
        end_line = self._code_entity.to_relative_position(docstring_range.end).line
        del self._cleaned_code_lines[start_line : end_line + 1]

    def _remove_comments(self) -> None:
        """Removes comments from the source code."""
        self._cleaned_code_lines = [
            line
            for line in self._cleaned_code_lines
            if not line.lstrip().startswith("#")
        ]

    def _remove_blank_lines(self) -> None:
        """Removes blank lines from the source code."""
        self._cleaned_code_lines = [
            line for line in self._cleaned_code_lines if line.strip()
        ]


class NamedEntitiesCleaner(CodeCleaner):
    """A class for cleaning code specific to class and function entities.

    Adds functionality for removing indentation.
    """

    _code_entity: "base.NamedCodeEntity"

    def _remove_indentation(self) -> None:
        """Removes indentation from the source code."""
        indent_level = self._code_entity.indent_level
        if indent_level > 0:
            self._cleaned_code_lines = [
                line[4 * indent_level :] for line in self._cleaned_code_lines
            ]


class ModuleCleaner(CodeCleaner):
    """A class for cleaning module-level code."""

    _code_entity: "base.BaseModule"
