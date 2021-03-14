from aiohttp.web import Application
from views.couriers_view import *


def set_routes(app: "Application"):
    app.router.add_post("/couriers", load_couriers)
    app.router.add_patch(r"/couriers/{courier_id:[1-9][0-9]*}", change_courier_info)
