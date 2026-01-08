import json
import httpx
import asyncio
import os
from utils.logger import setup_logger

logger = setup_logger("inference_manager")

class InferenceManager:
    def __init__(self, plugins_manifests):
        self.manifests = plugins_manifests
        self.config_path = "config/settings.json"

    def _get_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        return {}

    def get_effective_mode(self, plugin_id):
        config = self._get_config()
        manifest = self.manifests.get(plugin_id, {})
        inf_conf = manifest.get("inference_config", {})

        # 1. Manifest 제약 사항 (기본값 설정)
        allowed = inf_conf.get("allowed_modes", ["local", "web"])
        preferred = inf_conf.get("preferred_inference", "local")

        # 2. 사용자 설정 확인 (Settings.json)
        user_override = config.get("plugins", {}).get(plugin_id, {}).get("inference_mode")

        # 3. 최종 모드 결정
        mode = user_override if user_override else preferred

        # 4. 유효성 검증 (지원하지 않는 모드 강제 시 fallback)
        if mode not in allowed:
            logger.warning(f"Plugin {plugin_id} mode '{mode}' is not allowed. Falling back to '{preferred}'.")
            mode = preferred

        return mode

    async def run(self, plugin_id, func_name, request_data, local_func):
        """
        추론을 로컬 함수로 실행할지, 웹 릴레이로 보낼지 결정하여 실행합니다.
        
        Args:
            plugin_id: 플러그인 ID
            func_name: 실행할 함수(엔드포인트) 이름
            request_data: 요청 데이터 (Pydantic 모델 또는 dict)
            local_func: 로컬 실행 시 호출할 함수 객체
        """
        mode = self.get_effective_mode(plugin_id)
        config = self._get_config()

        # Web 요청을 위해 데이터가 Pydantic 모델인 경우 dict로 변환
        if hasattr(request_data, "dict"):
            payload = request_data.dict()
        else:
            payload = request_data

        if mode == "web":
            # Web Inference (Azure Relay)
            base_url = config.get("azure_relay_url", "").rstrip("/")
            if not base_url:
                return {"error": "Azure Relay URL is not configured."}
                
            target = f"{base_url}/api/{plugin_id}/{func_name}"
            
            async with httpx.AsyncClient() as client:
                try:
                    # 타임아웃 30초 설정
                    resp = await client.post(target, json=payload, timeout=30.0)
                    if resp.status_code >= 400:
                        return {"error": f"Web inference failed: {resp.text}"}
                    return resp.json()
                except Exception as e:
                    logger.error(f"Web request error: {e}")
                    return {"error": str(e)}
        else:
            # Local Inference
            try:
                if asyncio.iscoroutinefunction(local_func):
                    return await local_func(request_data)
                else:
                    return local_func(request_data)
            except Exception as e:
                logger.error(f"Local execution error: {e}")
                return {"error": str(e)}