import os
import json
from dagster import op
from retrying import retry
from sp_api.api import Reports
from ops.helpers import credentials
from .. import my_logger, retry_if_error, SP_EXCEPTIONS


@retry(
    retry_on_exception=retry_if_error,
    stop_max_attempt_number=5,
    wait_fixed=5000,
)
@op(required_resource_keys={"report_details"})
def get_report_document(context):
    try:
        result = context.resources.report_details
        data = json.loads(result["data"])
        if data:
            path = "./reports_temp"
            isExist = os.path.exists(path)
            if not isExist:
                os.makedirs(path)
            file_name = f"reports_temp/Report-{data['seller_id']}-{data['report_type']}.tsv"

            report = Reports(credentials=credentials.sp_credentials()).get_report_document(
                data["reportDocumentId"], decrypt=True, file=file_name
            )
            if report.payload:
                return file_name
            else:
                return None
        else:
            my_logger.info('No report found')
            return False

    except SP_EXCEPTIONS as e:
        my_logger.error(e)
        raise e
