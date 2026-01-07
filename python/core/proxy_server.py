import asyncio
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from .addons.csp_remover import CSPRemover
from .addons.flow_controller import FlowController

def start_proxy_server(proxy_port, api_port):
    async def run():
        opts = options.Options(listen_port=proxy_port)
        # DumpMaster runs headless
        m = DumpMaster(opts, with_termlog=False, with_dumper=False)
        
        m.addons.add(CSPRemover())
        m.addons.add(FlowController(api_port))
        
        try:
            await m.run()
        except KeyboardInterrupt:
            m.shutdown()

    asyncio.run(run())