from sqlalchemy import (Table, Column, Text, Integer,
                        ARRAY, MetaData, Enum as PgEnum,
                        REAL, ForeignKey)

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
                 Column('working_hours', ARRAY(Text), nullable=False),
                 Column('earnings', Integer, default=0),
                 )

orders = Table('orders', meta,
               Column('order_id', Integer, primary_key=True, nullable=False),
               Column('weight', REAL, nullable=False),
               Column('region', Integer, nullable=False),
               Column('delivery_hours', ARRAY(Text), nullable=False),
               Column('courier_id', ForeignKey('couriers.courier_id')),
               Column('assign_time', Text),
               Column('complete_time', Text)
               )
