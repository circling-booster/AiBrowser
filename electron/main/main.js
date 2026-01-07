const { app, BrowserWindow } = require('electron');
const path = require('path');
const { startPythonBackend, killPythonProcess } = require('./process-manager');
const { setupCSPBypass } = require('./session-handler');
const { setupIPC } = require('./ipc-handler');

let mainWindow;

async function createWindow() {
  const { apiPort } = await startPythonBackend(mainWindow);

  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  
  // Inject Config into Internal Browser Session
  mainWindow.webContents.executeJavaScript(`window.AiPlugsConfig = { apiPort: ${apiPort} };`);
  
  setupCSPBypass();
}

app.whenReady().then(() => {
  setupIPC();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  killPythonProcess();
});