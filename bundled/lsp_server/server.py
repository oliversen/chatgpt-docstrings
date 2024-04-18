from __future__ import annotations

from typing import Any, Optional

import lsprotocol.types as lsp
from pygls import server

from custom_types import TelemetryParams, TelemetryTypes
from progress import Progress, ProgressHundlers
from settings import MAX_WORKERS, SERVER_NAME, SERVER_VER


class LanguageServer(server.LanguageServer):
    def __init__(self, *args: Optional[Any], **kwargs: Optional[Any]) -> None:
        super().__init__(*args, **kwargs)
        self.lsp.progress_handlers = ProgressHundlers()
        self.lsp.fm.add_builtin_feature(
            lsp.WINDOW_WORK_DONE_PROGRESS_CANCEL, self.progress_cancel
        )

    def progress(self, *args: Optional[Any], **kwargs: Optional[Any]) -> Progress:
        return Progress(self.lsp, *args, **kwargs)

    def progress_cancel(
        ls: server.LanguageServer, params: lsp.WorkDoneProgressCancelParams
    ) -> None:
        ls.lsp.progress_handlers.get(params.token).cancel()

    def apply_edit_async(
        self, edit: lsp.WorkspaceEdit, label: Optional[str] = None
    ) -> lsp.WorkspaceApplyEditResponse:
        """Sends apply edit request to the client. Should be called with `await`"""
        return self.lsp.send_request_async(
            lsp.WORKSPACE_APPLY_EDIT,
            lsp.ApplyWorkspaceEditParams(edit=edit, label=label),
        )

    def _send_telemetry(self, params: TelemetryParams) -> None:
        self.send_notification(lsp.TELEMETRY_EVENT, params)

    def send_telemetry_info(self, name: str, data: dict[str, str]) -> None:
        params = TelemetryParams(TelemetryTypes.Info, name, data)
        self._send_telemetry(params)

    def send_telemetry_error(self, name: str, data: dict[str, str]) -> None:
        params = TelemetryParams(TelemetryTypes.Error, name, data)
        self._send_telemetry(params)


LSP_SERVER = LanguageServer(
    name=SERVER_NAME, version=SERVER_VER, max_workers=MAX_WORKERS
)
