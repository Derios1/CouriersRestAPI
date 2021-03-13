from aiohttp.web import Response, json_response
from typing import List

from models.db import couriers
from models.courier_schema import CourierSchema
from marshmallow import ValidationError
from asyncpg.exceptions import UniqueViolationError
import json


def _parse_time_intervals(intervals: List[str]):
    for i in range(len(intervals)):
        intervals[i] = intervals[i].split('-')


def _parse_unique_key_error(msg: str) -> int:
    return int(msg.split('=')[1].split()[0].strip('()'))


async def load_couriers(request):
    data = await request.json()
    data = data['data']

    values = []
    response = {"couriers": []}
    invalid_ids = {
        "validation_error": {
            "couriers": []
        }
    }

    for courier_data in data:
        response["couriers"].append({"id": int(courier_data["courier_id"])})
        values.append({
            "courier_id": courier_data["courier_id"],
            "courier_type": courier_data["courier_type"],
            "regions": courier_data["regions"],
            "working_hours": courier_data["working_hours"]
        })
        try:
            courier_hours = values[-1]["working_hours"].copy()
            _parse_time_intervals(courier_hours)
            CourierSchema().validate(values[-1])
        except ValueError:
            invalid_ids["validation_error"]["couriers"].append(
                {"id": values[-1]["courier_id"]}
            )

    try:
        async with request.app['db'].acquire() as connection:
            query = couriers.insert().values(values)
            await connection.execute(query)
    except UniqueViolationError as u_err:
        u_id = _parse_unique_key_error(u_err.detail)
        invalid_ids["validation_error"]["couriers"].append({"id": u_id})

    if len(invalid_ids["validation_error"]["couriers"]) == 0:
        return json_response(json.dumps(response), status=201)
    return json_response(json.dumps(invalid_ids), status=400)
