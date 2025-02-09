from __future__ import annotations

from typing import Literal

import jedi
from jedi.api.classes import Name as JediName

from .base import (
    BaseAnalyzer,
    BaseClass,
    BaseFunction,
    BaseModule,
    CodeEntity,
    DocumentPosition,
    DocumentRange,
    IPosition,
    NamedCodeEntity,
    TCodeEntity,
)
from .factory import AnalyzerFactory


class JediEntity(CodeEntity):
    """Represents a code entity of a source code analyzed with Jedi."""

    def __init__(self, source_code: str, context: JediName) -> None:
        self._document_source_code = source_code
        self._context = context
        self._tree_node = context._name._value.tree_node

    @property
    def code(self) -> str:
        """Returns the source code of the code entity as a string."""
        return "\n".join(self.code_lines)

    @property
    def code_lines(self) -> list[str]:
        """Returns the source code of the code entity split into lines."""
        return self._document_source_code.splitlines()

    @property
    def docstring_range(self) -> DocumentRange | None:
        """Returns the start and end positions of the code entity docstring in code."""
        if doc_node := self._tree_node.get_doc_node():
            return DocumentRange(
                DocumentPosition(*doc_node.start_pos),
                DocumentPosition(*doc_node.end_pos),
            )
        else:
            return None


class JediNamedCodeEntity(JediEntity, NamedCodeEntity):
    """Represents either a function or a class of a source code analyzed with Jedi."""

    @property
    def name(self) -> str:
        """Returns the code entity name."""
        return self._tree_node.name.value

    @property
    def signature_end(self) -> DocumentPosition:
        """Returns the end position of the code entity signature in the source code."""
        return DocumentPosition(*self._tree_node.get_suite().start_pos)

    @property
    def code_lines(self) -> list[str]:
        """Returns the source code of the code entity split into lines."""
        source_lines = super().code_lines
        return source_lines[self.code_range.start.line - 1 : self.code_range.end.line]

    @property
    def code_range(self) -> DocumentRange:
        """Returns the start and end positions of the code entity in the source code."""
        return DocumentRange(
            DocumentPosition(*self._context.get_definition_start_position()),
            DocumentPosition(*self._context.get_definition_end_position()),
        )


class JediFunction(JediNamedCodeEntity, BaseFunction):
    """Represents a function of a source code analyzed with Jedi."""


class JediClass(JediNamedCodeEntity, BaseClass):
    """Represents a class of a source code analyzed with Jedi."""


class JediModule(JediEntity, BaseModule):
    """Represents a module of a source code analyzed with Jedi."""


@AnalyzerFactory.register_analyzer("jedi")
class JediAnalyzer(BaseAnalyzer):
    """Analyzer that uses Jedi for analyzing Python code."""

    ENTITY_MAP = {"function": JediFunction, "class": JediClass, "module": JediModule}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._script = jedi.Script(
            self._source_code, environment=jedi.InterpreterEnvironment()
        )

    def get_context(self, cursor: IPosition) -> JediEntity | None:
        """Returns the code entity under the cursor."""
        context = self._script.get_context(cursor.line, cursor.character)
        if context and context.type in self.ENTITY_MAP:
            entity_cls = self.ENTITY_MAP[context.type]
            return entity_cls(self._source_code, context)
        return None

    def get_function(self, cursor: IPosition) -> JediFunction | None:
        """Returns the function entity under the cursor."""
        return self._find_entity(cursor, "function", JediFunction)

    def get_class(self, cursor: IPosition) -> JediClass | None:
        """Returns the class entity under the cursor."""
        return self._find_entity(cursor, "class", JediClass)

    def get_module(self, cursor: IPosition) -> JediModule | None:
        """Returns the module entity under the cursor."""
        return self._find_entity(cursor, "module", JediModule)

    def _find_entity(
        self,
        cursor: IPosition,
        entity_type: Literal["function", "class", "module"],
        entity_class: type[TCodeEntity],
    ) -> TCodeEntity | None:
        """Helper method to return the entity under the cursor based on its type."""
        context = self._script.get_context(cursor.line, cursor.character)

        while context:
            if context.type == entity_type:
                return entity_class(self._source_code, context)
            context = context.parent()

        return None
