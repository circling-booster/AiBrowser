from bs4 import BeautifulSoup
from utils.logger import setup_logger

logger = setup_logger("injector")

class Injector:
    def __init__(self, api_port):
        self.api_port = api_port

    def inject(self, html_bytes, script_content=None):
        try:
            soup = BeautifulSoup(html_bytes, 'html.parser')
            
            # 1. Config Injection (Must be first)
            config_tag = soup.new_tag("script")
            config_tag.string = f"window.AiPlugsConfig = {{ apiPort: {self.api_port} }};"
            
            if soup.head:
                soup.head.insert(0, config_tag)
            elif soup.body:
                soup.body.insert(0, config_tag)
            else:
                soup.append(config_tag)

            # 2. Plugin Script Injection
            if script_content:
                script_tag = soup.new_tag("script")
                script_tag.string = script_content
                
                if soup.body:
                    soup.body.append(script_tag)
                else:
                    soup.append(script_tag)

            return soup.encode("utf-8")
        except Exception as e:
            logger.error(f"Injection Error: {e}")
            return html_bytes