from __future__ import annotations

import re

import lsprotocol.types as lsp

import server
from utils import get_entity_at_cursor, mark_as_feature
from utils.code_analyzers.base import BaseFunction


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

    # Check if the cursor is positioned after an opening triple quote for a docstring
    line_before_cursor = document.lines[cursor.line][0 : cursor.character]
    if re.match(r'^(\s{4})+"""$', line_before_cursor):
        code_entity = get_entity_at_cursor(document.source, cursor)
        if (
            not code_entity
            or not isinstance(code_entity, BaseFunction)
            or cursor.line != code_entity.signature_end.line
        ):
            return None

        completion_text = (
            "" if code_entity.docstring_range else 'Await docstring generation..."""'
        )
        return _create_completion_list(cursor, completion_text)
    return None


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
