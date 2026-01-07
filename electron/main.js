const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;
let proxyProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // React Dev Server 또는 빌드 파일 로드
  mainWindow.loadURL('http://localhost:3000'); 
}

// 1. Python FastAPI 서버 실행
function startPythonBackend() {
  const scriptPath = path.join(__dirname, '../backend/main.py');
  pythonProcess = spawn('python', [scriptPath]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Python]: ${data}`);
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Python Error]: ${data}`);
  });
}

// 2. Mitmproxy 실행 (Native Mode 요청 시)
ipcMain.handle('start-proxy', () => {
    if (proxyProcess) return;
    const addonPath = path.join(__dirname, '../backend/addons/injector.py');
    // mitmdump는 UI 없는 CLI 버전
    proxyProcess = spawn('mitmdump', ['-s', addonPath]); 
    console.log("Mitmproxy Started...");
});

app.whenReady().then(() => {
  startPythonBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  // 종료 시 하위 프로세스 정리 (중요)
  if (pythonProcess) pythonProcess.kill();
  if (proxyProcess) proxyProcess.kill();
  app.quit();
});