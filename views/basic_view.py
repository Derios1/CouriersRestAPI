from marshmallow import Schema, ValidationError
from asyncpg.exceptions import UniqueViolationError
from abc import ABCMeta, abstractmethod
from aiohttp.web import Response, json_response
import json


class BasicView(metaclass=ABCMeta):
    @property
    @abstractmethod
    def _namespace(self):
        pass

    @property
    @abstractmethod
    def _schema(self):
        pass

    @property
    @abstractmethod
    def _table(self):
        pass

    @staticmethod
    def _parse_unique_key_error(msg: str) -> int:
        return int(msg.split('=')[1].split()[0].strip('()'))

    @classmethod
    async def load_data(cls, request):
        data = await request.json()
        data = data['data']

        name, id_name = cls._namespace["name"], cls._namespace["name_id"]
        response = {name: []}
        invalid_ids = {
            "validation_error": {
                name: []
            }
        }

        for value_data in data:
            response[name].append({"id": int(value_data[id_name])})
            try:
                cls._schema().load(value_data)
            except ValidationError:
                invalid_ids["validation_error"][name].append(
                    {"id": value_data[id_name]}
                )

        if len(invalid_ids["validation_error"][name]) == 0:
            try:
                async with request.app['db'].acquire() as connection:
                    query = cls._table.insert().values(data)
                    await connection.execute(query)
            except UniqueViolationError as u_err:
                u_id = cls._parse_unique_key_error(u_err.detail)
                invalid_ids["validation_error"][name].append({"id": u_id})

        if len(invalid_ids["validation_error"][name]) == 0:
            return json_response(json.dumps(response), status=201)
        return json_response(json.dumps(invalid_ids), status=400)
