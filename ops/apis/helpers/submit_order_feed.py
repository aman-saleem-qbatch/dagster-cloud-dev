from io import BytesIO
from retrying import retry
from sp_api.api import Feeds
from ops.helpers import credentials
from ... import my_logger, SP_EXCEPTIONS, retry_if_error


"""
This function submits the Feed to Amazon.  Basically, we take the submission and post it to Amazon and get the
submission_id that tells us that the feed was successfully submitted to Amazon, returning "FAILED" otherwise.
"""


@retry(
    retry_on_exception=retry_if_error,
    stop_max_attempt_number=5,
    wait_fixed=5000,
)
def submit_feed(feed_body):
    feed_id = "FAILED"

    my_logger.info("Making Submitting Feed to Amazon")
    try:
        feed = BytesIO()
        feed.write(feed_body)
        feed.seek(0)
        result = Feeds(credentials=credentials.sp_credentials()).submit_feed(
            "POST_ORDER_ACKNOWLEDGEMENT_DATA",
            feed,
            'text/xml'
        )
        response_json = {}
        if len(result) > 1:
            response_json = result[1].payload
        my_logger.info(response_json)

        feed_id = response_json.get('feedId', '')
        my_logger.info("feed ID: {}".format(feed_id))

        return feed_id

    except SP_EXCEPTIONS as e:
        my_logger.error(
            f"Exception in while submitting Feed to Amazon | {str(e)}")
        raise e
