from marshmallow import Schema, fields, validate
from validators.time_validators import validate_hours


class OrderSchema(Schema):
    order_id = fields.Integer(required=True, validate=validate.Range(min=1))
    weight = fields.Float(required=True)
    region = fields.Integer(required=True)
    delivery_hours = fields.List(fields.String, required=True, validate=validate_hours)
