from sqlalchemy import Column, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AmazonInventoryReport(Base):
    __tablename__ = 'amazon_inventory_report'
    sku = Column('sku', Text, primary_key=True)
    asin = Column('asin', Text)
    price = Column('price', Text)
    quantity = Column('quantity', Text)
    marketplace_id = Column('marketplace_id', Text)
    business_price = Column('Business Price', Text)
    quantity_price_type = Column('Quantity Price Type', Text)
    quantity_lower_bound_1 = Column('Quantity Lower Bound 1', Text)
    quantity_price_1 = Column('Quantity Price 1', Text)
    quantity_lower_bound_2 = Column('Quantity Lower Bound 2', Text)
    quantity_price_2 = Column('Quantity Price 2', Text)
    quantity_lower_bound_3 = Column('Quantity Lower Bound 3', Text)
    quantity_price_3 = Column('Quantity Price 3', Text)
    quantity_lower_bound_4 = Column('Quantity Lower Bound 4', Text)
    quantity_price_4 = Column('Quantity Price 4', Text)
    quantity_lower_bound_5 = Column('Quantity Lower Bound 5', Text)
    quantity_price_5 = Column('Quantity Price 5', Text)
    created_at = Column('created_at', DateTime)
    updated_at = Column('updated_at', DateTime)

    def __init__(self, sku, asin):
        self.sku = sku
        self.asin = asin

    def __repr__(self):
        return "<AmazonInventoryReport: {} {}>".format(self.sku, self.asin)
