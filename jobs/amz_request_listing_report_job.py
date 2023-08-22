from dagster import op, job
from ops.reports.create_listing_report import request_listing_report


@job(tags={"job_type": 'amz_request_listing_report_job' })
def amz_request_listing_report_job():
    request_listing_report()
