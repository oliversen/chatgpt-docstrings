from __future__ import annotations

import re
from typing import Iterable

import lsprotocol.types as lsp
from pygls.workspace import TextDocument

import server
from utils import get_entity_at_cursor, mark_as_feature
from utils.code_analyzers.base import CodeEntity, NamedCodeEntity


@mark_as_feature(
    lsp.TEXT_DOCUMENT_COMPLETION, lsp.CompletionOptions(trigger_characters=['"'])
)
def completions(
    ls: server.DocstringLanguageServer, params: lsp.CompletionParams
) -> None | lsp.CompletionList:
    """Returns completion items for docstring generation."""
    cursor = params.position
    uri = params.text_document.uri
    document = ls.workspace.get_document(uri)
    settings = ls.workspace_settings.get_settings_for_document(document)

    if not _cursor_after_quotes(document, cursor):
        return None

    if settings["codeAnalyzer"] == "ast":
        code_entity = _get_entity_using_ast(ls, document, cursor)
    else:
        code_entity = get_entity_at_cursor(
            document.source, cursor, settings["codeAnalyzer"]
        )

    if (
        not code_entity
        or not isinstance(code_entity, NamedCodeEntity)
        or cursor.line != code_entity.signature_end.to_lsp().line + 1
    ):
        return None

    completion_text = (
        "" if code_entity.docstring_range else 'Await docstring generation..."""'
    )
    return _create_completion_list(cursor, completion_text)


def _remove_line_from_source(document: TextDocument, line_to_remove: int) -> str:
    """Remove a specific line from the document source."""
    lines = document.lines[:]
    del lines[line_to_remove]
    return "".join(lines)


def _sources_for_ast_analysis(
    document: TextDocument, cursor: lsp.Position
) -> Iterable[str]:
    """Yields the source code and the source code without the current line."""
    yield document.source
    yield _remove_line_from_source(document, cursor.line)


def _get_entity_using_ast(
    ls: server.DocstringLanguageServer, document: TextDocument, cursor: lsp.Position
) -> CodeEntity | None:
    """Tries to analyze the code using `ast`.

    If the triple quotes are not closed, a syntax error occurs.
    We remove the line with the opening quotes and repeat the code analysis.
    """
    for source in _sources_for_ast_analysis(document, cursor):
        try:
            return get_entity_at_cursor(source, cursor, "ast")
        except SyntaxError:
            continue
    else:
        ls.show_warning("The source code contains a syntax error.")
    return None


def _cursor_after_quotes(document: TextDocument, cursor: lsp.Position) -> bool:
    """Checks if the cursor is positioned after an opening triple quote."""
    line_before_cursor = document.lines[cursor.line][0 : cursor.character]
    return bool(re.match(r'^(\s{4})+"""$', line_before_cursor))


def _create_completion_list(
    cursor: lsp.Position, completion_text: str
) -> lsp.CompletionList:
    """Creates a CompletionList containing the provided completion text."""
    return lsp.CompletionList(
        is_incomplete=False,
        items=[
            lsp.CompletionItem(
                label="Generate Docstring (ChatGPT)",
                kind=lsp.CompletionItemKind.Text,
                text_edit=lsp.TextEdit(
                    range=lsp.Range(start=cursor, end=cursor),
                    new_text=completion_text,
                ),
                command=lsp.Command(
                    title="Generate Docstring (ChatGPT)",
                    command="chatgpt-docstrings.generateDocstring",
                ),
            ),
        ],
    )
