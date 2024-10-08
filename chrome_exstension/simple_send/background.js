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
        (async () => {
            let queryOptions = {active: true, currentWindow: true};
            // let [tab] = await chrome.tabs.query(queryOptions);
            // console.log("Link URL:", info.linkUrl);
            const url = new URL(info.linkUrl);
            const port = (await chrome.storage.sync.get('port')).port;
            const server = (await chrome.storage.sync.get('server')).server;
            const secure = (await chrome.storage.sync.get('secure')).secure;
            const endpoint = (await chrome.storage.sync.get('endpoint')).endpoint;
            // chrome.tabs.update({
            //   url: `http${secure ? 's' : ''}://localhost:${port ?? '3000'}${
            //     url.pathname
            //   }`,
            let data = {
                url: url
            };
            const surl = `http${secure ? 's' : ''}://${server ?? 'localhost'}:${port ?? '3000'}${endpoint}`
            fetch(surl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }).then(response => response.json())
                .then(json => console.log(json))
                .catch(error => console.error('Error:', error));
        })();
    }
});

async function getCurrentTab() {
    let queryOptions = {active: true, lastFocusedWindow: true};
    // `tab` will either be a `tabs.Tab` instance or `undefined`.
    let [tab] = await chrome.tabs.query(queryOptions);
    return tab;
}