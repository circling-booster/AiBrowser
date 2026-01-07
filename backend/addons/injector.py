from mitmproxy import http
import requests

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:5000/injection/scripts"

class Injector:
    def response(self, flow: http.HTTPFlow):
        # HTML 응답에만 반응
        if "text/html" in flow.response.headers.get("content-type", ""):
            url = flow.request.pretty_url
            
            # 1. FastAPI 서버에 "이 URL에 주입할 스크립트가 있는가?" 문의
            try:
                resp = requests.get(API_URL, params={"url": url}, timeout=0.5)
                data = resp.json()
                scripts = data.get("scripts", [])
            except:
                scripts = []

            if scripts:
                # 2. 스크립트 주입 (Body 닫는 태그 직전)
                injection_code = "<script>" + "\n".join(scripts) + "</script>"
                html = flow.response.text
                if "</body>" in html:
                    flow.response.text = html.replace("</body>", injection_code + "</body>")
                else:
                    flow.response.text += injection_code

addons = [Injector()]