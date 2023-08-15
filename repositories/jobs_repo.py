from dagster import repository

from sensors import (
    processing_sensor
)
from schedulers import (
    listing_report
)
from jobs import (
    create_report_job,
    amz_process_continues_reports
)


@repository
def repo():
    return [
        # Jobs
        create_report_job.create_report_job,
        amz_process_continues_reports.amz_process_continues_reports,
        # Schedulars
        listing_report.listing_report(),
        # Sensors
        processing_sensor.report_process_sensor
    ]
