from marshmallow import Schema, fields, validate


class CourierSchema(Schema):
    courier_id = fields.Integer(required=True, validate=validate.Range(min=1))
    courier_type = fields.String(validate=validate.OneOf(["car", "bike", "foot"]), required=True)
    regions = fields.List(fields.Integer(), required=True)
    working_hours = fields.List(fields.List(fields.Time(format='%H:%M')), required=True)
