from mitmproxy import http
import requests
import re

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:5000/injection/scripts"

class Injector:
    def response(self, flow: http.HTTPFlow):
        # 1. CSP 관련 헤더 제거 (Bypass CSP Headers)
        # 브라우저가 보안 정책을 인식하지 못하도록 헤더에서 삭제합니다.
        csp_headers = [
            "Content-Security-Policy",
            "Content-Security-Policy-Report-Only",
            "X-Content-Security-Policy",
            "X-WebKit-CSP"
        ]
        for header in csp_headers:
            if header in flow.response.headers:
                del flow.response.headers[header]

        # 2. HTML 응답인 경우에만 스크립트 주입 및 Meta CSP 제거
        if "text/html" in flow.response.headers.get("content-type", ""):
            # HTML 내부에 <meta http-equiv="Content-Security-Policy" ...> 형태로 포함된 CSP 제거
            # 헤더뿐만 아니라 HTML 내부 정책까지 지워야 완벽한 stealth가 가능합니다.
            html_content = flow.response.text
            html_content = re.sub(
                r'<meta http-equiv=["\']Content-Security-Policy["\'][^>]*>', 
                '', 
                html_content, 
                flags=re.IGNORECASE
            )

            url = flow.request.pretty_url
            
            # FastAPI 서버에 "이 URL에 주입할 스크립트가 있는가?" 문의
            try:
                resp = requests.get(API_URL, params={"url": url}, timeout=0.5)
                data = resp.json()
                scripts = data.get("scripts", [])
            except:
                scripts = []

            if scripts:
                # 스크립트 주입 (Body 닫는 태그 직전)
                injection_code = "<script>" + "\n".join(scripts) + "</script>"
                if "</body>" in html_content:
                    flow.response.text = html_content.replace("</body>", injection_code + "</body>")
                else:
                    flow.response.text = html_content + injection_code
            else:
                # 스크립트 주입이 없더라도 meta CSP가 제거된 HTML 반영
                flow.response.text = html_content

addons = [Injector()]