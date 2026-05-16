"""
Module Runtime — hosts EV, Trading, and future plugins.
Registers capabilities with the gateway kernel via gRPC.
"""

import asyncio
import logging
import os
import importlib
import sys
from concurrent import futures

import grpc

from services.proto import plugin_host_pb2, plugin_host_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("module-runtime")

GATEWAY_HOST = os.getenv("GATEWAY_HOST", "gateway")
GATEWAY_PORT = os.getenv("GATEWAY_PORT", "50054")
PORT = os.getenv("PORT", "50052")


class PluginHostServicer(plugin_host_pb2_grpc.PluginHostServicer):
    def __init__(self):
        self.plugins = {}

    async def start(self):
        plugins_dir = os.getenv("PLUGINS_DIR", "/app/plugins")
        sys.path.insert(0, os.path.dirname(plugins_dir))
        for plugin_name in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, plugin_name)
            if os.path.isdir(plugin_path) and not plugin_name.startswith("_"):
                try:
                    module = importlib.import_module(f"plugins.{plugin_name}.plugin")
                    if hasattr(module, "plugin"):
                        self.plugins[plugin_name] = module.plugin
                        logger.info(f"Loaded plugin: {plugin_name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_name}: {e}")

    async def ExecuteCapability(self, request, context):
        capability = request.capability
        payload = dict(request.payload)
        for plugin_name, plugin in self.plugins.items():
            manifest = getattr(plugin, "manifest", None)
            caps = getattr(manifest, "capabilities", []) if manifest else []
            if capability in caps:
                try:
                    handler = getattr(plugin, capability.replace(".", "_"), None)
                    if handler:
                        result = await handler(payload)
                        return plugin_host_pb2.ExecuteResponse(
                            success=True, result=str(result)
                        )
                except Exception as e:
                    return plugin_host_pb2.ExecuteResponse(success=False, error=str(e))
        return plugin_host_pb2.ExecuteResponse(
            success=False, error=f"Capability {capability} not found"
        )

    async def HealthCheck(self, request, context):
        return plugin_host_pb2.HealthResponse(
            healthy=True, plugins=list(self.plugins.keys())
        )

    async def RegisterCapabilities(self, request, context):
        self.plugins[request.plugin_name] = request
        logger.info(
            f"Registered plugin: {request.plugin_name} v{request.plugin_version}"
        )
        return plugin_host_pb2.RegisterResponse(
            success=True, message=f"Registered {request.plugin_name}"
        )


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=20))
    servicer = PluginHostServicer()
    await servicer.start()
    plugin_host_pb2_grpc.add_PluginHostServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{PORT}")
    await server.start()
    logger.info(f"Module Runtime listening on port {PORT}")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
