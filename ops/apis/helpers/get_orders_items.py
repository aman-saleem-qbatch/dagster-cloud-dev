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
def get_orders_items(order_id):
    try:
        resp = Orders(
            credentials=credentials.sp_credentials()
        ).get_order_items(order_id=order_id)

        order_items = []
        if resp:
            order_items = resp.payload["OrderItems"] if resp.payload["OrderItems"] else []
            next_token = (
                resp.payload["NextToken"]
                if resp.payload.get("NextToken")
                else None
            )
            while next_token:
                time.sleep(3)
                resp = Orders(credentials=credentials.sp_credentials()).get_order_items(
                    NextToken=next_token
                )
                if resp:
                    next_token = (
                        resp.payload["NextToken"]
                        if resp.payload.get("NextToken")
                        else None
                    )
                    temp_orders_items = resp.payload["OrderItems"] if resp.payload["OrderItems"] else []
                    order_items.extend(temp_orders_items)

        return order_items
    except SP_EXCEPTIONS as e:
        my_logger.error(
            f"Exception in the while requesting Order Items : {e}")
        resp = None
        raise e
