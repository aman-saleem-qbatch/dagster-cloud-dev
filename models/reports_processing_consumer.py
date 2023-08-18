from sqlalchemy import Column, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Reports_Processing_Consumer(Base):
    __tablename__ = 'reports_processing_consumer'
    report_id = Column('report_id', Integer, primary_key=True)
    seller_id = Column('seller_id', Text)
    report_type = Column('report_type', Text)
    marketplace_id = Column('marketplace_id', Text)
    created_at = Column('created_at', DateTime)
    updated_at = Column('updated_at', DateTime)

    def __init__(self, report_id, seller_id, report_type, marketplace_id, created_at, updated_at):
        self.report_id = report_id
        self.seller_id = seller_id
        self.report_type = report_type
        self.marketplace_id = marketplace_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<Reports_Processing_Consumer: {} {}>".format(self.report_id, self.report_type)
