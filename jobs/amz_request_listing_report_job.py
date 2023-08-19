from dagster import op, job
from ops.reports.create_listing_report import request_listing_report


@job
def amz_request_listing_report_job():
    request_listing_report()
