from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class VideoReq(BaseModel):
    video_id: str

@router.post("/summarize")
def summarize(req: VideoReq):
    return {"status": "success", "summary": f"Mock summary for video {req.video_id}."}