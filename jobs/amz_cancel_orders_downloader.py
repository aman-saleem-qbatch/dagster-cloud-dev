from dagster import job
from ops.apis.process_orders import process_cancel_orders_details


@job
def amz_cancel_orders_downloader():
    process_cancel_orders_details()

