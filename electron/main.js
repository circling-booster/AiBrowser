// electron/main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const certManager = require('./cert_manager'); // [추가] 인증서 관리 모듈 임포트

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

  // [디버깅] 개발자 도구 열기
  mainWindow.webContents.openDevTools();

  const url = 'http://localhost:3000';
  console.log(`[Electron] Loading URL: ${url}`);

  mainWindow.loadURL(url);

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error(`[Electron Error] Failed to load URL: ${errorCode} - ${errorDescription}`);
  });
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

// 2. Mitmproxy 실행 함수 (실제 프로세스 생성)
function launchMitmproxy() {
  const addonPath = path.join(__dirname, '../backend/addons/injector.py');
  // mitmdump는 UI 없는 CLI 버전
  proxyProcess = spawn('mitmdump', ['-s', addonPath]);
  
  proxyProcess.stdout.on('data', (data) => {
    console.log(`[Mitmproxy]: ${data}`);
  });

  proxyProcess.stderr.on('data', (data) => {
    console.error(`[Mitmproxy Error]: ${data}`);
  });

  console.log("Mitmproxy Started...");
}

// 3. 프록시 시작 요청 처리 (인증서 설치 -> 프록시 실행)
ipcMain.handle('start-proxy', () => {
  if (proxyProcess) return;

  // 인증서 설치 모듈 호출, 설치 완료(또는 스킵) 후 launchMitmproxy 실행
  certManager.installCertificate(() => {
    launchMitmproxy();
  });
});

app.whenReady().then(() => {
  startPythonBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  if (pythonProcess) pythonProcess.kill();
  if (proxyProcess) proxyProcess.kill();
  app.quit();
});