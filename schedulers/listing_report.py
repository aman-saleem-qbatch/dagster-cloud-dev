from dagster import ScheduleDefinition


def listing_report():
    return ScheduleDefinition(
        cron_schedule="0 */12 * * *",  # every 12 hours
        job_name="create_report_job",
        execution_timezone="US/Central",
    )
