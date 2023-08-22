from dagster import job
from ops.apis.process_orders import process_cancel_orders_details


@job(tags={"job_type": 'amz_cancel_orders_downloader' })
def amz_cancel_orders_downloader():
    process_cancel_orders_details()

