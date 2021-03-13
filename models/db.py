from sqlalchemy import Table, Column, Text, Integer, ARRAY, MetaData, Enum as PgEnum

from enum import Enum, unique


@unique
class CourierType(Enum):
    car = "car"
    bike = "bike"
    foot = "foot"


meta = MetaData()
couriers = Table('couriers', meta,
                 Column('courier_id', Integer, primary_key=True, nullable=False),
                 Column('courier_type', PgEnum(CourierType, name="courier_type"), nullable=False),
                 Column('regions', ARRAY(Integer), nullable=False),
                 Column('working_hours', ARRAY(Text), nullable=False)
                 )
