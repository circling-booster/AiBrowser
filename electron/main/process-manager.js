const { spawn } = require('child_process');
const path = require('path');
const getPort = require('get-port');
const treeKill = require('tree-kill');
const WebSocket = require('ws');

let pythonProcess = null;

async function startPythonBackend(mainWindow) {
  const apiPort = await getPort({ port: 54321 });
  const proxyPort = await getPort({ port: 8080 });

  const scriptPath = path.join(__dirname, '../../python/main.py');
  
  // Use PYTHONUNBUFFERED to ensure logs stream immediately
  pythonProcess = spawn('python', [
    scriptPath,
    '--api-port', apiPort,
    '--proxy-port', proxyPort
  ], {
    env: { ...process.env, PYTHONUNBUFFERED: "1" }
  });

  console.log(`[Electron] Spawning Python: API=${apiPort}, Proxy=${proxyPort}`);

  pythonProcess.stdout.on('data', (data) => {
    const msg = data.toString();
    console.log(`[Py]: ${msg}`);
    if (mainWindow) mainWindow.webContents.send('log-entry', msg);
  });

  pythonProcess.stderr.on('data', (data) => {
    const msg = data.toString();
    console.error(`[Py Err]: ${msg}`);
    if (mainWindow) mainWindow.webContents.send('log-entry', `ERROR: ${msg}`);
  });

  verifyConnection(apiPort, mainWindow);

  return { apiPort, proxyPort };
}

function verifyConnection(port, mainWindow) {
  setTimeout(() => {
    const ws = new WebSocket(`ws://127.0.0.1:${port}/ws`);
    ws.on('open', () => {
        ws.send('ping');
        if(mainWindow) mainWindow.webContents.send('status-update', 'online');
        ws.close();
    });
    ws.on('error', () => {
        if(mainWindow) mainWindow.webContents.send('status-update', 'starting');
        verifyConnection(port, mainWindow); // Retry
    });
  }, 2000);
}

function killPythonProcess() {
  if (pythonProcess) {
    console.log("[Electron] Killing Python Process...");
    treeKill(pythonProcess.pid);
  }
}

module.exports = { startPythonBackend, killPythonProcess };