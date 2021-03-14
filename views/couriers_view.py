from aiohttp.web import Response, json_response
from models.db import couriers
from models.courier_schema import CourierSchema
from marshmallow import ValidationError
from views.basic_view import BasicView
import json


class CourierView(BasicView):
    _namespace = {"name": "couriers", "name_id": "courier_id"}
    _schema = CourierSchema
    _table = couriers

    @staticmethod
    async def change_courier_info(request):
        data = await request.json()

        try:
            CourierSchema().load(data, partial=True)

        except ValidationError:
            return Response(status=400)

        async with request.app['db'].acquire() as connection:
            query = couriers.update().where(
                couriers.c.courier_id == int(request.match_info['courier_id'])).values(data)
            await connection.execute(query)
            query = couriers.select().where(couriers.c.courier_id == int(request.match_info['courier_id']))
            upd_courier = await connection.fetch(query)

        upd_courier = dict(upd_courier[0])

        return json_response(json.dumps(upd_courier), status=200)



