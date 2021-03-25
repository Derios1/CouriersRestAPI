from models.db import orders, couriers
from models.orders_schema import OrderSchema
from views.basic_view import BasicView
from aiohttp.web import Response, json_response
from datetime import datetime
from models.courier_schema import courier_weights, courier_prices_c
from sqlalchemy import and_
import json


class OrdersView(BasicView):
    _namespace = {"name": "orders", "name_id": "order_id"}
    _schema = OrderSchema
    _table = orders

    @staticmethod
    def is_intervals_intersect(int1, int2) -> bool:
        """""""""
        Check if there are some intersections between
        time intervals of courier and order 
        """""""""
        left = max(int1[0], int2[0])
        right = min(int1[1], int2[1])

        return left <= right

    @staticmethod
    def is_order_acceptable(courier: dict,
                            order: dict) -> bool:
        if not (order['region'] in courier['regions']):
            return False
        working_hours = list(map(lambda s: list(map(lambda spl: datetime.strptime(spl, "%H:%M"),
                                                    s.split('-'))), courier['working_hours']))
        delivery_hours = list(map(lambda s: list(map(lambda spl: datetime.strptime(spl, "%H:%M"),
                                                     s.split('-'))), order['delivery_hours']))

        i, j = 0, 0
        while i < len(working_hours) and j < len(delivery_hours):
            if OrdersView.is_intervals_intersect(working_hours[i], delivery_hours[j]):
                return True

            if working_hours[i][1] < delivery_hours[j][1]:
                i += 1
            else:
                j += 1
        return False

    @staticmethod
    async def assign_orders(request):
        data = await request.json()
        cour_id = data['courier_id']

        async with request.app['db'].acquire() as connection:
            query = orders.select()
            orders_table = await connection.fetch(query)
            query = couriers.select().where(couriers.c.courier_id == int(cour_id))
            courier_info = await connection.fetch(query)

        try:
            courier_info = dict(courier_info[0])
        except IndexError:
            return Response(status=400)

        cour_weight = courier_weights[courier_info['courier_type']]
        acceptable_orders = []

        for order in orders_table:
            order_info = dict(order)
            if order_info['courier_id'] == cour_id and order_info['complete_time'] == '':
                cour_weight -= float(order_info['weight'])
            if order_info['assign_time'] == '' and \
                    OrdersView.is_order_acceptable(courier_info, order_info):
                acceptable_orders.append(order_info)

        optimized_orders = []
        assign_time = datetime.now().isoformat() + 'Z'
        response_data = {"orders": [], "assign_time": assign_time}
        for order in sorted(acceptable_orders, key=lambda a: float(a['weight'])):
            if cour_weight >= float(order['weight']):
                optimized_orders.append(order)
                response_data["orders"].append({"id": order["order_id"]})
                order['courier_id'] = cour_id
                order['assign_time'] = assign_time
                cour_weight -= float(order['weight'])
            else:
                break

        async with request.app['db'].acquire() as connection:
            for order in optimized_orders:
                query = orders.update().where(orders.c.order_id == int(order['order_id'])).values(order)
                await connection.execute(query)

        if len(response_data['orders']) == 0:
            del response_data['assign_time']
        return json_response(json.dumps(response_data), status=200)

    @staticmethod
    async def set_completed_order(request):
        data = await request.json()

        upd_time = {'complete_time': data['complete_time']}

        async with request.app['db'].acquire() as connection:
            query = orders.update().where(and_(orders.c.order_id == int(data['order_id']),
                                          orders.c.courier_id == int(data['courier_id']))
                                          ).values(upd_time)
            res = await connection.execute(query)

            if res.split()[1] == '0':
                return Response(status=400)

            query = couriers.select().where(couriers.c.courier_id == int(data['courier_id']))
            cour_info = await connection.fetch(query)
            cour_info = dict(cour_info[0])
            cour_info['earnings'] += 500*courier_prices_c[cour_info['courier_type']]
            query = couriers.update().where(couriers.c.courier_id == int(data['courier_id'])).values(cour_info)

            await connection.execute(query)

        return json_response(json.dumps({'order_id': data['order_id']}), status=200)
