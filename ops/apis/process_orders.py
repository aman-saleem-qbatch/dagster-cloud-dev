from .. import my_logger
from dagster import op
from datetime import datetime, timedelta, time as dtime
from models.last_updated_tracker import LastUpdatedTracker
from ops.apis.helpers.orders_processor import process_cancel_orders


"""
Check Last Updated time of the Order & Update Order's Cancellation Queue 
Accordingly Using Sp Api GetOrders & GetOrderItems Endpoints
"""

@op
def process_cancel_orders_details():
    try:
        last_tracker = LastUpdatedTracker.where(
            "tracker_type", "orders"
        ).first()        
        # end_of_hour
        t_end_date = datetime.now()
        end_date = t_end_date.replace(minute=0, second=0, microsecond=0) - timedelta(minutes=3)

        delta = timedelta(days=1)   

        if last_tracker:
            my_logger.info(f"Record existed |  {last_tracker.last_updated_at.timestamp()}")
            # start_of_hour
            start_date = datetime.fromtimestamp(last_tracker.last_updated_at.timestamp())
            start_date = start_date.replace(minute=0, second=0, microsecond=0)
        else:
            my_logger.info("Record not existed running job from the start of the month")
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
