import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from .plugin_loader import load_plugins
from utils.logger import setup_logger
import json

# 전역 Inference Manager 인스턴스 (플러그인에서 참조)
inference_mgr = None

logger = setup_logger("api_server")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global inference_mgr
    loaded_data = load_plugins()
    
    manifests = {}
    
    for pid, data in loaded_data.items():
        router = data.get("router")
        manifest = data.get("manifest", {})
        
        manifests[pid] = manifest
        
        if router:
            app.include_router(router, prefix=f"/api/plugins/{pid}")
            
    # Manifest 정보를 기반으로 Manager 초기화
    from core.inference_manager import InferenceManager
    inference_mgr = InferenceManager(manifests)
    logger.info("InferenceManager initialized.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Establishes readiness check with Electron"""
    await websocket.accept()
    logger.info("Electron connected via WebSocket")
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except Exception:
        logger.info("WebSocket disconnected")

# 기존의 단순 relay 라우트는 제거되고, 각 플러그인 내부에서 Manager를 통해 처리됨

def start_api_server(api_port, proxy_port):
    uvicorn.run(app, host="127.0.0.1", port=api_port, log_level="error")