// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import * as fs from 'fs-extra';
import * as path from 'path';
import { Uri, WorkspaceFolder } from 'vscode';
import { DocumentSelector } from 'vscode-languageclient';
import { EXTENSION_ROOT_DIR } from './constants';
import { getWorkspaceFolders, isVirtualWorkspace } from './vscodeapi';

export interface IServerInfo {
    name: string;
    module: string;
}

export function loadServerDefaults(): IServerInfo {
    const packageJson = path.join(EXTENSION_ROOT_DIR, 'package.json');
    const content = fs.readFileSync(packageJson).toString();
    const config = JSON.parse(content);
    return config.serverInfo as IServerInfo;
}

export async function getProjectRoot(): Promise<WorkspaceFolder> {
    const workspaces: readonly WorkspaceFolder[] = getWorkspaceFolders();
    if (workspaces.length === 0) {
        return {
            uri: Uri.file(process.cwd()),
            name: path.basename(process.cwd()),
            index: 0,
        };
    } else if (workspaces.length === 1) {
        return workspaces[0];
    } else {
        let rootWorkspace = workspaces[0];
        let root = undefined;
        for (const w of workspaces) {
            if (await fs.pathExists(w.uri.fsPath)) {
                root = w.uri.fsPath;
                rootWorkspace = w;
                break;
            }
        }

        for (const w of workspaces) {
            if (root && root.length > w.uri.fsPath.length && (await fs.pathExists(w.uri.fsPath))) {
                root = w.uri.fsPath;
                rootWorkspace = w;
            }
        }
        return rootWorkspace;
    }
}

export function getDocumentSelector(): DocumentSelector {
    // virtual workspaces are not supported yet
    return isVirtualWorkspace()
        ? [{ language: 'python' }]
        : [
              { scheme: 'file', language: 'python' },
              { scheme: 'untitled', language: 'python' },
              { scheme: 'vscode-notebook', language: 'python' },
              { scheme: 'vscode-notebook-cell', language: 'python' },
          ];
}

export class AsyncLock {
    private isLocked: boolean = false;
    private waitingQueue: (() => void)[] = [];
    private isWaiting: boolean = false;

    async lock(): Promise<void> {
        return new Promise<void>((resolve) => {
            const tryLock = () => {
                if (!this.isLocked) {
                    this.isLocked = true;
                    resolve();
                } else if (!this.isWaiting) {
                    this.isWaiting = true;
                    this.waitingQueue.push(tryLock);
                }
            };
            tryLock();
        });
    }

    unlock(): void {
        this.isLocked = false;
        this.isWaiting = false;
        if (this.waitingQueue.length > 0) {
            const next = this.waitingQueue.shift();
            if (next) next();
        }
    }

    async *[Symbol.asyncIterator]() {
        await this.lock();
        try {
            yield;
        } finally {
            this.unlock();
        }
    }
}
