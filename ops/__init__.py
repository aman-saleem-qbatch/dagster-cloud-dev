from dotenv import load_dotenv
from dagster import get_dagster_logger
from sp_api.base.exceptions import (
    SellingApiRequestThrottledException,
    SellingApiForbiddenException,
    SellingApiServerException,
    SellingApiBadRequestException,
)


load_dotenv()

my_logger = get_dagster_logger()

SP_EXCEPTIONS = (
    SellingApiRequestThrottledException,
    SellingApiBadRequestException,
    SellingApiForbiddenException,
    SellingApiServerException,
    Exception
)


def retry_if_error(exception):
    """Return True if we should retry (in this case when it's an ThrottlingError or TokenExpiryError), False otherwise"""
    return isinstance(
        exception,
        (
            SellingApiRequestThrottledException,
            SellingApiForbiddenException,
            SellingApiServerException,
            SellingApiBadRequestException,
        )
    )
