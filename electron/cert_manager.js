// electron/cert_manager.js
const { exec } = require('child_process');
const path = require('path');
const os = require('os');

function installCertificate(callback) {
  const platform = process.platform;
  const homeDir = os.homedir();
  let certPath = '';
  let installCmd = '';

  console.log(`[Cert Manager] Detected Platform: ${platform}`);

  if (platform === 'win32') {
    // 1. Windows: certutil 사용 (.cer 파일)
    // 'root' 저장소에 추가하여 신뢰할 수 있는 루트 인증서로 등록
    certPath = path.join(homeDir, '.mitmproxy', 'mitmproxy-ca-cert.cer');
    installCmd = `certutil -addstore root "${certPath}"`;

  } else if (platform === 'darwin') {
    // 2. macOS: security 명령어 사용 (.pem 파일)
    // login 키체인에 추가하고(-k), 신뢰 설정(-d), 항상 신뢰(-r trustRoot) 옵션 적용
    certPath = path.join(homeDir, '.mitmproxy', 'mitmproxy-ca-cert.pem');
    const keychainPath = path.join(homeDir, 'Library/Keychains/login.keychain-db');
    installCmd = `security add-trusted-cert -d -r trustRoot -k "${keychainPath}" "${certPath}"`;
  }

  // 3. 명령어 실행
  if (installCmd) {
    console.log(`[Cert Manager] Executing: ${installCmd}`);
    exec(installCmd, (error, stdout, stderr) => {
      if (error) {
        console.error(`[Cert Manager Error]: ${error.message}`);
        console.error(`[Cert Manager Stderr]: ${stderr}`);
        // 권한 문제나 사용자 취소 등으로 실패할 수 있으나, 
        // 프로그램 흐름을 위해 프록시 실행은 계속 진행하도록 함
      } else {
        console.log('[Cert Manager] Certificate trusted successfully.');
      }
      // 작업 완료 후 콜백 실행 (프록시 런칭)
      if (callback) callback();
    });
  } else {
    // 리눅스 등 기타 OS는 별도 설치 과정 없이 진행
    console.log('[Cert Manager] No auto-install script for this platform. Skipping...');
    if (callback) callback();
  }
}

module.exports = { installCertificate };