// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import { PythonExtension, ResolvedEnvironment } from '@vscode/python-extension';
import * as fsapi from 'fs-extra';
import { Disposable, Event, EventEmitter, LanguageStatusSeverity, Uri, commands } from 'vscode';
import { traceError, traceLog, traceVerbose, traceWarn } from './logging';
import { getInterpreterFromSetting } from './settings';
import { updateStatus } from './status';

export interface IInterpreterDetails {
    path?: string[];
    resource?: Uri;
}

const onDidChangePythonInterpreterEvent = new EventEmitter<IInterpreterDetails>();
export const onDidChangePythonInterpreter: Event<IInterpreterDetails> = onDidChangePythonInterpreterEvent.event;

let _api: PythonExtension | undefined;
async function getPythonExtensionAPI(): Promise<PythonExtension | undefined> {
    if (_api) {
        return _api;
    }
    _api = await PythonExtension.api();
    return _api;
}

export async function initializePython(disposables: Disposable[]): Promise<void> {
    try {
        const api = await getPythonExtensionAPI();

        if (api) {
            disposables.push(
                api.environments.onDidChangeActiveEnvironmentPath((e) => {
                    onDidChangePythonInterpreterEvent.fire({ path: [e.path], resource: e.resource?.uri });
                }),
            );

            traceLog('Waiting for interpreter from python extension.');
            onDidChangePythonInterpreterEvent.fire(await getInterpreterDetails());
        }
    } catch (error) {
        traceError('Error initializing python: ', error);
    }
}

export async function resolveInterpreter(interpreter: string[]): Promise<ResolvedEnvironment | undefined> {
    const api = await getPythonExtensionAPI();
    return api?.environments.resolveEnvironment(interpreter[0]);
}

export async function getInterpreterDetails(resource?: Uri): Promise<IInterpreterDetails> {
    const api = await getPythonExtensionAPI();
    const environment = await api?.environments.resolveEnvironment(
        api?.environments.getActiveEnvironmentPath(resource),
    );
    if (environment?.executable.uri && checkVersion(environment)) {
        return { path: [environment?.executable.uri.fsPath], resource };
    }
    return { path: undefined, resource };
}

export async function getDebuggerPath(): Promise<string | undefined> {
    const api = await getPythonExtensionAPI();
    return api?.debug.getDebuggerPackagePath();
}

export async function runPythonExtensionCommand(command: string, ...rest: any[]) {
    await getPythonExtensionAPI();
    return await commands.executeCommand(command, ...rest);
}

export function checkVersion(resolved: ResolvedEnvironment | undefined): boolean {
    const version = resolved?.version;
    if (version?.major === 3 && version?.minor >= 9) {
        return true;
    }
    return false;
}

export async function checkInterpreter(serverId: string): Promise<boolean> {
    const interpreter = getInterpreterFromSetting(serverId);

    // Check if interpreter is set in the settings
    if (interpreter && interpreter.length > 0) {
        const interpreterPath = interpreter[0];
        if (!(await fsapi.pathExists(interpreterPath))) {
            const msg = `The interpreter set in "${serverId}.interpreter" setting was not found.`;
            traceWarn(msg);
            updateStatus(msg, LanguageStatusSeverity.Warning);
            return false;
        }

        const resolvedInterpreter = await resolveInterpreter(interpreter);
        if (!checkVersion(resolvedInterpreter)) {
            const msg = `The interpreter set in "${serverId}.interpreter" setting is not supported. Please use Python 3.9 or greater.`;
            traceWarn(msg);
            updateStatus(msg, LanguageStatusSeverity.Warning);
            return false;
        }

        traceVerbose(`Using interpreter from ${serverId}.interpreter: ${interpreter[0]}`);
        return true;
    }

    // Check if the interpreter is available from the Python extension
    const interpreterDetails = await getInterpreterDetails();
    if (interpreterDetails.path) {
        traceVerbose(`Using interpreter from Python extension: ${interpreterDetails.path.join(' ')}`);
        return true;
    }

    // Warning about the need to select the Python interpreter.
    const msg = `Select the python interpreter version 3.9 or greater in the status bar, or set it in the "${serverId}.interpreter" setting.`;
    traceWarn(msg);
    updateStatus(msg, LanguageStatusSeverity.Warning);
    return false;
}
