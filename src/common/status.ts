// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import { Disposable, LanguageStatusItem, LanguageStatusSeverity } from 'vscode';
import { Command } from 'vscode-languageclient';
import { getDocumentSelector } from './utilities';
import { createLanguageStatusItem } from './vscodeapi';

let _status: LanguageStatusItem | undefined;
export function registerLanguageStatusItem(id: string, name: string, command: string): Disposable {
    _status = createLanguageStatusItem(id, getDocumentSelector());
    _status.name = name;
    _status.text = name;
    _status.command = Command.create('Show logs', command);

    return {
        dispose: () => {
            _status?.dispose();
            _status = undefined;
        },
    };
}

export function updateStatus(
    status: string | undefined,
    severity: LanguageStatusSeverity,
    busy?: boolean,
    detail?: string,
): void {
    if (_status) {
        _status.text = status && status.length > 0 ? `${_status.name}: ${status}` : `${_status.name}`;
        _status.severity = severity;
        _status.busy = busy ?? false;
        _status.detail = detail;
    }
}

export function getStatus(): LanguageStatusItem | undefined {
    return _status;
}
