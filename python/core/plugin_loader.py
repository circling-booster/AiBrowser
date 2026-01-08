import os
import importlib.util
import json
from utils.logger import setup_logger

logger = setup_logger("plugin_loader")

def load_plugins():
    plugins_dir = "plugins"
    loaded = {}
    
    if not os.path.exists(plugins_dir):
        return loaded

    for item in os.listdir(plugins_dir):
        p_path = os.path.join(plugins_dir, item)
        backend = os.path.join(p_path, "backend.py")
        manifest_path = os.path.join(p_path, "manifest.json")
        
        if os.path.exists(backend):
            try:
                # 1. Manifest 로드
                manifest_data = {}
                if os.path.exists(manifest_path):
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest_data = json.load(f)

                # 2. Backend 모듈 로드
                spec = importlib.util.spec_from_file_location(f"plugins.{item}", backend)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "router"):
                    # Router와 Manifest를 함께 반환 구조 변경
                    loaded[item] = {
                        "router": module.router,
                        "manifest": manifest_data
                    }
                    logger.info(f"Loaded plugin: {item}")
            except Exception as e:
                logger.error(f"Failed to load plugin {item}: {e}")
    return loaded