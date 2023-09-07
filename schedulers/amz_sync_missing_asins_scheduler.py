from dagster import ScheduleDefinition


def amz_sync_missing_asins_scheduler():
    return ScheduleDefinition(
        cron_schedule="0 */4 * * *",  # every 4 hours
        job_name="amz_sync_missing_asins",
        execution_timezone="US/Central",
    )
