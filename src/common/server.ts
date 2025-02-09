// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import * as fsapi from 'fs-extra';
import { Disposable, env, LogOutputChannel, LanguageStatusSeverity } from 'vscode';
import { State } from 'vscode-languageclient';
import {
    LanguageClient,
    LanguageClientOptions,
    RevealOutputChannelOn,
    ServerOptions,
} from 'vscode-languageclient/node';
import { SERVER_DEBUG_SCRIPT_PATH, SERVER_START_SCRIPT_PATH, SERVER_LIBS_PATH } from './constants';
import { traceError, traceWarn, traceInfo, traceVerbose } from './log/logging';
import { getDebuggerPath, checkVersion, resolveInterpreter, getInterpreterDetails } from './python';
import {
    getExtensionSettings,
    getGlobalSettings,
    getWorkspaceSettings,
    ISettings,
    getInterpreterFromSetting,
} from './settings';
import { getLSClientTraceLevel, getProjectRoot } from './utilities';
import { isVirtualWorkspace } from './vscodeapi';
import { telemetryReporter } from './telemetry';
import { updateStatus } from './status';

export type IInitOptions = { settings: ISettings[]; globalSettings: ISettings };

async function checkInterpreter(serverId: string): Promise<boolean> {
    const interpreter = getInterpreterFromSetting(serverId);
    if (interpreter && interpreter.length > 0) {
        if (!(await fsapi.pathExists(interpreter[0]))) {
            const msg = `The interpreter set in "${serverId}.interpreter" setting was not found.`;
            traceWarn(msg);
            updateStatus(msg, LanguageStatusSeverity.Warning);
            return false;
        }
        if (!checkVersion(await resolveInterpreter(interpreter))) {
            const msg = `The interpreter set in "${serverId}.interpreter" setting is not supported. Please use Python 3.8 or greater.`;
            traceWarn(msg);
            updateStatus(msg, LanguageStatusSeverity.Warning);
            return false;
        }
        traceVerbose(`Using interpreter from ${serverId}.interpreter: ${interpreter[0]}`);
        return true;
    }

    const interpreterDetails = await getInterpreterDetails();
    if (interpreterDetails.path) {
        traceVerbose(`Using interpreter from Python extension: ${interpreterDetails.path.join(' ')}`);
        return true;
    }

    const msg = `Select the python interpreter version 3.8 or greater in the status bar, or set it in the "${serverId}.interpreter" setting.`;
    traceWarn(msg);
    updateStatus(msg, LanguageStatusSeverity.Warning);
    return false;
}

async function createServer(
    settings: ISettings,
    serverId: string,
    serverName: string,
    outputChannel: LogOutputChannel,
    initializationOptions: IInitOptions,
): Promise<LanguageClient> {
    const command = settings.interpreter[0];
    const cwd = settings.cwd;

    // Set debugger path needed for debugging python code.
    const newEnv = { ...process.env };
    const debuggerPath = await getDebuggerPath();
    const isDebugScript = await fsapi.pathExists(SERVER_DEBUG_SCRIPT_PATH);
    if (newEnv.USE_DEBUGPY && debuggerPath) {
        newEnv.DEBUGPY_PATH = debuggerPath;
    } else {
        newEnv.USE_DEBUGPY = 'False';
    }

    newEnv.PYTHONPATH = SERVER_LIBS_PATH;

    const args =
        newEnv.USE_DEBUGPY === 'False' || !isDebugScript
            ? settings.interpreter.slice(1).concat([SERVER_START_SCRIPT_PATH])
            : settings.interpreter.slice(1).concat([SERVER_DEBUG_SCRIPT_PATH]);
    traceInfo(`Server run command: ${[command, ...args].join(' ')}`);

    const serverOptions: ServerOptions = {
        command,
        args,
        options: { cwd, env: newEnv },
    };

    // Options to control the language client
    const clientOptions: LanguageClientOptions = {
        // Register the server for python documents
        documentSelector: isVirtualWorkspace()
            ? [{ language: 'python' }]
            : [
                  { scheme: 'file', language: 'python' },
                  { scheme: 'untitled', language: 'python' },
                  { scheme: 'vscode-notebook', language: 'python' },
                  { scheme: 'vscode-notebook-cell', language: 'python' },
              ],
        outputChannel: outputChannel,
        traceOutputChannel: outputChannel,
        revealOutputChannelOn: RevealOutputChannelOn.Never,
        connectionOptions: { maxRestartCount: 0 },
        initializationOptions,
    };

    return new LanguageClient(serverId, serverName, serverOptions, clientOptions);
}

let _disposables: Disposable[] = [];
export async function restartServer(
    serverId: string,
    serverName: string,
    outputChannel: LogOutputChannel,
    lsClient?: LanguageClient,
): Promise<LanguageClient | undefined> {
    if (lsClient) {
        traceInfo(`Server: Stop requested`);
        await lsClient.stop();
        _disposables.forEach((d) => d.dispose());
        _disposables = [];
    }
    if (!(await checkInterpreter(serverId))) {
        return undefined;
    }
    const projectRoot = await getProjectRoot();
    const workspaceSetting = await getWorkspaceSettings(serverId, projectRoot, true);

    const newLSClient = await createServer(workspaceSetting, serverId, serverName, outputChannel, {
        settings: await getExtensionSettings(serverId, true),
        globalSettings: await getGlobalSettings(serverId, false),
    });
    traceInfo(`Server: Start requested.`);
    _disposables.push(
        newLSClient.onDidChangeState((e) => {
            switch (e.newState) {
                case State.Stopped:
                    traceVerbose(`Server State: Stopped`);
                    updateStatus('Server is stopped.', LanguageStatusSeverity.Warning, false);
                    break;
                case State.Starting:
                    traceVerbose(`Server State: Starting`);
                    updateStatus('Server is starting...', LanguageStatusSeverity.Information, true);
                    break;
                case State.Running:
                    traceVerbose(`Server State: Running`);
                    updateStatus(undefined, LanguageStatusSeverity.Information, false);
                    break;
            }
        }),
    );
    try {
        await newLSClient.start();
    } catch (ex) {
        traceError(`Server: Start failed: ${ex}`);
        updateStatus('Server failed to start.', LanguageStatusSeverity.Error);
        return undefined;
    }

    telemetryReporter.configureOnTelemetry(newLSClient);
    const level = getLSClientTraceLevel(outputChannel.logLevel, env.logLevel);
    await newLSClient.setTrace(level);
    return newLSClient;
}
