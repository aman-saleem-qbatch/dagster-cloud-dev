from sqlalchemy import Column, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class AmazonInventoryReport(Base):
    __tablename__ = "amazon_inventory_report"
    sku = Column("sku", Text, primary_key=True)
    asin = Column("asin", Text)
    price = Column("price", Text)
    quantity = Column("quantity", Text)

    def __init__(self, sku, asin):
        self.sku = sku
        self.asin = asin

    def __repr__(self):
        return "<AmazonInventoryReport: {} {}>".format(self.sku, self.asin)
