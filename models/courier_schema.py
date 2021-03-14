from marshmallow import Schema, fields, validate, validates, ValidationError
import datetime


class CourierSchema(Schema):
    courier_id = fields.Integer(required=True, validate=validate.Range(min=1))
    courier_type = fields.String(validate=validate.OneOf(["car", "bike", "foot"]), required=True)
    regions = fields.List(fields.Integer(validate=validate.Range(min=1)), required=True)
    working_hours = fields.List(fields.String, required=True)

    @validates("working_hours")
    def validate_hours(self, intervals):
        time_values = []
        for interval in intervals:
            time_values.extend(interval.split('-'))
        for time_val in time_values:
            try:
                datetime.datetime.strptime(time_val, "%H:%M")
            except ValueError as err:
                raise ValidationError(message="Invalid time: {}".format(time_val)) from err

