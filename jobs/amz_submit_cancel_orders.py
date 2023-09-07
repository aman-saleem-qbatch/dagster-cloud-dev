from dagster import job, in_process_executor
from resources import report_details
from ops.apis.process_cancel_feed import process_cancels


@job(
    executor_def=in_process_executor,
    resource_defs={"report_details": report_details.get_details},
)
def amz_submit_cancel_orders():
    process_cancels()

