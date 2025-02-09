from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Literal, NamedTuple, Protocol, TypeVar

import lsprotocol.types as lsp

from ..code_cleaners import CodeCleaner, ModuleCleaner, NamedEntitiesCleaner

TCodeEntity = TypeVar("TCodeEntity", bound="CodeEntity")


class IPosition(Protocol):
    """Protocol that defines the structure for a position in a document."""

    @property
    def line(self) -> int:
        """Line number of the position."""
        ...

    @property
    def character(self) -> int:
        """Character position on the line."""
        ...


class IRange(Protocol):
    """Protocol that defines the structure for a range in a document."""

    @property
    def start(self) -> IPosition:
        """Start position of the range."""
        ...

    @property
    def end(self) -> IPosition:
        """End position of the range."""
        ...


class Position(NamedTuple):
    """Represents a position in a document, defined by a line and character."""

    line: int
    character: int

    def __str__(self) -> str:
        return f"{self.line}:{self.character}"


class Range(NamedTuple):
    """Represents a range in a document, defined by a start and end position."""

    start: Position
    end: Position

    def __str__(self) -> str:
        return f"{self.start}-{self.end}"


class DocumentPosition(Position):
    """Represents a position in a document with methods to convert to/from LSP format.

    - Document is 1-indexed for lines and 0-indexed for columns
    - LSP is 0-indexed for lines and 0-indexed for columns
    """

    @classmethod
    def from_lsp(cls, position: lsp.Position) -> DocumentPosition:
        """Converts a position from the LSP format."""
        return cls(position.line + 1, position.character)

    def to_lsp(self) -> lsp.Position:
        """Converts a position to the LSP format."""
        return lsp.Position(self.line - 1, self.character)


class DocumentRange(Range):
    """Represents a range in a document with methods to convert to/from LSP format.

    - Document is 1-indexed for lines and 0-indexed for columns
    - LSP is 0-indexed for lines and 0-indexed for columns
    """

    @classmethod
    def from_lsp(cls, range_: lsp.Range) -> DocumentRange:
        """Converts a range from the LSP format."""
        return cls(
            start=DocumentPosition(range_.start.line + 1, range_.start.character),
            end=DocumentPosition(range_.end.line + 1, range_.end.character),
        )

    def to_lsp(self) -> lsp.Range:
        """Converts a range to the LSP format."""
        return lsp.Range(
            start=lsp.Position(self.start.line - 1, self.start.character),
            end=lsp.Position(self.end.line - 1, self.end.character),
        )


class BaseAnalyzer(ABC):
    """Base class for analyzing Python code."""

    def __init__(self, code: str) -> None:
        self._source_code = code

    @abstractmethod
    def get_context(self, cursor: IPosition) -> CodeEntity:
        """Returns the code entity under the cursor."""

    @abstractmethod
    def get_function(self, cursor: IPosition) -> BaseFunction | None:
        """Returns the function entity under the cursor."""

    @abstractmethod
    def get_class(self, cursor: IPosition) -> BaseClass | None:
        """Returns the class entity under the cursor."""

    @abstractmethod
    def get_module(self, cursor: IPosition) -> BaseModule:
        """Returns the module entity under the cursor."""


class CodeEntity(ABC):
    """A base class representing either a function, class, or module of a source code."""

    entity_name: Literal["module", "class", "function"]
    default_cleaner: CodeCleaner = CodeCleaner()

    @property
    @abstractmethod
    def code(self) -> str:
        """Returns the source code of the code entity as a string."""

    @property
    @abstractmethod
    def code_lines(self) -> list[str]:
        """Returns the source code of the code entity split into lines."""

    @property
    @abstractmethod
    def docstring_range(self) -> IRange | None:
        """Returns the start and end positions of the code entity's docstring in code."""

    @abstractmethod
    def to_relative_position(self, position: IPosition) -> IPosition:
        """Converts an absolute position to a relative position within the code entity.

        This function calculates the position relative to the start of the code entity
        from the given absolute position in the source code.
        """

    def clean_code(self, cleaner: CodeCleaner | None = None, *args, **kwargs) -> str:
        """Cleans the code using the provided or default cleaner."""
        cleaner = cleaner or self.default_cleaner
        return cleaner.clean(self, *args, **kwargs)


class NamedCodeEntity(CodeEntity):
    """A base class representing either a function or a class of a source code."""

    default_cleaner = NamedEntitiesCleaner()

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the code entity name."""

    @property
    @abstractmethod
    def code_range(self) -> DocumentRange:
        """Returns the start and end positions of the code entity in source code."""

    @property
    @abstractmethod
    def signature_end(self) -> DocumentPosition:
        """Returns the end position of the code entity signature in the source code."""

    @property
    def indent_level(self) -> int:
        """Returns the indentation level of the source code."""
        indent_level = 0
        if match := re.match(r"^\s+", self.code_lines[0]):
            indent_level = len(match.group()) // 4
        return indent_level

    def to_relative_position(self, position: IPosition) -> IPosition:
        """Converts an absolute position to a relative position within the code entity.

        This function calculates the position relative to the start of the code entity
        from the given absolute position in the source code.
        """
        return Position(position.line - self.code_range.start.line, position.character)


class BaseFunction(NamedCodeEntity):
    """Represents a function of a source code.."""

    entity_name = "function"


class BaseClass(NamedCodeEntity):
    """Represents a class of a source code."""

    entity_name = "class"


class BaseModule(CodeEntity):
    """Represents a module of a source code."""

    entity_name = "module"
    default_cleaner = ModuleCleaner()

    def to_relative_position(self, position: IPosition) -> IPosition:
        """Converts an absolute position to a relative position within the code entity.

        This function calculates the position relative to the start of the code entity
        from the given absolute position in the source code.
        """
        return position
