from __future__ import annotations

import os
import sys
from pathlib import Path

from pygls import uris, workspace

SERVER_NAME = "chatgpt-docstrings"
SERVER_VERSION = "0.1"
ALLOWED_PROXY_PROTOCOLS = ("http", "https", "socks5", "socks5h")


class GlobalSettings(dict):
    """Represents VSCode global settings."""

    def __init__(self, settings: dict) -> None:
        super().__init__()
        self.update(**settings)
        self.setdefault("interpreter", [sys.executable])


class WorkspaceSettings(dict):
    """Represents VSCode workspace settings."""

    def __init__(self, settings: list[dict], global_settings: GlobalSettings) -> None:
        super().__init__()
        self.global_settings = global_settings
        if settings:
            self._load_workspace_settings(settings)
        else:
            self._set_default_workspace()

    def _load_workspace_settings(self, settings: list[dict]) -> None:
        """Loads settings for each workspace from the provided list."""
        for setting in settings:
            workspace_path = uris.to_fs_path(setting["workspace"])
            self[workspace_path] = {
                **setting,
                "workspaceFS": workspace_path,
            }

    def _set_default_workspace(self) -> None:
        """Sets up default workspace configuration if no settings are provided."""
        cur_dir = os.getcwd()
        self[cur_dir] = self._create_workspace_settings(cur_dir)

    def _create_workspace_settings(self, path: str) -> dict:
        """Creates workspace settings based on the given directory path."""
        return {
            "cwd": path,
            "workspaceFS": path,
            "workspace": uris.from_fs_path(path),
            **self.global_settings,
        }

    def get_settings_for_document(self, document: workspace.Document | None) -> dict:
        """Returns the settings associated with the given document.

        If the document is not part of a workspace,
        returns settings based on global settings.
        """
        if document is None or document.path is None:
            return list(self.values())[0]

        if workspace_key := self._find_workspace_key_for_document(document):
            return self[workspace_key]

        # This is either a non-workspace file or there is no workspace.
        file_path = os.fspath(Path(document.path).parent)
        return self._create_workspace_settings(file_path)

    def _find_workspace_key_for_document(
        self, document: workspace.Document
    ) -> str | None:
        """Find workspace settings for the given document."""
        document_path = Path(document.path)
        workspace_paths = {s["workspaceFS"] for s in self.values()}
        while document_path != document_path.parent:
            if str(document_path) in workspace_paths:
                return str(document_path)
            document_path = document_path.parent
        return None

    def get_settings_for_file(self, file_path: Path) -> dict:
        """Returns the settings for a file based on its path.

        If the file path belongs to a workspace,
        the settings for that workspace are returned.
        """
        workspace_paths = {s["workspaceFS"] for s in self.values()}
        while file_path != file_path.parent:
            if str(file_path) in workspace_paths:
                return self[str(file_path)]
            file_path = file_path.parent
        return list(self.values())[0]
