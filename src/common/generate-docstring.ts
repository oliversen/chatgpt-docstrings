import * as vscode from 'vscode';
import {
    LanguageClient,
    TextDocumentPositionParams,
    ExecuteCommandParams,
    ExecuteCommandRequest,
    ProgressType,
    WorkDoneProgressReport,
    WorkDoneProgressCancelNotification,
} from 'vscode-languageclient/node';
import * as UUID from 'vscode-languageclient/lib/common/utils/uuid';
import { ApiKey } from './api-key';
import { telemetryReporter } from './telemetry';
import { getStatus } from './status';
import { getProjectRoot } from './utilities';
import { getWorkspaceSettings } from './settings';

function showProblemNotification(): void {
    const status: vscode.LanguageStatusItem | undefined = getStatus();
    if (status) {
        if (status.busy) {
            vscode.window.showInformationMessage('Server is starting... Try again in a few seconds.');
            return;
        }
        let msg;
        const msgItems = [
            { title: 'Show Logs', id: 1 },
            { title: 'Restart Server', id: 2 },
        ];
        switch (status.severity) {
            case vscode.LanguageStatusSeverity.Information:
                msg = vscode.window.showInformationMessage('Server not running...', ...msgItems);
                break;
            case vscode.LanguageStatusSeverity.Warning:
                msg = vscode.window.showWarningMessage(status.text, ...msgItems);
                break;
            case vscode.LanguageStatusSeverity.Error:
                msg = vscode.window.showErrorMessage(status.text, ...msgItems);
                break;
        }
        msg.then((value) => {
            if (value !== undefined && value.id === 1) {
                vscode.commands.executeCommand('chatgpt-docstrings.showLogs');
            } else if (value !== undefined && value.id === 2) {
                vscode.commands.executeCommand('chatgpt-docstrings.restart');
            }
        });
    }
}

export async function generateDocstring(
    serverId: string,
    lsClient: LanguageClient | undefined,
    secrets: vscode.SecretStorage,
) {
    if (!lsClient) {
        showProblemNotification();
        return;
    }

    const textEditor = vscode.window.activeTextEditor;
    if (!textEditor) {
        return;
    }

    const apiKey = await new ApiKey(lsClient.outputChannel, secrets).get();
    if (!apiKey) {
        return;
    }

    const projectRoot = await getProjectRoot();
    const settings = await getWorkspaceSettings(serverId, projectRoot, false);
    const pos = textEditor.selection.start;
    const textDocument: TextDocumentPositionParams = {
        textDocument: { uri: textEditor.document.uri.toString() },
        position: { line: pos.line, character: pos.character },
    };
    vscode.window.withProgress(
        {
            location: settings.showProgressNotification
                ? vscode.ProgressLocation.Notification
                : vscode.ProgressLocation.Window,
            cancellable: true,
        },
        (progress, progressToken) => {
            progress.report({ message: 'Generating docstring...' });

            let progressTokenID = UUID.generateUuid();
            progressToken.onCancellationRequested(() => {
                lsClient.sendNotification(WorkDoneProgressCancelNotification.type, { token: progressTokenID });
            });

            let progressDisposable = lsClient.onProgress(
                new ProgressType<WorkDoneProgressReport>(),
                progressTokenID,
                async (params) => {
                    progress.report(params);
                },
            );

            const params: ExecuteCommandParams = {
                command: 'chatgpt-docstrings.applyGenerate',
                arguments: [textDocument, apiKey, progressTokenID],
            };

            const p = new Promise<void>((resolve) => {
                lsClient
                    .sendRequest(ExecuteCommandRequest.type, params)
                    .catch((error) => {
                        vscode.window
                            .showErrorMessage(
                                `${error.message} See '${lsClient.outputChannel.name}' output channel for details.`,
                                { title: 'Open Output', id: 1 },
                            )
                            .then((value) => {
                                if (value !== undefined && value.id === 1) {
                                    lsClient.outputChannel.show();
                                }
                            });
                        telemetryReporter.sendError('clientRequestGenerateError', error.toJson());
                    })
                    .finally(() => {
                        progressDisposable.dispose();
                        resolve();
                    });
            });
            return p;
        },
    );
}
