from dagster import repository

from jobs import (
    amz_cancel_orders_downloader,
)

from schedulers import (
    amz_cancel_orders_scheduler
)


@repository
def repo():
    return [
        # Jobs
       amz_cancel_orders_downloader.amz_cancel_orders_downloader,
        # Schedulers
       amz_cancel_orders_scheduler.amz_cancel_orders()
        # Sensors        
    ]
