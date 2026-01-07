import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from .plugin_loader import load_plugins
from utils.logger import setup_logger
import httpx
import json

logger = setup_logger("api_server")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Plugins on Startup
@app.on_event("startup")
async def startup_event():
    plugins = load_plugins()
    for pid, router in plugins.items():
        if router:
            app.include_router(router, prefix=f"/api/plugins/{pid}")
            logger.info(f"Plugin loaded: {pid}")

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

@app.post("/api/relay/{plugin_id}/{func_name}")
async def relay_inference(plugin_id: str, func_name: str, request: Request):
    """Relays requests to Azure if Web Inference is enabled."""
    body = await request.json()
    
    config_path = "config/settings.json"
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except:
        config = {"inference_mode": "local"}
        
    if config.get("inference_mode") == "web":
        target = f"{config['azure_relay_url']}/api/{plugin_id}/{func_name}"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(target, json=body, timeout=30.0)
                return resp.json()
            except Exception as e:
                return {"error": str(e)}
    else:
        return {"error": "Inference mode is local. Use plugin direct route."}

def start_api_server(api_port, proxy_port):
    uvicorn.run(app, host="127.0.0.1", port=api_port, log_level="error")