from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import asdict, dataclass, field
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, Callable
from unittest.mock import Mock

import pytest
from lsprotocol import types as lsp
from pygls import uris
from pygls.lsp.client import BaseLanguageClient
from pytest_asyncio import fixture as async_fixture

from language_server.commands import (
    CommandArguments,
    Position,
    TextDocument,
    TextDocumentPosition,
)

# marks all test coroutines in this module
pytestmark = pytest.mark.asyncio(loop_scope="session")

async_session_fixture = partial(async_fixture, scope="session", loop_scope="session")

REPO_DIR = Path(__file__, "..", "..").resolve()
TESTS_DIR = REPO_DIR / "tests"
ASSERTS_DIR = WORKSPACE_DIR = TESTS_DIR / "asserts"
SERVER_DIR = REPO_DIR / "language_server"
SERVER_LIBS_DIR = SERVER_DIR / "libs"
ROOT_URI = uris.from_fs_path(str(WORKSPACE_DIR))
WORKSPACE_FILE_URI = uris.from_fs_path(str(WORKSPACE_DIR / "workspace_file_sample.py"))

assert ROOT_URI
assert WORKSPACE_FILE_URI


@dataclass
class ProxySettings:
    url: str = ""
    authorization: str = ""
    strictSSL: bool = False


@dataclass
class GlobalSettings:
    cwd: str = str(REPO_DIR)
    workspace: str = str(REPO_DIR)
    interpreter: list[str] = field(default_factory=list)
    baseUrl: str = "https://api.openai.com/v1"
    aiModel: str = "gpt-4o-mini"
    docstringStyle: str = "google"
    onNewLine: bool = False
    promptPattern: str = (
        "Generate a {docstring_style}-style docstring "
        "for the following Python {entity} code:\n{code}"
    )
    requestTimeout: int = 15
    showProgressNotification: bool = True
    proxy: ProxySettings = field(default_factory=ProxySettings)


@dataclass
class WorkspaceSettings(GlobalSettings):
    cwd: str = str(WORKSPACE_DIR)
    workspace: str = ROOT_URI
    interpreter: list[str] = field(default_factory=lambda: [sys.executable])


INITIALIZATION_OPTIONS = {
    "settings": [asdict(WorkspaceSettings())],
    "globalSettings": asdict(GlobalSettings()),
}


def wrap_in_mock(function: Callable) -> Mock:
    """Wraps the given function in a mock object using unittest.mock.Mock."""
    function = Mock(wraps=function)
    return function


class LanguageClient(BaseLanguageClient):
    """Language client to use for testing."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.feature("workspace/applyEdit")(self.apply_edit)

    @staticmethod
    @wrap_in_mock
    def apply_edit(
        params: lsp.ApplyWorkspaceEditParams,
    ) -> lsp.ApplyWorkspaceEditResult:
        return lsp.ApplyWorkspaceEditResult(applied=True)

    async def server_exit(self, server: asyncio.subprocess.Process) -> None:
        # -15: terminated (probably by the client)
        #   0: all ok
        if (
            server.returncode not in {-15, 0}
            and server.stderr
            and (err := await server.stderr.read())
        ):
            print(f"stderr: {err.decode('utf8')}", file=sys.stderr)


@async_session_fixture
async def client() -> AsyncGenerator[LanguageClient, None]:
    server_env = {**os.environ, "PYTHONPATH": str(SERVER_LIBS_DIR)}
    server_cmd = [sys.executable, str(SERVER_DIR / "_start.py")]
    client = LanguageClient("pygls-test-suite", "v1")
    await client.start_io(*server_cmd, env=server_env)
    yield client
    await client.shutdown_async(None)
    client.exit(None)
    await client.stop()


@async_session_fixture(autouse=True)
async def initialize_result(client: LanguageClient) -> lsp.InitializeResult:
    initialize_result = await client.initialize_async(
        lsp.InitializeParams(
            capabilities=lsp.ClientCapabilities(),
            initialization_options=INITIALIZATION_OPTIONS,
            root_uri=ROOT_URI,
        )
    )
    assert initialize_result is not None
    return initialize_result


async def test_completion_support(
    initialize_result: lsp.InitializeResult,
) -> None:
    completion_provider = initialize_result.capabilities.completion_provider
    assert completion_provider
    assert completion_provider.trigger_characters == ['"']


@pytest.mark.parametrize("cursor", [(1, 7), (16, 7), (20, 7)])
async def test_with_completion_items(
    client: LanguageClient, cursor: tuple[int, int]
) -> None:
    response = await client.text_document_completion_async(
        lsp.CompletionParams(
            text_document=lsp.TextDocumentIdentifier(uri=WORKSPACE_FILE_URI),
            position=lsp.Position(line=cursor[0], character=cursor[1]),
        )
    )
    assert isinstance(response, lsp.CompletionList)
    assert len(response.items) == 1
    assert response.items[0].command
    assert response.items[0].command.command == "chatgpt-docstrings.generateDocstring"


@pytest.mark.parametrize("cursor", [(8, 7), (12, 13)])
async def test_without_completion_items(
    client: LanguageClient, cursor: tuple[int, int]
) -> None:
    response = await client.text_document_completion_async(
        lsp.CompletionParams(
            text_document=lsp.TextDocumentIdentifier(uri=WORKSPACE_FILE_URI),
            position=lsp.Position(line=cursor[0], character=cursor[1]),
        )
    )
    assert response is None


async def test_generate_docstring_command(
    client: LanguageClient, initialize_result: lsp.InitializeResult
) -> None:
    command_name = "chatgpt-docstrings.applyGenerate"
    command_arguments = CommandArguments(
        text_document_position=TextDocumentPosition(
            textDocument=TextDocument(uri=WORKSPACE_FILE_URI),
            position=Position(line=16, character=7),
        ),
        api_key="",
        progress_token=1,
    )

    # Check that the command has been registered by the server
    assert initialize_result.capabilities.execute_command_provider
    assert initialize_result.capabilities.execute_command_provider.commands == [
        command_name
    ]

    # Exetute the command
    response = await client.workspace_execute_command_async(
        lsp.ExecuteCommandParams(
            command=command_name,
            arguments=list(command_arguments),
        )
    )
    assert response

    # Check that 'workspace/applyEdit' request was executed correctly
    assert client.apply_edit.call_count == 1
    apply_edit_params = client.apply_edit.call_args.args[0]
    document_changes = apply_edit_params.edit.document_changes
    assert len(document_changes) == 1
    edits = document_changes[0].edits
    assert len(edits) == 2
    remove_docstring, add_docstring = edits
    assert str(remove_docstring.range) == "16:0-17:0"
    assert remove_docstring.new_text == ""
    assert str(add_docstring.range) == "16:0-16:0"
    assert add_docstring.new_text == '    """docstring"""\n'
