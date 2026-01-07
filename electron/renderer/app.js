const logDiv = document.getElementById('log-container');
const statusDot = document.getElementById('status');

window.electronAPI.onLogEntry((msg) => {
    const div = document.createElement('div');
    div.className = 'log-entry';
    div.innerText = msg;
    logDiv.appendChild(div);
    logDiv.scrollTop = logDiv.scrollHeight;
});

window.electronAPI.onStatusUpdate((status) => {
    if (status === 'online') statusDot.classList.add('online');
});