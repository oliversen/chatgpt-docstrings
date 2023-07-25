import * as vscode from 'vscode';
import {
    LanguageClient,
    TextDocumentPositionParams,
    ExecuteCommandParams,
    ExecuteCommandRequest
} from 'vscode-languageclient/node';
import { OpenaiApiKey } from "./openai-api-key";

export async function generateDocstring(
    lsClient: LanguageClient | undefined,
    serverStarting: boolean,
    secrets: vscode.SecretStorage
) {
    if (!lsClient) {
        if (serverStarting) {
            vscode.window.showInformationMessage('Python Language Server is starting, try again later.');
        } else {
            vscode.window.showInformationMessage('Python Language Server not running, try restart it.');
        }
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
        position: { line: pos.line, character: pos.character }
    };
    const params: ExecuteCommandParams = {
        command: 'chatgpt-docstrings.applyGenerate',
        arguments: [textDocument, openaiApiKey]
    };
    vscode.window.withProgress({
        location: vscode.ProgressLocation.Window,
        title: "Generating docstring...",
        cancellable: false
    }, (_progress, _token) => {
        const p = new Promise<void>(resolve => {
            lsClient.sendRequest(ExecuteCommandRequest.type, params)
                .catch((error) => {
                    vscode.window.showErrorMessage(`${error.message} See '${lsClient.outputChannel.name}' output channel for details.`, { title: 'Open Output', id: 1 }).then((value) => {
                        if (value !== undefined && value.id === 1) {
                            lsClient.outputChannel.show();
                        }
                    });
                })
                .finally(() => {
                    resolve();
                });
        });
        return p;
    });
}