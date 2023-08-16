import time
from retrying import retry
from sp_api.api import Orders
from ops.helpers import credentials
from ... import my_logger, retry_if_error, SP_EXCEPTIONS


@retry(
    retry_on_exception=retry_if_error,
    stop_max_attempt_number=5,
    wait_fixed=5000,
)
def get_orders(posted_after, posted_before, marketplace_ids, order_statuses, fulfillment_channels):
    try:
        resp = Orders(credentials=credentials.sp_credentials()).get_orders(
            LastUpdatedAfter=posted_after,
            LastUpdatedBefore=posted_before,
            MarketplaceIds=marketplace_ids,
            OrderStatuses=order_statuses,
            FulfillmentChannels=fulfillment_channels,
        )

        orders = []
        if resp:
            orders = resp.payload["Orders"] if resp.payload["Orders"] else []
            next_token = (
                resp.payload["NextToken"]
                if resp.payload.get("NextToken")
                else None
            )
            while next_token:
                time.sleep(3)
                resp = Orders(credentials=credentials.sp_credentials()).get_orders(
                    NextToken=next_token
                )
                if resp:
                    next_token = (
                        resp.payload["NextToken"]
                        if resp.payload.get("NextToken")
                        else None
                    )
                    temp_orders = resp.payload["Orders"] if resp.payload["Orders"] else []
                    orders.extend(temp_orders)

        return orders
    except SP_EXCEPTIONS as e:
        my_logger.error(str(e))
        resp = None
        my_logger.error(f"Exception in the while requesting Order | {str(e)}")
        raise e
