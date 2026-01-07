import ctypes
import winreg
from .logger import setup_logger

logger = setup_logger("system_proxy")

class SystemProxy:
    def __init__(self, port):
        self.port = port
        self.proxy_server = f"127.0.0.1:{port}"
        self.reg_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

    def _refresh(self):
        """Force Windows to refresh internet settings immediately via WinINet API."""
        INTERNET_OPTION_SETTINGS_CHANGED = 39
        INTERNET_OPTION_REFRESH = 37
        ctypes.windll.wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        ctypes.windll.wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)

    def enable_windows_proxy(self):
        logger.info(f"Enabling System Proxy -> {self.proxy_server}")
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_WRITE)
            
            # Enable Proxy
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            # Set Server
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, self.proxy_server)
            # Bypass Localhost
            winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "<local>")
            
            winreg.CloseKey(key)
            self._refresh()
        except Exception as e:
            logger.error(f"Failed to enable proxy: {e}")

    def disable_windows_proxy(self):
        logger.info("Disabling System Proxy")
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            self._refresh()
        except Exception as e:
            logger.error(f"Failed to disable proxy: {e}")