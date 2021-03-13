from aiohttp.web import Application
from views.couriers_view import *


def set_routes(app: "Application"):
    app.router.add_post("/couriers", load_couriers)
