from models.db import orders
from models.orders_schema import OrderSchema
from views.basic_view import BasicView


class OrdersView(BasicView):
    _namespace = {"name": "orders", "name_id": "order_id"}
    _schema = OrderSchema
    _table = orders
