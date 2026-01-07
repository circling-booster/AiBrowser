const { app, BrowserWindow } = require('electron');
const path = require('path');
const { startPythonBackend, killPythonProcess } = require('./process-manager');
const { setupCSPBypass } = require('./session-handler');
const { setupIPC } = require('./ipc-handler');

let mainWindow;

async function createWindow() {
  // 1. 창(Window)을 먼저 생성하여 mainWindow 변수에 객체를 할당합니다.
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // 2. 초기화된 mainWindow 객체를 백엔드 시작 함수에 전달합니다.
  // 이제 process-manager.js가 정상적으로 이 창에 로그와 상태 메시지를 보낼 수 있습니다.
  const { apiPort } = await startPythonBackend(mainWindow);

  // 3. UI 파일 로드
  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  
  // 4. 내부 브라우저 세션에 설정(포트 정보) 주입
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