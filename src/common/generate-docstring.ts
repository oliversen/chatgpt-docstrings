import * as vscode from 'vscode';
import {
    LanguageClient,
    TextDocumentPositionParams,
    ExecuteCommandParams,
    ExecuteCommandRequest,
} from 'vscode-languageclient/node';
import { OpenaiApiKey } from './openai-api-key';
import { telemetryReporter } from './telemetry';

export async function generateDocstring(lsClient: LanguageClient | undefined, secrets: vscode.SecretStorage) {
    if (!lsClient) {
        return;
    }

    const textEditor = vscode.window.activeTextEditor;
    if (!textEditor) {
        return;
    }

    const openaiApiKey = await new OpenaiApiKey(lsClient.outputChannel, secrets).get();
    if (!openaiApiKey) {
        return;
    }

    const pos = textEditor.selection.start;
    const textDocument: TextDocumentPositionParams = {
        textDocument: { uri: textEditor.document.uri.toString() },
        position: { line: pos.line, character: pos.character },
    };
    const params: ExecuteCommandParams = {
        command: 'chatgpt-docstrings.applyGenerate',
        arguments: [textDocument, openaiApiKey],
    };
    vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Window,
            title: 'Generating docstring...',
            cancellable: false,
        },
        (_progress, _token) => {
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
                        resolve();
                    });
            });
            return p;
        },
    );
}
