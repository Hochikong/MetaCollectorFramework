// Saves options to chrome.storage
const saveOptions = () => {
    const server = document.getElementById('server').value;
    const port = document.getElementById('port').value;
    const secure = document.getElementById('secure').checked;
    const endpoint = document.getElementById('endpoint').value;
    chrome.storage.sync.set({server, port, secure, endpoint});
    window.close();
};

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
const restoreOptions = async () => {
    const syncItems = await chrome.storage.sync.get(['server', 'port', 'secure', 'endpoint']);
    console.log(syncItems);
    document.getElementById('server').value = syncItems.server ?? 'localhost';
    document.getElementById('port').value = syncItems.port ?? '3000';
    document.getElementById('secure').checked = syncItems.secure;
    document.getElementById('endpoint').value = syncItems.endpoint ?? '/mcf/v2/tasks/single/';
};

document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save').addEventListener('click', saveOptions);
