(async () => {
    let queryOptions = {active: true, currentWindow: true};
    let [tab] = await chrome.tabs.query(queryOptions);
    const url = new URL(tab.url);
    const port = (await chrome.storage.sync.get('port')).port;
    const server = (await chrome.storage.sync.get('server')).server;
    const secure = (await chrome.storage.sync.get('secure')).secure;
    // chrome.tabs.update({
    //   url: `http${secure ? 's' : ''}://localhost:${port ?? '3000'}${
    //     url.pathname
    //   }`,
    let data = {
        url: url
    };
    const surl = `http${secure ? 's' : ''}://${server ?? 'localhost'}:${port ?? '3000'}`
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
