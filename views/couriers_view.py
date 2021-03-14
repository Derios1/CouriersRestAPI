from aiohttp.web import Response, json_response
from typing import List

from models.db import couriers
from models.courier_schema import CourierSchema
from marshmallow import ValidationError
from asyncpg.exceptions import UniqueViolationError
import json


def _parse_unique_key_error(msg: str) -> int:
    return int(msg.split('=')[1].split()[0].strip('()'))


async def load_couriers(request):
    data = await request.json()
    data = data['data']

    response = {"couriers": []}
    invalid_ids = {
        "validation_error": {
            "couriers": []
        }
    }

    for courier_data in data:
        response["couriers"].append({"id": int(courier_data["courier_id"])})
        try:
            CourierSchema().load(courier_data)
        except ValidationError:
            invalid_ids["validation_error"]["couriers"].append(
                {"id": courier_data["courier_id"]}
            )

    if len(invalid_ids["validation_error"]["couriers"]) == 0:
        try:
            async with request.app['db'].acquire() as connection:
                query = couriers.insert().values(data)
                await connection.execute(query)
        except UniqueViolationError as u_err:
            u_id = _parse_unique_key_error(u_err.detail)
            invalid_ids["validation_error"]["couriers"].append({"id": u_id})

    if len(invalid_ids["validation_error"]["couriers"]) == 0:
        return json_response(json.dumps(response), status=201)
    return json_response(json.dumps(invalid_ids), status=400)


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
