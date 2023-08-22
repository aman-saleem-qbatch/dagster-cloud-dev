from dagster import op
from datetime import datetime, timedelta, time as dtime
from sqlalchemy import select
from models.last_updated_tracker import LastUpdatedTracker
from ops.apis.helpers.orders_processor import process_cancel_orders
from .. import my_logger
from ..helpers.db_config import db_conn

conn = db_conn()

"""
Check Last Updated time of the Order & Update Order's Cancellation Queue 
Accordingly Using Sp Api GetOrders & GetOrderItems Endpoints
"""


@op
def process_cancel_orders_details():
    try:
        # end_of_hour
        t_end_date = datetime.now()
        end_date = t_end_date.replace(
            minute=0, second=0, microsecond=0) - timedelta(minutes=5)

        delta = timedelta(days=1)

        stmt = (
            select(LastUpdatedTracker.last_updated_at)
            .where(LastUpdatedTracker.tracker_type == 'orders')
        )
        last_tracker = conn.execute(stmt).scalar()
        if last_tracker:
            my_logger.info(f"Record existed |  {last_tracker}")
            # start_of_hour
            start_date = last_tracker.replace(
                minute=0, second=0, microsecond=0)
        else:
            my_logger.info(
                "Record not existed running job from the start of the month")
            # start_of_hour and start of the month
            temp_date = datetime.combine(datetime.now(), dtime.min)
            start_date = temp_date.replace(day=1)

        my_logger.info(
            f"TOTAL SYNCABLE TIME {start_date.isoformat()} -  {end_date.isoformat()}"
        )
        while start_date < end_date:
            posted_after = start_date.isoformat()
            start_date += delta
            if start_date < end_date:
                posted_before = (start_date).isoformat()
            else:
                posted_before = end_date.isoformat()

            # Processing order details for specific interval
            process_cancel_orders(posted_after, posted_before)

    except Exception as e:
        my_logger.error(f"error {e}")
        return False
