from aiohttp.web import Application
from views.couriers_view import CourierView
from views.orders_view import OrdersView


def set_routes(app: "Application"):
    app.router.add_post("/couriers", CourierView.load_data)
    app.router.add_patch(r"/couriers/{courier_id:[1-9][0-9]*}", CourierView.change_courier_info)
    app.router.add_post("/orders", OrdersView.load_data)
