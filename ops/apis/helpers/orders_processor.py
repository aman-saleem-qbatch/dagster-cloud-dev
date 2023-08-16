import time
from datetime import datetime
from ... import my_logger, SP_EXCEPTIONS
from models.cancel_queue import CancelQueue
from models.last_updated_tracker import LastUpdatedTracker
from .get_orders import get_orders
from .get_orders_items import get_orders_items

"""
Hitting Sp Api Orders & Orders Item Api to fetch user's orders information
And Updating the Amazon Orders Cancel Queue Based on order's is_buyer_requested_cancellation status
"""


def process_cancel_orders(posted_after, posted_before):
    try:
        my_logger.info(
            f"posted_after {posted_after} | posted_before {posted_before} | Datetime Now {(datetime.now()).isoformat()}"
        )
        time.sleep(3)
        orders = get_orders(
            posted_after,
            posted_before,
            marketplace_ids=["ATVPDKIKX0DER"],
            order_statuses=["PartiallyShipped", "Unshipped"],
            fulfillment_channels=["MFN"]
        )
        if len(orders) > 0:
            my_logger.info(f"orders length {len(orders)}")
            for order in orders:
                time.sleep(3)
                order_items = get_orders_items(
                    order_id=order.get("AmazonOrderId"))
                if order_items:
                    my_logger.info(f"order_items {len(order_items)}")
                    for order_item in order_items:
                        is_buyer_requested_cancellation = order_item.get("BuyerRequestedCancel").get(
                            "IsBuyerRequestedCancel") if order_item.get("BuyerRequestedCancel") else "false"
                        # Updating the Cancel Queue
                        if is_buyer_requested_cancellation != "false":
                            cqs = CancelQueue.where(
                                'order_number', order.get('AmazonOrderId')
                            ).where(
                                'order_item_number', order_item.get(
                                    "OrderItemId")
                            ).where(
                                'sku', order_item.get("SellerSKU")
                            ).first()
                            if not cqs:
                                CancelQueue.insert({
                                    "order_number": order.get('AmazonOrderId'),
                                    "order_item_number": order_item.get("OrderItemId"),
                                    "sku": order_item.get("SellerSKU"),
                                    "cancel_date": datetime.now(),
                                    "desktopshipper_cancel": 0,
                                    "skubana_cancel": 0,
                                    "created_at": datetime.now(),
                                    "updated_at": datetime.now(),
                                })
                            else:
                                my_logger.debug(
                                    f"Order ID: {order.get('AmazonOrderId')} is already in the queue, skipping.")

                my_logger.info(
                    f'LastUpdateDate | {order.get("LastUpdateDate")}')
                # Updating Order Tracker
                last_tracker = LastUpdatedTracker.where(
                    "tracker_type", "orders"
                ).first()
                if not last_tracker:
                    LastUpdatedTracker.insert({
                        "tracker_type": "orders",
                        "last_updated_at": datetime.strptime(order.get("LastUpdateDate"), "%Y-%m-%dT%H:%M:%SZ"),
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                    })
                else:
                    last_tracker.update({
                        "last_updated_at": datetime.strptime(order.get("LastUpdateDate"), "%Y-%m-%dT%H:%M:%SZ")
                    })
            return True
        else:
            my_logger.error(f"No Orders")
            return False
    except SP_EXCEPTIONS as e:
        my_logger.error(str(e))
        orders = None
        my_logger.error(f"Exception in request_report | {str(e)}")
        raise e
