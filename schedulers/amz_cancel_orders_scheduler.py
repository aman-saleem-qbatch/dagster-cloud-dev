from dagster import ScheduleDefinition


def amz_cancel_orders_scheduler():
    return ScheduleDefinition(
        cron_schedule="*/30 * * * *",  # every 30 min 
        job_name="amz_cancel_orders_downloader",
        execution_timezone="US/Central",
    )
