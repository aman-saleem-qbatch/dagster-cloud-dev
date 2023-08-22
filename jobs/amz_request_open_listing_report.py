from dagster import op, job
from ops.reports.request_open_listing_report import request_open_listing_report


@job(tags={"job_type": 'amz_request_open_listing_report' })
def amz_request_open_listing_report():
    request_open_listing_report()
