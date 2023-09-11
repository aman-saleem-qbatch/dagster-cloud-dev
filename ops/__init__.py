import pytz
from dotenv import load_dotenv
from dagster import get_dagster_logger
from requests import exceptions
from sp_api.base.exceptions import (
    SellingApiRequestThrottledException,
    SellingApiForbiddenException,
    SellingApiServerException,
    SellingApiBadRequestException,
    SellingApiTemporarilyUnavailableException,
    SellingApiGatewayTimeoutException
)

pacific_zone = pytz.timezone('US/Pacific')

load_dotenv()

my_logger = get_dagster_logger()

SP_EXCEPTIONS = (
    Exception,
    SellingApiRequestThrottledException,
    SellingApiForbiddenException,
    SellingApiServerException,
    SellingApiBadRequestException,
    SellingApiTemporarilyUnavailableException,
    SellingApiGatewayTimeoutException,
    exceptions.SSLError
)


def retry_if_error(exception):
    """Return True if we should retry (in this case when it's an ThrottlingError or TokenExpiryError), False otherwise"""
    return isinstance(
        exception,
        (
            SellingApiRequestThrottledException,
            SellingApiServerException,
            SellingApiTemporarilyUnavailableException,
            SellingApiGatewayTimeoutException,
            exceptions.SSLError
        )
    )
