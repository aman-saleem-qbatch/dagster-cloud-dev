import os
from dagster import op
from datetime import datetime
from sp_api.api import ReportsV2
from ops.helpers import credentials
from models.reports_processing_consumer import ReportsProcessingConsumer
from .. import my_logger


@op
def request_listing_report():
    data = {
        "report_type": 'GET_MERCHANT_LISTINGS_ALL_DATA',
        "marketplace_id": ["ATVPDKIKX0DER"]
    }
    try:
        requested_response = ReportsV2(credentials=credentials.sp_credentials()).create_report(
            reportType=data["report_type"],
            marketplaceIds=data["marketplace_id"]
        )
    except Exception as e:
        my_logger.error(str(e))
        requested_response = None

    if requested_response:
        my_logger.info(
            f"\n report_id: {requested_response.payload['reportId']}")
        report_data = ReportsProcessingConsumer.insert(
            {
                "report_id": requested_response.payload["reportId"],
                "seller_id": os.getenv("seller_id"),
                "report_type": data["report_type"],
                "marketplace_id": data["marketplace_id"],
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )
        my_logger.info(
            f"\n report_data: {report_data}")
