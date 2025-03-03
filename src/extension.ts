import * as vscode from 'vscode';
import { ApiKey } from './common/api-key';
import { generateDocstring } from './common/generate-docstring';
import { getLSClientTraceLevel, registerLogger, traceLog, traceVerbose } from './common/logging';
import { initializePython, onDidChangePythonInterpreter } from './common/python';
import { ServerManager } from './common/server';
import { checkIfConfigurationChanged, getInterpreterFromSetting } from './common/settings';
import { registerLanguageStatusItem } from './common/status';
import { telemetryReporter } from './common/telemetry';
import { loadServerDefaults } from './common/utilities';
import { createOutputChannel, onDidChangeConfiguration, registerCommand } from './common/vscodeapi';

let serverManager: ServerManager;

export async function activate(context: vscode.ExtensionContext): Promise<void> {
    const serverInfo = loadServerDefaults();
    const serverName = serverInfo.name;
    const serverId = serverInfo.module;

    // Setup telemetry
    context.subscriptions.push(telemetryReporter);

    // Setup logging
    const outputChannel = createOutputChannel(serverName);
    context.subscriptions.push(outputChannel, registerLogger(outputChannel));

    const changeLogLevel = async (c: vscode.LogLevel, g: vscode.LogLevel) => {
        const level = getLSClientTraceLevel(c, g);
        await serverManager.lsClient?.setTrace(level);
    };

    context.subscriptions.push(
        outputChannel.onDidChangeLogLevel(async (e) => {
            await changeLogLevel(e, vscode.env.logLevel);
        }),
        vscode.env.onDidChangeLogLevel(async (e) => {
            await changeLogLevel(outputChannel.logLevel, e);
        }),
    );

    // Log Server information
    traceLog(`Name: ${serverInfo.name}`);
    traceLog(`Module: ${serverInfo.module}`);
    traceVerbose(`Full Server Info: ${JSON.stringify(serverInfo)}`);

    serverManager = new ServerManager(serverId, serverName, outputChannel);

    context.subscriptions.push(
        onDidChangePythonInterpreter(async () => {
            serverManager.restartServer();
        }),
        onDidChangeConfiguration(async (e: vscode.ConfigurationChangeEvent) => {
            if (!checkIfConfigurationChanged(e, serverId)) return;
            serverManager.restartServer();
        }),
        registerCommand(`${serverId}.restart`, async () => {
            serverManager.restartServer();
        }),
        registerCommand(`${serverId}.showLogs`, async () => {
            outputChannel.show();
        }),
        registerCommand(`${serverId}.setApiKey`, () => {
            new ApiKey(outputChannel, context.secrets).set();
        }),
        registerCommand(`${serverId}.generateDocstring`, () => {
            generateDocstring(serverId, serverManager.lsClient, context.secrets);
        }),
        registerLanguageStatusItem(serverId, serverName, `${serverId}.showLogs`),
    );

    setImmediate(async () => {
        const interpreter = getInterpreterFromSetting(serverId);
        if (interpreter === undefined || interpreter.length === 0) {
            traceLog(`Python extension loading`);
            await initializePython(context.subscriptions);
            traceLog(`Python extension loaded`);
        } else {
            serverManager.restartServer();
        }
    });
}

export async function deactivate(): Promise<void> {
    if (!serverManager.lsClient) return;
    await serverManager.lsClient.stop();
}
