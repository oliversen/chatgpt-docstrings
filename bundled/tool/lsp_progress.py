from typing import Union

from lsprotocol.types import (
    PROGRESS,
    ProgressParams,
    WorkDoneProgressReport,
)
from pygls.protocol import LanguageServerProtocol


class Progress:
    def __init__(self, lsp: LanguageServerProtocol, token: str) -> None:
        self._lsp = lsp
        self._token = token
        self._cancelled = False

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def cancel(self):
        self._cancelled = True

    def report(self, message: str):
        value = WorkDoneProgressReport(message=message)
        self._lsp.notify(PROGRESS, ProgressParams(token=self._token, value=value))

    def __enter__(self):
        self._lsp.progress_handlers.add(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._lsp.progress_handlers.remove(self)

    def __eq__(self, __value: object) -> bool:
        return self._token == __value._token


class ProgressHundlers:
    def __init__(self) -> None:
        self._hundlers = []

    def _has(self, hundler: Progress) -> bool:
        for h in self._hundlers:
            if h == hundler:
                return True
        return False

    def add(self, hundler: Progress) -> None:
        if not self._has(hundler):
            self._hundlers.append(hundler)

    def get(self, progress_token: str) -> Union[Progress, None]:
        for hundler in self._hundlers:
            if hundler._token == progress_token:
                return hundler
        return None

    def remove(self, hundler: Progress) -> None:
        self._hundlers.remove(hundler)
