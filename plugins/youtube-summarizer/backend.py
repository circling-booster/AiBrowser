from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
# 중요: from core.api_server import inference_mgr 대신 모듈 전체를 import해야
# 초기화 시점에 None이었던 값이 나중에 업데이트된 객체를 참조할 수 있음
from core import api_server

router = APIRouter()

class VideoReq(BaseModel):
    video_id: str

# 로컬 실행 로직을 별도 함수로 분리
async def local_summarize_logic(req: VideoReq):
    # 로컬 추론 시뮬레이션
    await asyncio.sleep(1)
    return {"status": "success", "summary": f"Local processing for {req.video_id} completed."}

@router.post("/summarize")
async def summarize(req: VideoReq):
    # InferenceManager에게 실행 위임
    # req(Pydantic 모델)와 로컬 함수를 전달하면, 설정에 따라 알아서 처리함
    return await api_server.inference_mgr.run(
        plugin_id="youtube-summarizer",
        func_name="summarize",
        request_data=req,
        local_func=local_summarize_logic
    )