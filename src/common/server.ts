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
import { getLSClientTraceLevel, getProjectRoot, getDocumentSelector } from './utilities';
import { telemetryReporter } from './telemetry';
import { updateStatus } from './status';

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
            const msg = `The interpreter set in "${serverId}.interpreter" setting is not supported. Please use Python 3.9 or greater.`;
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

    const msg = `Select the python interpreter version 3.9 or greater in the status bar, or set it in the "${serverId}.interpreter" setting.`;
    traceWarn(msg);
    updateStatus(msg, LanguageStatusSeverity.Warning);
    return false;
}

export class ServerManager {
    private disposables: Disposable[] = [];
    lsClient: LanguageClient | undefined;

    constructor(
        private serverId: string,
        private serverName: string,
        private outputChannel: LogOutputChannel,
    ) {}

    public async restartServer(): Promise<void> {
        await this.stopServer();
        if (!(await checkInterpreter(this.serverId))) return;
        const newLSClient = await this.createServer();
        if (!(await this.startServer(newLSClient))) return;
        this.configureTelemetry(newLSClient);
        await this.configureTraceLevel(newLSClient, this.outputChannel);
        this.lsClient = newLSClient;
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
