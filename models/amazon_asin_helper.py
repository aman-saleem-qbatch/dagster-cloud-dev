from sqlalchemy import Column, Text, Integer
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class AmazonAsinHelper(Base):
    __tablename__ = 'amazon_asinhelper'
    product_id = Column('product_id', Integer, primary_key=True)
    variant_id = Column('variant_id', Text)
    asin = Column('asin', Text)
    upc = Column('upc', Text)

    def __init__(self, product_id, variant_id=None, upc=None, asin=None):
        self.produc_id = product_id
        self.variant_id = variant_id
        self.upc = upc
        self.asin = asin

    def __repr__(self):
        return "<AmazonAsinHelper {}, {}, {}, {}>".format(self.product_id, self.variant_id, self.upc, self.asin)
