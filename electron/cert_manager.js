// electron/cert_manager.js
const { exec } = require('child_process');
const path = require('path');
const os = require('os');

/**
 * OS별 인증서 자동 설치 및 신뢰 설정
 * @param {Function} callback - 설치 완료(또는 실패) 후 실행할 콜백 함수
 */
function installCertificate(callback) {
  const platform = process.platform;
  const homeDir = os.homedir();
  let certPath = '';
  let installCmd = '';

  console.log(`[Cert Manager] 플랫폼 감지: ${platform}`);

  if (platform === 'win32') {
    // 1. Windows: certutil 사용 (root 저장소에 추가)
    certPath = path.join(homeDir, '.mitmproxy', 'mitmproxy-ca-cert.cer');
    installCmd = `certutil -addstore root "${certPath}"`;

  } else if (platform === 'darwin') {
    // 2. macOS: security 명령어 사용 (login 키체인에 추가 및 신뢰 설정)
    certPath = path.join(homeDir, '.mitmproxy', 'mitmproxy-ca-cert.pem');
    const keychainPath = path.join(homeDir, 'Library/Keychains/login.keychain-db');
    installCmd = `security add-trusted-cert -d -r trustRoot -k "${keychainPath}" "${certPath}"`;
  }

  if (installCmd) {
    console.log(`[Cert Manager] 인증서 설치 시도 중...`);
    exec(installCmd, (error, stdout, stderr) => {
      if (error) {
        // 관리자 권한 부족 등의 이유로 에러가 날 수 있으나, 서비스 중단을 막기 위해 로그만 남김
        console.warn(`[Cert Manager Warning] 자동 설치 실패 (권한 부족일 수 있음): ${error.message}`);
      } else {
        console.log('[Cert Manager] 인증서 설치 및 신뢰 설정 완료.');
      }
      if (callback) callback();
    });
  } else {
    console.log('[Cert Manager] 지원되지 않는 OS입니다. 자동 설치를 건너뜁니다.');
    if (callback) callback();
  }
}

module.exports = { installCertificate };