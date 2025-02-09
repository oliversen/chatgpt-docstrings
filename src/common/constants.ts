// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import * as path from 'path';

const folderName = path.basename(__dirname);
export const EXTENSION_ROOT_DIR =
    folderName === 'common' ? path.dirname(path.dirname(__dirname)) : path.dirname(__dirname);
export const SERVER_LIBS_PATH = path.join(EXTENSION_ROOT_DIR, 'language_server', `libs`);
export const SERVER_START_SCRIPT_PATH = path.join(EXTENSION_ROOT_DIR, 'language_server', `_start.py`);
export const SERVER_DEBUG_SCRIPT_PATH = path.join(EXTENSION_ROOT_DIR, 'language_server', `_debug.py`);
