from __future__ import annotations

import ast
import contextlib
import re
import tokenize
from io import BytesIO
from tokenize import TokenInfo
from typing import Protocol, TypeVar, Union, cast

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
    Position,
)
from .factory import AnalyzerFactory

NamedNodes = Union[ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef]
ContextNodes = Union[ast.Module, NamedNodes]
TContextNode = TypeVar("TContextNode", bound=ContextNodes)


class ASTWithLocation(ast.mod):
    """AST node with end location information."""

    end_lineno: int
    end_col_offset: int


class NamedASTWithLocation(ASTWithLocation):
    """AST node with name and body, including location information."""

    name: str
    body: list[ast.stmt]


def _check_location_attrs(node: ast.AST) -> None:
    """Checks if the node has valid location attributes."""
    if node.end_lineno is None or node.end_col_offset is None:
        raise AttributeError("Node is missing `end_lineno` or `end_col_offset`.")


def _check_named_node_attrs(node: NamedNodes) -> None:
    """Checks if the node has `name` and `body` attributes."""
    for attr in ("name", "body"):
        if not hasattr(node, attr):
            raise AttributeError(f"Node is missing attribute: {attr}")


def ensure_node_has_location(node: ast.AST) -> ASTWithLocation:
    """Ensures the node has both `end_lineno` and `end_col_offset` attributes.

    The end positions are not required by the compiler and are therefore optional.
    """
    _check_location_attrs(node)
    return cast(ASTWithLocation, node)


def ensure_named_node_has_location(node: NamedNodes) -> NamedASTWithLocation:
    """Ensures the named node has both `end_lineno` and `end_col_offset` attributes.

    The end positions are not required by the compiler and are therefore optional.
    """
    _check_named_node_attrs(node)
    _check_location_attrs(node)
    return cast(NamedASTWithLocation, node)


def is_cursor_within_node(node: ast.AST, cursor: IPosition) -> bool:
    """Determine if the cursor is inside the given node.

    This function checks if the cursor's position is within the line range
    of the specified node. It considers both the starting and ending line
    numbers of the node, as well as the column offset for cases where the
    cursor is on the same line as the node.

    Args:
        node: The node to check against.
        cursor: The cursor position to check.

    Returns:
        True if the cursor is inside the node, False otherwise.
    """
    node = ensure_node_has_location(node)
    if node.lineno <= cursor.line <= node.end_lineno:
        return cursor.character > node.col_offset
    return False


def is_child_node(node: ast.AST, parent: ast.AST) -> bool:
    """Check if the node is a child of the given parent node.

    This function traverses the abstract syntax tree (AST) starting from the
    parent node and checks if the specified node is present in the subtree.

    Args:
        node: The node to check if it is a child.
        parent: The parent node to check against.

    Returns:
        True if the node is a child of the parent node, False otherwise.
    """
    return any(i for i in ast.walk(parent) if i is node)


def get_source_segment(source: str, node: ast.AST, *, padded: bool = False) -> str:
    """Get source code segment of the *source* that generated *node*.

    Args:
        source: The source code as a string from which the segment will be extracted.
        node: The node whose corresponding source code segment is to be extracted.
        padded: If True, the function ensures the extracted segment maintains
            proper indentation by padding the first line of the statement.

    Returns:
        The source code segment corresponding to the node, or None if any location
        information is missing (e.g., `lineno`, `end_lineno`,`col_offset`,
        or `end_col_offset`).
    """
    node = ensure_node_has_location(node)

    lineno = node.lineno - 1
    end_lineno = node.end_lineno - 1
    col_offset = node.col_offset
    end_col_offset = node.end_col_offset

    lines = _splitlines_no_ff(source)

    if padded:
        padding = _pad_whitespace(lines[lineno].encode()[:col_offset].decode())
    else:
        padding = ""

    if end_lineno == lineno:
        return padding + lines[lineno].encode()[col_offset:end_col_offset].decode()

    first = padding + lines[lineno].encode()[col_offset:].decode()
    last = lines[end_lineno].encode()[:end_col_offset].decode()
    lines = lines[lineno + 1 : end_lineno]

    lines.insert(0, first)
    lines.append(last)
    return "".join(lines)


def _find_colon_tokens(code: str | list[str]) -> list[TokenInfo] | None:
    """Find and return colon tokens in the given code.

    This function tokenizes the provided code string
    and collects all tokens that are colons.

    Args:
        code: The source code to be analyzed as a string.

    Returns:
        A list of tokenize.TokenInfo objects representing
        the colon tokens found in the code.
        Returns None if no colon tokens are present.
    """
    if isinstance(code, list):
        code = "\n".join(code)
    colons = []
    tokens = tokenize.tokenize(BytesIO(code.encode("utf-8")).readline)
    for token in tokens:
        if token.type == tokenize.OP and token.exact_type == tokenize.COLON:
            colons.append(token)
    return colons if colons else None


