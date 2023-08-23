import os
import json
import requests
from dagster import op
from retrying import retry
from sp_api.api import Reports
from ops.helpers import credentials
from .. import my_logger


def retry_if_requests_error(exception):
    """Return True if we should retry (in this case when it's an IOError), False otherwise"""
    return isinstance(exception, requests.exceptions.ConnectionError)


@retry(
    retry_on_exception=retry_if_requests_error,
    stop_max_attempt_number=3,
    wait_fixed=3000,
)
@op(required_resource_keys={"report_details"})
def get_report_document(context):
    result = context.resources.report_details
    data = json.loads(result["data"])
    if data:
        path = "./reports_temp"
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        file_name = f"reports_temp/Report-{data['seller_id']}-{data['report_type']}.tsv"
        try:
            report = Reports(credentials=credentials.sp_credentials()).get_report_document(
                data["reportDocumentId"], decrypt=True, file=file_name
            )
            return file_name
        except (requests.exceptions.ConnectionError) as e:
            my_logger.error(e)
            raise e
    else:
        my_logger.info('No report found')
        return False
