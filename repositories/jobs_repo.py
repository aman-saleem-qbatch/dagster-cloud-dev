from dagster import repository

from jobs import (
    amz_cancel_orders_downloader,
    amz_submit_cancel_orders,
    amz_request_open_listing_report,
    amz_process_done_reports,
    amz_sync_missing_asins
)
from schedulers import (
    amz_cancel_orders_scheduler,
    amz_request_open_listing_report_scheduler,
    amz_sync_missing_asins_scheduler
)
from sensors import (
    processing_sensor,
    amz_submit_cancel_order_sensor
)


@repository
def repo():
    return [
        # Jobs
        amz_request_open_listing_report.amz_request_open_listing_report,
        amz_process_done_reports.amz_process_done_reports,
        amz_cancel_orders_downloader.amz_cancel_orders_downloader,
        amz_submit_cancel_orders.amz_submit_cancel_orders,
        amz_sync_missing_asins.amz_sync_missing_asins,
        # ----------------------------------------------------------
        # Schedulers
        amz_cancel_orders_scheduler.amz_cancel_orders_scheduler(),
        amz_request_open_listing_report_scheduler.amz_request_open_listing_report_scheduler(),
        amz_sync_missing_asins_scheduler.amz_sync_missing_asins_scheduler(),
        # ----------------------------------------------------------
        # Sensors
        processing_sensor.report_process_sensor,
        amz_submit_cancel_order_sensor.process_submit_cancel_orders
    ]
