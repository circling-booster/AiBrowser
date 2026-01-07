import os
import json
import importlib.util
from fastapi import APIRouter

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir
        self.plugins = {} # {plugin_id: metadata}
        self.routers = [] # FastAPI Routers

    def load_plugins(self):
        """plugins 폴더를 스캔하여 manifest.json을 읽고 모듈을 로드합니다."""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)

        for folder in os.listdir(self.plugin_dir):
            path = os.path.join(self.plugin_dir, folder)
            manifest_path = os.path.join(path, "manifest.json")
            
            if os.path.isdir(path) and os.path.exists(manifest_path):
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                
                plugin_id = manifest["id"]
                
                # Backend Logic 로드 (backend.py가 있는 경우)
                backend_file = os.path.join(path, manifest.get("backend_entry", "backend.py"))
                if os.path.exists(backend_file):
                    spec = importlib.util.spec_from_file_location(f"plugins.{folder}", backend_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 모듈 내에 router가 정의되어 있으면 등록
                    if hasattr(module, "router"):
                        self.routers.append(module.router)

                self.plugins[plugin_id] = {
                    "info": manifest,
                    "path": path,
                    "active": False # 기본값
                }
                print(f"[System] Plugin Loaded: {manifest['name']}")

    def get_active_injections(self, current_url):
        """현재 URL에 주입해야 할 스크립트(JS) 반환"""
        scripts = []
        for pid, pdata in self.plugins.items():
            if pdata["active"]:
                # 간단한 도메인 매칭 로직 (실제로는 정규식 추천)
                for target in pdata["info"]["targets"]:
                    if target in current_url:
                        inject_file = os.path.join(pdata["path"], pdata["info"]["frontend_script"])
                        if os.path.exists(inject_file):
                            with open(inject_file, "r", encoding="utf-8") as f:
                                scripts.append(f.read())
        return scripts

    def toggle_plugin(self, plugin_id: str, state: bool):
        if plugin_id in self.plugins:
            self.plugins[plugin_id]["active"] = state
            return True
        return False

# 싱글톤 인스턴스
manager = PluginManager()