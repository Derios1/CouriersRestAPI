from marshmallow import Schema, fields, validate
from validators.time_validators import validate_hours

courier_weights = {'foot': 10, 'bike': 15, 'car': 50}
courier_prices_c = {'foot': 2, 'bike': 5, 'car': 9}


class CourierSchema(Schema):
    courier_id = fields.Integer(required=True, validate=validate.Range(min=1))
    courier_type = fields.String(validate=validate.OneOf(["car", "bike", "foot"]), required=True)
    regions = fields.List(fields.Integer(validate=validate.Range(min=1)), required=True)
    working_hours = fields.List(fields.String, required=True, validate=validate_hours)
