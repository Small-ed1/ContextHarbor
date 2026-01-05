#!/usr/bin/env python3
"""
Simple reverse proxy for Kiwix from laptop-server
"""
import asyncio
import logging

import aiohttp
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def proxy_handler(request):
    """Proxy requests to laptop-server Kiwix"""
    path = request.path_qs

    # Ensure path starts with /kiwix
    if not path.startswith("/kiwix"):
        return web.Response(text="Not found", status=404)

    target_url = f"http://127.0.0.1:8080{path}"

    try:
        async with aiohttp.ClientSession() as session:
            # Forward the request
            headers = {
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ["host", "connection"]
            }

            async with session.request(
                request.method,
                target_url,
                headers=headers,
                data=await request.read()
                if request.method in ["POST", "PUT", "PATCH"]
                else None,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                # Forward the response
                response_data = await resp.read()
                return web.Response(
                    body=response_data,
                    status=resp.status,
                    headers={
                        k: v
                        for k, v in resp.headers.items()
                        if k.lower() not in ["content-encoding", "transfer-encoding"]
                    },
                )

    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return web.Response(text=f"Proxy error: {str(e)}", status=500)


async def init_app():
    app = web.Application()
    app.router.add_route("*", "/{path:kiwix.*}", proxy_handler)
    return app


if __name__ == "__main__":
    app = asyncio.run(init_app())
    web.run_app(app, host="127.0.0.1", port=18080)
