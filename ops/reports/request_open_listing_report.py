import os
from dagster import op
from datetime import datetime
from retrying import retry
from sp_api.api import ReportsV2
from ops.helpers import credentials
from ops.helpers.db_config import db_conn
from models.reports_processing_consumer import ReportsProcessingConsumer
from .. import my_logger, retry_if_error, SP_EXCEPTIONS, pacific_zone

conn = db_conn()


@retry(
    retry_on_exception=retry_if_error,
    stop_max_attempt_number=5,
    wait_fixed=5000,
)
@op
def request_open_listing_report():
    try:
        data = {
            "report_type": 'GET_FLAT_FILE_OPEN_LISTINGS_DATA',
            "marketplace_id": ["ATVPDKIKX0DER"]
        }
        requested_response = ReportsV2(credentials=credentials.sp_credentials()).create_report(
            reportType=data["report_type"],
            marketplaceIds=data["marketplace_id"]
        )
        if requested_response:
            my_logger.info(
                f"\n report_id: {requested_response.payload['reportId']}")
            report_data = ReportsProcessingConsumer(
                report_id=requested_response.payload["reportId"],
                seller_id=os.getenv("seller_id"),
                report_type=data["report_type"],
                marketplace_id=data["marketplace_id"],
                created_at=datetime.now(pacific_zone),
                updated_at=datetime.now(pacific_zone)
            )
            conn.add(report_data)
            conn.commit()

    except SP_EXCEPTIONS as e:
        my_logger.error(str(e))
        raise e
