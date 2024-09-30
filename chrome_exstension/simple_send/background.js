// Create context menu item
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "sendPostRequest",
        title: "Send URL via POST request",
        contexts: ["all"]
    });
});

// Add click event listener
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "sendPostRequest") {
        sendPostRequest();
    }
});

async function getCurrentTab() {
    let queryOptions = {active: true, lastFocusedWindow: true};
    // `tab` will either be a `tabs.Tab` instance or `undefined`.
    let [tab] = await chrome.tabs.query(queryOptions);
    return tab;
}

function sendPostRequest() {
    console.log("sending PostRequest");
    let tab = getCurrentTab();
    tab.then(data => {
        // console.log('PromiseResult:', data);
        // console.log(data.url);
    const url = new URL(data.url);
    const server = (chrome.storage.sync.get('server')).server;
    const port = (chrome.storage.sync.get('port')).port;
    const secure = (chrome.storage.sync.get('secure')).secure;
        const endpoint = (chrome.storage.sync.get('endpoint')).endpoint;

    let sendData = {
        url: url
    };
        const surl = `http${secure ? 's' : ''}://${server ?? 'localhost'}:${port ?? '3000'}${endpoint}`;

    fetch(surl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(sendData)
    })
        .then(response => response.json())
        .then(json => console.log(json))
        .catch(error => console.error('Error:', error));
    })
        .catch(error => {
            console.error('Error:', error);
        });


}
