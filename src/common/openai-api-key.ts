import * as vscode from 'vscode';
import { traceError } from './log/logging';

async function inputOpenaiApiKey() {
    const prompt = 'Please enter your OpenAI API key. You can get the key [here](https://platform.openai.com/account/api-keys).';
    const openaiApiKey = await vscode.window.showInputBox(
        {
            prompt: prompt,
            validateInput: text => {
                if (!text) {
                    return prompt;
                } else {
                    return undefined;
                }
            }
        }
    );
    return openaiApiKey;
}

export async function setOpenaiApiKey(outputChannel: vscode.OutputChannel, secrets: vscode.SecretStorage) {
    const openaiApiKey = await inputOpenaiApiKey();
    if (openaiApiKey) {
        await secrets.store("openaiApiKey", openaiApiKey).then(undefined,
            (error) => {
                traceError('Error saving OpenAI API Key: ', error);
                vscode.window.showErrorMessage(`Error saving OpenAI API Key! See '${outputChannel.name}' output channel for details.`, { title: 'Open Output', id: 1 }).then((value) => {
                    if (value !== undefined && value.id === 1) {
                        outputChannel.show();
                    }
                });
            },
        );
    }
    return openaiApiKey;
}