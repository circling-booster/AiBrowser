from mitmproxy import http

class CSPRemover:
    def response(self, flow: http.HTTPFlow):
        # Strip CSP headers to allow arbitrary script injection
        headers = [
            "Content-Security-Policy",
            "Content-Security-Policy-Report-Only",
            "X-Frame-Options"
        ]
        for h in headers:
            if h in flow.response.headers:
                del flow.response.headers[h]