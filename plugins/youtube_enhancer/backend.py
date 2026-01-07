from fastapi import APIRouter, BackgroundTasks
import time

router = APIRouter(prefix="/yt-dl", tags=["youtube"])

def run_inference_task(video_id: str):
    """
    [User Logic Placeholder]
    여기에 yt-dlp 다운로드 및 Demucs 추론 로직 구현
    """
    print(f"Processing Video: {video_id}...")
    time.sleep(5) # AI 처리 시뮬레이션
    print(f"Finished: {video_id}")

@router.post("/process")
async def process_video(video_id: str, background_tasks: BackgroundTasks):
    # 백그라운드에서 무거운 작업 실행 (UI 블로킹 방지)
    background_tasks.add_task(run_inference_task, video_id)
    return {"status": "queued", "message": "AI Processing Started"}