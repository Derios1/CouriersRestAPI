import datetime
from marshmallow import ValidationError


def validate_hours(intervals):
    time_values = []
    for interval in intervals:
        time_values.extend(interval.split('-'))
    for time_val in time_values:
        try:
            datetime.datetime.strptime(time_val, "%H:%M")
        except ValueError as err:
            raise ValidationError(message="Invalid time: {}".format(time_val)) from err
