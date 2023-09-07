from sqlalchemy import Column, Text, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class CancelQueue(Base):
    __tablename__ = 'cancel_queue'
    cancel_id = Column(
        'cancel_id',
        Integer,
        primary_key=True,
        autoincrement=True
    )
    order_number = Column('order_number', Text)
    order_item_id = Column('order_item_id', Text)
    sku = Column('sku', Text)
    skubana_cancel = Column('skubana_cancel', Integer)
    desktopshipper_cancel = Column('desktopshipper_cancel', Integer)
    amazon_cancel = Column('amazon_cancel', Integer)
    buyer_cancellation_reason = Column('buyer_cancellation_reason', Text)
    buyer_cancel_date = Column('buyer_cancel_date', DateTime)
    purchase_date = Column('purchase_date', DateTime)
    acknowledged_cancel_date_skubana = Column('acknowledged_cancel_date_skubana', DateTime)
    acknowledged_cancel_date_dts = Column('acknowledged_cancel_date_dts', DateTime)
    amazon_cancel_date = Column('amazon_cancel_date', DateTime)
    processing_status = Column('processing_status', Text)
    last_processed_at = Column('last_processed_at', DateTime)
    error_message = Column('error_message', Text)
    created_at = Column('created_at', DateTime)
    updated_at = Column('updated_at', DateTime)

    def __init__(self, order_number):
        self.order_number = order_number

    def __repr__(self):
        return "<CancelQueue: {} {}>".format(self.order_number, self.buyer_cancel_date)
