import argparse
import sys
import multiprocessing
import atexit
import time
import signal
import subprocess
import os
from utils.logger import setup_logger
from utils.system_proxy import SystemProxy
from utils.cert_manager import CertManager
from utils.admin_utils import is_admin
from core.api_server import start_api_server
from core.proxy_server import start_proxy_server

logger = setup_logger("main")

def kill_process_on_port(port):
    """
    윈도우에서 특정 포트를 사용 중인 프로세스(PID)를 찾아 강제 종료합니다.
    재실행 시 'Address already in use' 오류를 방지하기 위한 안전장치입니다.
    """
    try:
        # netstat 명령어로 포트 점유 중인 프로세스 찾기
        cmd = f'netstat -ano | findstr :{port}'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if not result.stdout:
            return

        lines = result.stdout.strip().split('\n')
        pids = set()
        
        for line in lines:
            # 리스닝 중인 포트만 타겟팅
            if "LISTENING" in line:
                parts = line.split()
                # 마지막 부분이 PID
                pid = parts[-1]
                if pid.isdigit() and int(pid) != os.getpid():
                    pids.add(pid)
        
        for pid in pids:
            logger.warning(f"Port {port} is occupied by PID {pid}. Killing zombie process...")
            subprocess.run(f"taskkill /F /PID {pid}", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            
    except Exception as e:
        logger.error(f"Failed to kill process on port {port}: {e}")

def cleanup(proxy_mgr):
    """Critical: Ensure system proxy is disabled on shutdown"""
    logger.info("Shutting down... Restoring system settings.")
    try:
        if proxy_mgr:
            proxy_mgr.disable_windows_proxy()
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

def terminate_process(process):
    """프로세스를 안전하게, 그러나 확실하게 종료합니다."""
    if process and process.is_alive():
        logger.info(f"Terminating process {process.name}...")
        process.terminate()
        process.join(timeout=2)
        if process.is_alive():
            logger.warning(f"Process {process.name} did not terminate. Killing it.")
            process.kill() # Python 3.7+ 강제 종료

def main():
    parser = argparse.ArgumentParser(description="AiPlugs Backend")
    parser.add_argument("--api-port", type=int, required=True)
    parser.add_argument("--proxy-port", type=int, required=True)
    args = parser.parse_args()

    # [중요] 시작 전 좀비 프로세스 정리 (Address already in use 방지)
    kill_process_on_port(args.api_port)
    kill_process_on_port(args.proxy_port)

    # 1. Admin Check
    if not is_admin():
        logger.warning("Running without Administrator privileges. Proxy/Cert operations may fail.")

    # 2. Certificate Management
    cert_mgr = CertManager()
    cert_mgr.ensure_cert_installed()

    # 3. Proxy Management Setup
    proxy_mgr = SystemProxy(port=args.proxy_port)
    atexit.register(cleanup, proxy_mgr)

    # 4. Start Services
    # API Server (FastAPI)
    api_process = multiprocessing.Process(
        target=start_api_server,
        args=(args.api_port, args.proxy_port),
        name="API_Server"
    )
    api_process.daemon = True

    # Proxy Server (Mitmproxy)
    proxy_process = multiprocessing.Process(
        target=start_proxy_server,
        args=(args.proxy_port, args.api_port),
        name="Proxy_Server"
    )
    proxy_process.daemon = True

    api_process.start()
    proxy_process.start()

    logger.info(f"Services Started. API: {args.api_port}, Proxy: {args.proxy_port}")

    # 5. Enable System Proxy (Wait 3s for Mitmproxy to initialize)
    time.sleep(3)
    proxy_mgr.enable_windows_proxy()

    try:
        # 메인 프로세스가 살아있는 동안 대기
        while api_process.is_alive() and proxy_process.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt received.")
    finally:
        # 종료 시 정리 작업
        cleanup(proxy_mgr)
        terminate_process(api_process)
        terminate_process(proxy_process)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()