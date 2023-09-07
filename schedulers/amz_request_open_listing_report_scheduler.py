from dagster import ScheduleDefinition


def amz_request_open_listing_report_scheduler():
    return ScheduleDefinition(
        cron_schedule="0 */12 * * *",  # every 12 hours
        job_name="amz_request_open_listing_report",
        execution_timezone="US/Central",
    )
