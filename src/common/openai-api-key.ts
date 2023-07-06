import * as vscode from 'vscode';

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

export async function setOpenaiApiKey(secrets: vscode.SecretStorage) {
    const openaiApiKey = await inputOpenaiApiKey();
    if (openaiApiKey) {
        await secrets.store("openaiApiKey", openaiApiKey);
    }
    return openaiApiKey;
}