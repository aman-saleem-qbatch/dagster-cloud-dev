from dagster import job, in_process_executor
from resources import processed_report_details
from ops.reports.save_report import save_report
from ops.reports.get_report_document import get_report_document


@job(
    executor_def=in_process_executor,
    resource_defs={
        "report_details": processed_report_details.get_report_details},
)
def amz_process_continues_reports():
    file_name = get_report_document()
    save_report(file_name)
    print("amz_process_continues_reports FINISHED")