def _splitlines_no_ff(source: str) -> list[str]:
    """Split a string into lines ignoring form feed and other chars.

    This mimics how the Python parser splits source code.
    """
    idx = 0
    lines = []
    next_line = ""
    while idx < len(source):
        c = source[idx]
        next_line += c
        idx += 1
        # Keep \r\n together
        if c == "\r" and idx < len(source) and source[idx] == "\n":
            next_line += "\n"
            idx += 1
        if c in "\r\n":
            lines.append(next_line)
            next_line = ""

    if next_line:
        lines.append(next_line)
    return lines


def _pad_whitespace(source: str) -> str:
    r"""Replace all chars except '\f\t' in a line with spaces."""
    result = ""
    for c in source:
        if c in "\f\t":
            result += c
        else:
            result += " "
    return result


class IASTContextResolver(Protocol):
    """Interface for resolving the context of an AST based on the cursor position.

    This protocol defines methods to retrieve the current function, class, and
    module context from an abstract syntax tree (AST) based on the cursor position.

    Attributes:
        cursor: The position of the cursor in the code.
        ast_tree: The AST to resolve context from.
    """

    def __init__(self, cursor: IPosition, ast_tree: ast.AST) -> None: ...

    def find_function_node(self) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
        """Finds the last function node under the cursor position."""

    def find_class_node(self) -> ast.ClassDef | None:
        """Finds the last class node under the cursor position."""

    def find_module_node(self) -> ast.Module | None:
        """Finds the module node."""

    def get_current_context(self) -> ContextNodes | None:
        """Returns the current context based on the cursor position."""


