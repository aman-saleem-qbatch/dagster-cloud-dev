from dagster import repository

from jobs import (
    amz_cancel_orders_downloader,
    amz_request_open_listing_report,
    amz_process_done_reports
)
from schedulers import (
    listing_report,
    amz_cancel_orders_scheduler
)
from sensors import (
    processing_sensor
)


@repository
def repo():
    return [
        # Jobs
        amz_request_open_listing_report.amz_request_open_listing_report,
        amz_process_done_reports.amz_process_done_reports,
        amz_cancel_orders_downloader.amz_cancel_orders_downloader,
        # ----------------------------------------------------------
        # Schedulers
        listing_report.listing_report(),
        amz_cancel_orders_scheduler.amz_cancel_orders(),
        # ----------------------------------------------------------
        # Sensors
        processing_sensor.report_process_sensor,
    ]
