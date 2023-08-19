from sqlalchemy import Column, Text, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class LastUpdatedTracker(Base):
    __tablename__ = 'last_updated_tracker'
    id = Column(
        'id',
        Integer,
        primary_key=True,
        autoincrement=True
    )
    tracker_type = Column('tracker_type', Text)
    last_updated_at = Column('last_updated_at', DateTime)
    created_at = Column('created_at', DateTime)
    updated_at = Column('updated_at', DateTime)

    def __init__(self, tracker_type, last_updated_at):
        self.tracker_type = tracker_type
        self.last_updated_at = last_updated_at

    def __repr__(self):
        return "<LastUpdatedTracker: {} {}>".format(self.tracker_type, self.last_updated_at)
