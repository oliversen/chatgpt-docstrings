import * as vscode from 'vscode';
import { traceWarn } from './log/logging';
import { telemetryReporter } from './telemetry';

let _cashedKey: string | undefined = undefined;

export class OpenaiApiKey {
    private readonly secretId: string = 'openaiApiKey';
    private outputChannel: vscode.OutputChannel;
    private secretStorage: vscode.SecretStorage;

    constructor(outputChannel: vscode.OutputChannel, secretStorage: vscode.SecretStorage) {
        this.outputChannel = outputChannel;
        this.secretStorage = secretStorage;
    }

    public async get() {
        if (!_cashedKey) {
            await this.secretStorage.get(this.secretId).then(
                (key) => {
                    _cashedKey = key;
                },
                (error) => {
                    traceWarn('Failed to get OpenAI API Key from SecretStorage: ', error);
                    const errorJson = { name: error.name, message: error.message, stack: error.stack };
                    telemetryReporter.sendError('getOpenaiApiKeyError', errorJson);
                    vscode.window
                        .showWarningMessage(
                            `Failed to get OpenAI API Key from SecretStorage! See '${this.outputChannel.name}' output channel for details.`,
                            { title: 'Open Output', id: 1 },
                        )
                        .then((value) => {
                            if (value !== undefined && value.id === 1) {
                                this.outputChannel.show();
                            }
                        });
                },
            );
        }
        return _cashedKey || (await this.set());
    }

    public async set() {
        const key = await this._ask();
        if (key) {
            _cashedKey = key;
            await this.secretStorage.store(this.secretId, key).then(undefined, (error) => {
                traceWarn('Failed to save OpenAI API Key to SecretStorage: ', error);
                const errorJson = { name: error.name, message: error.message, stack: error.stack };
                telemetryReporter.sendError('saveOpenaiApiKeyError', errorJson);
                vscode.window
                    .showWarningMessage(
                        `Failed to save OpenAI API Key to SecretStorage! See '${this.outputChannel.name}' output channel for details.`,
                        { title: 'Open Output', id: 1 },
                    )
                    .then((value) => {
                        if (value !== undefined && value.id === 1) {
                            this.outputChannel.show();
                        }
                    });
            });
        }
        return key;
    }

    private async _ask() {
        const prompt =
            'Please enter your OpenAI API key. You can get the key [here](https://platform.openai.com/account/api-keys).';
        const key = await vscode.window.showInputBox({
            prompt: prompt,
            validateInput: (text) => {
                if (!text) {
                    return prompt;
                } else {
                    return undefined;
                }
            },
        });
        return key;
    }
}
