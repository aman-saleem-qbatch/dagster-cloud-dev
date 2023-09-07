import time
from retrying import retry
from sp_api.api import Feeds
import xml.etree.ElementTree as ET
from ops.helpers import credentials
from ... import my_logger, retry_if_error, SP_EXCEPTIONS


"""
Once the feed is submitted to Amazon, we check to see if we get the feed results, and if the feed submission was
successful, we mark it completed in the database.
"""


@retry(
    retry_on_exception=retry_if_error,
    stop_max_attempt_number=5,
    wait_fixed=5000,
)
def request_feed_status(feed_request_id=None):
    try:
        my_logger.info(
            "Request_Reports(report_request_id={}): ".format(feed_request_id))
        my_logger.info("Waiting 30 Seconds for Feed to Process or whatever")
        time.sleep(30)
        feed_id = "FAILED"
        success_count = 0
        error_count = 0
        resultFeedDocumentId = ''
        processing_status = ''
        result = Feeds(credentials=credentials.sp_credentials()).get_feed(
            feedId=feed_request_id
        )
        if result and result.payload:
            my_logger.info(f'result {result}')
            response_json = result.payload
            processing_status = response_json.get('processingStatus')
            feed_id = response_json.get('feedId')
            resultFeedDocumentId = response_json.get(
                'resultFeedDocumentId')
            while processing_status != 'DONE':
                time.sleep(30)
                result = Feeds(credentials=credentials.sp_credentials()).get_feed(
                    feedId=feed_request_id
                )
                if result and result.payload:
                    my_logger.info(f'result {result}')
                    response_json = result.payload  # Update the response_json with the new JSON
                    processing_status = response_json.get(
                        'processingStatus'
                    )
                    feed_id = response_json.get('feedId')
                    resultFeedDocumentId = response_json.get(
                        'resultFeedDocumentId'
                    )
                    if processing_status == 'DONE':
                        my_logger.info(
                            f'processing_status {processing_status}'
                        )
                        break

        if feed_id != "FAILED":
            my_logger.info("Successfully located Transaction ID: {} & resultFeedDocumentId {}".format(
                    feed_id, resultFeedDocumentId
                )
            )
        resp = Feeds(credentials=credentials.sp_credentials()).get_feed_document(
            feedDocumentId=resultFeedDocumentId
        )
        root = ''
        if resp:
            # Extracting Data from the XML response
            root = ET.fromstring(resp)
            success_count = root.find(
                ".//ProcessingSummary/MessagesSuccessful").text
            error_count = root.find(
                ".//ProcessingSummary/MessagesWithError").text
            my_logger.info(
                "Feed Transaction {} & FeedDocumentId {}: Successes: {}  Errors: {}".format(
                    feed_id, resultFeedDocumentId, success_count, error_count
                )
            )
        error_message = ''
        if int(error_count) > 0:
            # When an Amazon order is already cancelled, it has the message below with the order number...
            # so we'll parse for that message and if we find it, we'll zero the error and assume it is good
            # to mark as cancelled in the database!
            error_message = root.find(
                ".//ResultDescription").text if root else ''
            my_logger.debug(f"ResultDescription {error_message}")
            if (error_message[:55] == "The items in your order cannot be found using order ID "):
                my_logger.info(
                    "See ResultDescription in response above.  Assuming Order is Already Cancelled.  Marking Error=0/Success=1"
                )
                error_count = "0"
                success_count = "1"

        if int(success_count) == 1 and int(error_count) == 0:
            return {
                'status': processing_status
            }
        else:
            return {
                'status': "FAILED",
                'error_message': error_message
            }

    except SP_EXCEPTIONS as e:
        my_logger.info("Exception: {}".format(str(e)))
        raise e
