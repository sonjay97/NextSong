let ipodRoot = null;

function setIpodStatus(text) {
    const el = document.getElementById('ipod-status');
    if (el) el.textContent = text;
}

/** returns true if the folder has a itunes db */
async function isIpodRoot(handle) {

    try {

        const control = await handle.getDirectoryHandle('iPod_Control');
        const itunes = await control.getDirectoryHandle('iTunes');
        await itunes.getFileHandle('iTunesDB');

        return true;
    } catch {
        return false;
    }
}

/** when user clicks connect iPod */

async function connectIpod() {

    if (!window.showDirectoryPicker) {
        alert('Sadly connecting an iPod through the browser requires Chrome or Microsoft Edge (nasty!). :( ')
        return;
    }

    try {

        setIpodStatus('Opening file explorer.');

        const handle = await window.showDirectoryPicker({ mode: 'readwrite' });

        if (!(await isIpodRoot(handle))) {
            
            setIpodStatus('Not connected');
            alert(
                'I don\'t think that folder is an iPod. I could be wrong though. but I think I\'m right.'
            );
            return;
        }

        ipodRoot = handle;

        setIpodStatus('Connected');
    } catch (err) {

        if (err.name === 'AbortError') {
            // user closed directory without choosing
            setIpodStatus('Not connected');
            return;
        }
        
        console.error(err);
        setIpodStatus('Not connected');
        alert('Could not connect: ' + err.message);
    }
}

/** read itunesDB from ipod */
async function getItunesDbFile() {

    if (!ipodRoot) throw new Error('Connect an iPod pls.');

    const itunes = await ipodRoot
        .getDirectoryHandle('iPod_Control')
        .then((h) => h.getDirectoryHandle('iTunes'));

    const fh = await itunes.getFileHandle('iTunesDB');

    return fh.getFile();
}

/** wire the connect button once DOM is ready */
function initIpodClient() {
    const btn = document.getElementById('connect-ipod');
    if (btn) btn.addEventListener('click', connectIpod);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initIpodClient);
} else {
    initIpodClient();
}