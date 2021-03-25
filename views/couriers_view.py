from aiohttp.web import Response, json_response
from models.db import couriers, orders
from models.courier_schema import CourierSchema, courier_weights
from marshmallow import ValidationError
from views.basic_view import BasicView
from views.orders_view import OrdersView
from math import inf
import datetime
import json


class CourierView(BasicView):
    _namespace = {"name": "couriers", "name_id": "courier_id"}
    _schema = CourierSchema
    _table = couriers

    @staticmethod
    def __get_orders_to_reassign(courier: dict, orders_table: list):
        courier_capacity = courier_weights[courier['courier_type']]
        orders_to_reassign = []
        for order in orders_table:
            dict_order = dict(order)
            if order['complete_time'] != '':
                continue
            if (dict_order['region'] not in courier['regions']
                    or not OrdersView.is_order_acceptable(courier, dict_order)):
                orders_to_reassign.append(dict_order)
                orders_table.remove(order)
            else:
                courier_capacity -= order['weight']

        orders_table.sort(key=lambda a: dict(a)['weight'])
        pointer = len(orders_table) - 1

        while courier_capacity < 0:
            if orders_table[pointer]['complete_time'] == '':
                orders_to_reassign.append(orders_table[pointer])
                courier_capacity += orders_table[pointer]['weight']
            pointer -= 1

        return orders_to_reassign

    @staticmethod
    async def change_courier_info(request):
        data = await request.json()
        cour_id = int(request.match_info['courier_id'])

        try:
            CourierSchema().load(data, partial=True)

        except ValidationError:
            return Response(status=400)

        async with request.app['db'].acquire() as connection:
            query = couriers.update().where(
                couriers.c.courier_id == cour_id).values(data)
            await connection.execute(query)

            query = couriers.select().where(couriers.c.courier_id == cour_id)
            upd_courier = await connection.fetch(query)
            upd_courier = dict(upd_courier[0])
            query = orders.select().where(orders.c.courier_id == cour_id)
            orders_table = await connection.fetch(query)
            orders_to_reassign = CourierView.__get_orders_to_reassign(upd_courier, orders_table)

            for order in orders_to_reassign:
                order['courier_id'] = None
                order['assign_time'] = ''
                query = orders.update().where(orders.c.order_id == order['order_id']).values(order)
                await connection.execute(query)

        return json_response(json.dumps(upd_courier), status=200)

    @staticmethod
    def __min_average_time(orders_by_region: dict):
        min_average = inf
        for region in orders_by_region:
            orders_by_region[region].sort(
                key=lambda a: datetime.datetime.strptime(a['complete_time'],
                                                         "%Y-%m-%dT%H:%M:%S.%fZ"))
            delta_sum = 0
            for i in range(len(orders_by_region[region])):
                order = orders_by_region[region][i]
                t2 = datetime.datetime.strptime(order['complete_time'],
                                                "%Y-%m-%dT%H:%M:%S.%fZ")
                if i == 0:
                    t1 = datetime.datetime.strptime(order['assign_time'],
                                                    "%Y-%m-%dT%H:%M:%S.%fZ")
                else:
                    prev_order = orders_by_region[region][i - 1]
                    t1 = datetime.datetime.strptime(prev_order['complete_time'],
                                                    "%Y-%m-%dT%H:%M:%S.%fZ")
                delta_sum += (t2 - t1).total_seconds()
            min_average = min(min_average, delta_sum / len(orders_by_region[region]))
        return min_average

    @staticmethod
    async def get_cour_info(request):
        cour_id = int(request.match_info['courier_id'])
        async with request.app['db'].acquire() as connection:
            query = couriers.select().where(couriers.c.courier_id == cour_id)
            cour_info = await connection.fetch(query)
            cour_info = dict(cour_info[0])

            query = orders.select().where(orders.c.courier_id == cour_id)
            cour_orders = await connection.fetch(query)

            if len(cour_orders) == 0:
                return json_response(json.dumps(cour_info))

            orders_by_region = {}

            for order in cour_orders:
                order = dict(order)
                if order['region'] in orders_by_region:
                    orders_by_region[order['region']].append(order)
                else:
                    orders_by_region[order['region']] = [order]

            min_average = CourierView.__min_average_time(orders_by_region)

            cour_info['rating'] = (60 * 60 - min(60 * 60, min_average)) / (60 * 60) * 5

        return json_response(json.dumps(cour_info), status=200)
