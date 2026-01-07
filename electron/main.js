// electron/main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const certManager = require('./cert_manager'); // 인증서 관리 모듈

let mainWindow;
let pythonProcess;
let proxyProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.webContents.openDevTools();
  const url = 'http://localhost:3000';
  console.log(`[Electron] UI 로드 중: ${url}`);
  mainWindow.loadURL(url);

  mainWindow.webContents.on('did-fail-load', () => {
    console.error(`[Electron Error] 페이지를 로드할 수 없습니다. Vite 서버를 확인하세요.`);
  });
}

// Python FastAPI 서버 실행
function startPythonBackend() {
  const scriptPath = path.join(__dirname, '../backend/main.py');
  pythonProcess = spawn('python', [scriptPath]);

  pythonProcess.stdout.on('data', (data) => console.log(`[Python]: ${data}`));
  pythonProcess.stderr.on('data', (data) => console.error(`[Python Error]: ${data}`));
}

// Mitmproxy(프록시 서버) 실행
function launchMitmproxy() {
  if (proxyProcess) return;

  const addonPath = path.join(__dirname, '../backend/addons/injector.py');
  // 8080 포트로 프록시 서버 실행
  proxyProcess = spawn('mitmdump', ['-s', addonPath, '--listen-port', '8080']);
  
  proxyProcess.stdout.on('data', (data) => console.log(`[Proxy]: ${data}`));
  proxyProcess.stderr.on('data', (data) => console.error(`[Proxy Error]: ${data}`));

  console.log("[System] 프록시 서버(Port 8080)가 준비되었습니다.");
}

// 앱 시작 시 자동 실행 흐름
app.whenReady().then(() => {
  // 1. 파이썬 백엔드 시작
  startPythonBackend();

  // 2. 인증서 설치 후 프록시 자동 시작 (개선된 부분)
  certManager.installCertificate(() => {
    launchMitmproxy();
  });

  // 3. UI 창 생성
  createWindow();
});

// 기존 버튼 클릭 대응 (이미 실행 중이면 무시)
ipcMain.handle('start-proxy', () => {
  launchMitmproxy();
});

app.on('window-all-closed', () => {
  if (pythonProcess) pythonProcess.kill();
  if (proxyProcess) proxyProcess.kill();
  app.quit();
});