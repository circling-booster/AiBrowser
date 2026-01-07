import argparse
import sys
import multiprocessing
import atexit
import time
import signal
from utils.logger import setup_logger
from utils.system_proxy import SystemProxy
from utils.cert_manager import CertManager
from utils.admin_utils import is_admin
from core.api_server import start_api_server
from core.proxy_server import start_proxy_server

logger = setup_logger("main")

def cleanup(proxy_mgr):
    """Critical: Ensure system proxy is disabled on shutdown"""
    logger.info("Shutting down... Restoring system settings.")
    try:
        if proxy_mgr:
            proxy_mgr.disable_windows_proxy()
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="AiPlugs Backend")
    parser.add_argument("--api-port", type=int, required=True)
    parser.add_argument("--proxy-port", type=int, required=True)
    args = parser.parse_args()

    # 1. Admin Check
    if not is_admin():
        logger.warning("Running without Administrator privileges. Proxy/Cert operations may fail.")

    # 2. Certificate Management
    cert_mgr = CertManager()
    cert_mgr.ensure_cert_installed()

    # 3. Proxy Management Setup
    proxy_mgr = SystemProxy(port=args.proxy_port)
    atexit.register(cleanup, proxy_mgr)

    # 4. Start Services (Multiprocessing for isolation)
    # API Server (FastAPI)
    api_process = multiprocessing.Process(
        target=start_api_server,
        args=(args.api_port, args.proxy_port),
        name="API_Server"
    )
    
    # Proxy Server (Mitmproxy)
    proxy_process = multiprocessing.Process(
        target=start_proxy_server,
        args=(args.proxy_port, args.api_port),
        name="Proxy_Server"
    )

    api_process.start()
    proxy_process.start()

    logger.info(f"Services Started. API: {args.api_port}, Proxy: {args.proxy_port}")

    # 5. Enable System Proxy (Wait 3s for Mitmproxy to initialize)
    time.sleep(3)
    proxy_mgr.enable_windows_proxy()

    try:
        api_process.join()
        proxy_process.join()
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt received.")
    finally:
        cleanup(proxy_mgr)
        if api_process.is_alive(): api_process.terminate()
        if proxy_process.is_alive(): proxy_process.terminate()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()