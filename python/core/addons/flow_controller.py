import json
import re
import os
from mitmproxy import http, tls
from ..injector import Injector
from utils.logger import setup_logger

logger = setup_logger("flow_controller")

class FlowController:
    def __init__(self, api_port):
        self.injector = Injector(api_port)
        self.passthrough_hosts = []
        self.plugin_scripts = []
        self.load_config()
        self.load_scripts()

    def load_config(self):
        try:
            with open("config/settings.json", "r") as f:
                data = json.load(f)
                self.passthrough_hosts = data.get("passthrough_hosts", [])
        except:
            self.passthrough_hosts = ["*.google.com"]

    def load_scripts(self):
        # Preload plugin scripts
        p_dir = "plugins"
        if not os.path.exists(p_dir): return
        
        for pid in os.listdir(p_dir):
            path = os.path.join(p_dir, pid)
            man_path = os.path.join(path, "manifest.json")
            js_path = os.path.join(path, "inject.js")
            
            if os.path.exists(man_path) and os.path.exists(js_path):
                with open(man_path, 'r') as f: manifest = json.load(f)
                with open(js_path, 'r') as f: code = f.read()
                
                for target in manifest.get("injection_targets", []):
                    self.plugin_scripts.append({
                        "regex": target["url_regex"],
                        "code": code
                    })

    def tls_clienthello(self, data: tls.ClientHelloData):
        # SSL Pinning Evasion / Passthrough
        # Checks if the host is in the ignore list and skips interception
        try:
            sni = data.client_hello.sni
            if not sni: return

            for pattern in self.passthrough_hosts:
                regex = pattern.replace(".", r"\.").replace("*", ".*")
                if re.match(regex, sni):
                    data.ignore_connection = True
                    return
        except:
            pass

    def response(self, flow: http.HTTPFlow):
        # Injection Logic
        ctype = flow.response.headers.get("Content-Type", "")
        if "text/html" not in ctype: return

        url = flow.request.pretty_url
        script_to_inject = None
        
        for item in self.plugin_scripts:
            if re.search(item["regex"], url):
                script_to_inject = item["code"]
                break
        
        # Always inject config, optionally inject script
        flow.response.content = self.injector.inject(flow.response.content, script_to_inject)