from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from core.plugin_manager import manager
import uvicorn
import threading

app = FastAPI()

# CORS 설정 (Electron 및 Injected Script 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 플러그인 로드 및 라우터 등록
manager.load_plugins()
for router in manager.routers:
    app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "running", "platform": "AI-Browser-Assistant"}

@app.get("/plugins")
def list_plugins():
    return manager.plugins

@app.post("/plugins/{plugin_id}/toggle")
def toggle_plugin(plugin_id: str, active: bool):
    return {"success": manager.toggle_plugin(plugin_id, active)}

@app.get("/injection/scripts")
def get_scripts(url: str):
    """Proxy나 Injected Script가 호출하여 실행할 JS 코드를 받아감"""
    return {"scripts": manager.get_active_injections(url)}

if __name__ == "__main__":
    # Electron에서 실행 시 포트 5000 사용
    uvicorn.run(app, host="127.0.0.1", port=5000)