from aiohttp import web
import routes
import asyncpgsa
import config


async def create_app() -> "web.Application":
    app = web.Application()
    routes.set_routes(app)

    app.on_startup.append(on_start)
    app.on_cleanup.append(on_close)

    return app


async def on_start(app: "web.Application"):
    app['db'] = await asyncpgsa.create_pool(dsn=config.database_url)


async def on_close(app: "web.Application"):
    await app['db'].close()