class ASTContextResolver(ast.NodeVisitor):
    """Visitor for traversing an AST to resolve the context based on the cursor position.

    This class tracks the current function, class and module context while visiting nodes
    in the AST. It maintains stack for module, classes and functions to allow retrieval
    of the most recent context.

    Attributes:
        _cursor: The position of the cursor in the code.
        _node_stack: Stack of module, class and function nodes that the cursor is inside.

    """

    def __init__(self, cursor: IPosition, ast_tree: ast.AST) -> None:
        self._cursor = cursor
        self._node_stack = []
        self.visit(ast_tree)

    def _should_visit(self, node: ast.AST) -> bool:
        """Checks if the given node needs to be visited.

        Returns True
            - if the cursor is within of the node
            - if the node does not have `end_lineno` and `end_col_offset` attributes
        """
        with contextlib.suppress(AttributeError):
            return is_cursor_within_node(node, self._cursor)
        return True

    def visit(self, node: ast.AST) -> None:
        """Visits the given AST node.

        This method dynamically calls the appropriate visit method based on the node type.
        """
        if self._should_visit(node):
            method = "visit_" + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node)
        return None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visits a function definition node and adds it to the node stack."""
        self._node_stack.append(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visits an async function definition node and adds it to the node stack."""
        self._node_stack.append(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visits an class definition node and adds it to the node stack."""
        self._node_stack.append(node)
        self.generic_visit(node)

    def visit_Module(self, node: ast.Module) -> None:
        """Visits an module definition node and adds it to the node stack."""
        self._node_stack.append(node)
        self.generic_visit(node)

    def _find_last_of_type(
        self, node_type: type[TContextNode] | tuple[type[TContextNode], ...]
    ) -> TContextNode | None:
        """Find the most recent node of a given type in the stack."""
        return next(
            (
                node
                for node in reversed(self._node_stack)
                if isinstance(node, node_type)
            ),
            None,
        )

    def find_function_node(self) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
        """Finds the last function node under the cursor position."""
        return self._find_last_of_type((ast.FunctionDef, ast.AsyncFunctionDef))

    def find_class_node(self) -> ast.ClassDef | None:
        """Finds the last class node under the cursor position."""
        return self._find_last_of_type(ast.ClassDef)

    def find_module_node(self) -> ast.Module | None:
        """Finds the module node."""
        return self._find_last_of_type(ast.Module)

    def get_current_context(
        self,
    ) -> ContextNodes | None:
        """Get the most recent node in the stack."""
        return self._node_stack[-1] if self._node_stack else None


class AstEntity(CodeEntity):
    """Represents a code entity of a source code analyzed with `ast`."""

    def __init__(self, source_code: str, node: ContextNodes) -> None:
        self._document_source_code = source_code
        self._node = node

    @property
    def code_lines(self) -> list[str]:
        """Returns the source code of the code entity split into lines."""
        return self.code.splitlines()

    @property
    def docstring_range(self) -> DocumentRange | None:
        """Returns the start and end positions of the code entity docstring in code."""
        if not (self._node.body and isinstance(self._node.body[0], ast.Expr)):
            return None
        node = self._node.body[0].value
        node = ensure_node_has_location(node)
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            return None
        return DocumentRange(
            Position(node.lineno, node.col_offset),
            Position(node.end_lineno, node.end_col_offset),
        )


class AstNamedEntity(AstEntity, NamedCodeEntity):
    """Represents either a function or a class of a source code analyzed with `ast`."""

    def __init__(self, source_code: str, node: NamedNodes) -> None:
        super().__init__(source_code, node)
        self._node = ensure_named_node_has_location(node)

    @property
    def code(self) -> str:
        """Returns the source code of the code entity as a string."""
        return get_source_segment(self._document_source_code, self._node, padded=True)

    @property
    def name(self) -> str:
        """Returns the code entity name."""
        return self._node.name

    @property
    def code_range(self) -> DocumentRange:
        """Returns the start and end positions of the code entity in the source code."""
        return DocumentRange(
            DocumentPosition(self._node.lineno, self._node.col_offset),
            DocumentPosition(self._node.end_lineno, self._node.end_col_offset),
        )

    @property
    def signature_end(self) -> DocumentPosition:
        """Returns the end position of the code entity signature in the source code."""
        # Extract the starting position of the code entity body.
        entity_body = Position(self._node.body[0].lineno, self._node.body[0].col_offset)
        # Extract the code entity header lines up to the body.
        entity_header = self.code_lines[
            0 : entity_body.line - self.code_range.start.line + 1
        ]
        # Trim the last header line to the position where the code entity body begins.
        entity_header[-1] = entity_header[-1][: entity_body.character]

        # Attempt to find the last colon in the code entity header.
        if colons := _find_colon_tokens(entity_header):
            last_colon = colons[-1]
            colon_line = last_colon.end[0] - 1  # Convert to 0-based line index.
            colon_character = last_colon.end[1]
            # Calculate the end position of the code entity signature
            # based on the colon’s position.
            signature_end = DocumentPosition(
                colon_line + self.code_range.start.line,
                colon_character,
            )
            # Check if the line after the colon contains a comment.
            if re.match(r"^\s*#", entity_header[colon_line][colon_character:]):
                # If there's a comment, adjust character position
                # to the end of the line.
                signature_end = DocumentPosition(
                    signature_end.line, len(entity_header[colon_line])
                )
        else:
            # Raise an exception if no colon is found.
            raise Exception("Colon not found or invalid syntax.")
        return signature_end


class AstFunction(AstNamedEntity, BaseFunction):
    """Represents a function of a source code analyzed with `ast`."""


class AstClass(AstNamedEntity, BaseClass):
    """Represents a class of a source code analyzed with `ast`."""


class AstModule(AstEntity, BaseModule):
    """Represents a module of a source code analyzed with `ast`."""

    @property
    def code(self) -> str:
        """Returns the source code of the module as a string."""
        return self._document_source_code


@AnalyzerFactory.register_analyzer("ast")
class AstAnalyzer(BaseAnalyzer):
    """Analyzer that uses `ast` for analyzing Python code."""

    NODE_ENTITY_MAP = {
        ast.FunctionDef: AstFunction,
        ast.AsyncFunctionDef: AstFunction,
        ast.ClassDef: AstClass,
        ast.Module: AstModule,
    }
    context_resolver_cls = ASTContextResolver

    def __init__(
        self,
        *args,
        context_resolver_cls: type[IASTContextResolver] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if context_resolver_cls is not None:
            self.context_resolver_cls = context_resolver_cls
        self._tree = ast.parse(self._source_code)

    def get_context(self, cursor: IPosition) -> AstEntity | None:
        """Returns the code entity under the cursor."""
        resolver = self.context_resolver_cls(cursor, self._tree)
        context_node = resolver.get_current_context()
        for node_type, entity_cls in self.NODE_ENTITY_MAP.items():
            if isinstance(context_node, node_type):
                return entity_cls(self._source_code, context_node)
        return None

    def get_function(self, cursor: IPosition) -> AstFunction | None:
        """Returns the function entity under the cursor."""
        resolver = self.context_resolver_cls(cursor, self._tree)
        node = resolver.find_function_node()
        return AstFunction(self._source_code, node) if node else None

    def get_class(self, cursor: IPosition) -> AstClass | None:
        """Returns the class entity under the cursor."""
        resolver = self.context_resolver_cls(cursor, self._tree)
        node = resolver.find_class_node()
        return AstClass(self._source_code, node) if node else None

    def get_module(self, cursor: IPosition) -> AstModule | None:
        """Returns the module entity under the cursor."""
        resolver = self.context_resolver_cls(cursor, self._tree)
        node = resolver.find_module_node()
        return AstModule(self._source_code, node) if node else None
