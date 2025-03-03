import * as fsapi from 'fs-extra';
import { Disposable, LanguageStatusSeverity, LogOutputChannel, env } from 'vscode';
import { State } from 'vscode-languageclient';
import {
    LanguageClient,
    LanguageClientOptions,
    RevealOutputChannelOn,
    ServerOptions,
} from 'vscode-languageclient/node';
import { SERVER_DEBUG_SCRIPT_PATH, SERVER_LIBS_PATH, SERVER_START_SCRIPT_PATH } from './constants';
import { getLSClientTraceLevel, traceError, traceInfo, traceVerbose } from './logging';
import { checkInterpreter, getDebuggerPath } from './python';
import { ISettings, getExtensionSettings, getGlobalSettings, getWorkspaceSettings } from './settings';
import { updateStatus } from './status';
import { telemetryReporter } from './telemetry';
import { AsyncLock, getDocumentSelector, getProjectRoot } from './utilities';

export class ServerManager {
    private disposables: Disposable[] = [];
    private restartLock = new AsyncLock();
    lsClient: LanguageClient | undefined;

    constructor(
        private serverId: string,
        private serverName: string,
        private outputChannel: LogOutputChannel,
    ) {}

    public async restartServer(): Promise<void> {
        for await (const _ of this.restartLock) {
            await this.stopServer();
            if (!(await checkInterpreter(this.serverId))) return;
            const newLSClient = await this.createServer();
            if (!(await this.startServer(newLSClient))) return;
            this.configureTelemetry(newLSClient);
            await this.configureTraceLevel(newLSClient, this.outputChannel);
            this.lsClient = newLSClient;
        }
    }

    private async stopServer(): Promise<void> {
        if (!this.lsClient) return;
        traceInfo(`Server: Stop requested`);
        await this.lsClient.stop();
        this.disposables.forEach((d) => d.dispose());
        this.disposables = [];
    }

    private async startServer(languageClient: LanguageClient): Promise<boolean> {
        try {
            traceInfo(`Server: Start requested.`);
            await languageClient.start();
            return true;
        } catch (error) {
            traceError(`Server: Start failed: ${error}`);
            updateStatus('Server failed to start.', LanguageStatusSeverity.Error);
            return false;
        }
    }

    private configureTelemetry(languageClient: LanguageClient): void {
        telemetryReporter.configureOnTelemetry(languageClient);
    }

    private async configureTraceLevel(languageClient: LanguageClient, outputChannel: LogOutputChannel): Promise<void> {
        const level = getLSClientTraceLevel(outputChannel.logLevel, env.logLevel);
        await languageClient.setTrace(level);
    }

    private async prepareEnvVars(): Promise<{ [key: string]: string | undefined }> {
        const newEnv = { ...process.env };
        const debuggerPath = await getDebuggerPath();
        if (newEnv.USE_DEBUGPY && debuggerPath) {
            newEnv.DEBUGPY_PATH = debuggerPath;
        } else {
            newEnv.USE_DEBUGPY = 'False';
        }
        newEnv.PYTHONPATH = SERVER_LIBS_PATH;
        return newEnv;
    }

    private constructServerArgs(
        settings: ISettings,
        environmentVariables: { [key: string]: string | undefined },
    ): string[] {
        const isDebugScript = environmentVariables.USE_DEBUGPY === 'True' && fsapi.pathExists(SERVER_DEBUG_SCRIPT_PATH);
        return isDebugScript
            ? settings.interpreter.slice(1).concat([SERVER_DEBUG_SCRIPT_PATH])
            : settings.interpreter.slice(1).concat([SERVER_START_SCRIPT_PATH]);
    }

    private handleServerStateChange(e: { newState: State }): void {
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
    }

    private async createServer(): Promise<LanguageClient> {
        const projectRoot = await getProjectRoot();
        const settings = await getWorkspaceSettings(this.serverId, projectRoot, true);

        const command = settings.interpreter[0];
        const cwd = settings.cwd;

        const envVars = await this.prepareEnvVars();
        const args = this.constructServerArgs(settings, envVars);

        const initOptions = {
            settings: await getExtensionSettings(this.serverId, true),
            globalSettings: await getGlobalSettings(this.serverId, false),
        };

        traceInfo(`Server run command: ${[command, ...args].join(' ')}`);

        const serverOptions: ServerOptions = {
            command,
            args,
            options: { cwd, env: envVars },
        };

        const clientOptions: LanguageClientOptions = {
            documentSelector: getDocumentSelector(),
            outputChannel: this.outputChannel,
            traceOutputChannel: this.outputChannel,
            revealOutputChannelOn: RevealOutputChannelOn.Never,
            connectionOptions: { maxRestartCount: 0 },
            initializationOptions: initOptions,
        };

        const client = new LanguageClient(this.serverId, this.serverName, serverOptions, clientOptions);

        this.disposables.push(client.onDidChangeState((e) => this.handleServerStateChange(e)));
        return client;
    }
}
