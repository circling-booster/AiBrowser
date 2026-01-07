import os
import importlib.util
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
        
        if os.path.exists(backend):
            try:
                spec = importlib.util.spec_from_file_location(f"plugins.{item}", backend)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "router"):
                    loaded[item] = module.router
            except Exception as e:
                logger.error(f"Failed to load plugin {item}: {e}")
    return loaded