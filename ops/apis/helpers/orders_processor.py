import time
from retrying import retry
from sp_api.api import Orders
from ops.helpers import credentials
from datetime import datetime
from ... import my_logger, retry_if_error, SP_EXCEPTIONS
from models.cancel_queue import CancelQueue
from models.last_updated_tracker import LastUpdatedTracker


"""
Hitting Sp Api Orders & Orders Item Api to fetch user's orders information
And Updating the Amazon Orders Cancel Queue Based on order's is_buyer_requested_cancellation status
"""
@retry(
    retry_on_exception=retry_if_error,
    stop_max_attempt_number=5,
    wait_fixed=5000,
)
def process_cancel_orders(posted_after, posted_before):
    try:
        my_logger.info(
            f"posted_after {posted_after} | posted_before {posted_before} | Datetime Now {(datetime.now()).isoformat()}"
        )
        time.sleep(3)
        resp = Orders(credentials=credentials.sp_credentials()).get_orders(
            LastUpdatedAfter=posted_after,
            LastUpdatedBefore=posted_before,
            MarketplaceIds=["ATVPDKIKX0DER"],
            OrderStatuses=["PartiallyShipped", "Unshipped"],
            FulfillmentChannels=["MFN"],
        )
        orders = []
        if resp:
            orders = resp.payload["Orders"] if resp.payload["Orders"] else []
            next_token = (
                resp.payload["NextToken"] if resp.payload.get("NextToken") else None
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
                    temp_orders = resp.payload["Orders"]
                    orders.extend(temp_orders)

            if len(orders) > 0:
                my_logger.info(f"orders length {len(orders)}")             
                for order in orders:                    
                    try:
                        resp = Orders(
                            credentials=credentials.sp_credentials()
                        ).get_order_items(order_id=order.get("AmazonOrderId"))
                    except SP_EXCEPTIONS as e:
                        my_logger.error(f"Exception in the while requesting Order Items : {e}")
                        resp = None
                        raise e
                    if resp:
                        order_items = resp.payload["OrderItems"]
                        my_logger.info(f"order_items {len(order_items)}")                        
                        for order_item in order_items:  
                            is_buyer_requested_cancellation = order_item.get("BuyerRequestedCancel").get("IsBuyerRequestedCancel") if  order_item.get("BuyerRequestedCancel") else ""
                            # Updating the Cancel Queue 
                            if is_buyer_requested_cancellation != "false":                                
                                cqs = CancelQueue.where(
                                    'order_number', order.get('AmazonOrderId')
                                ).where(
                                    'order_item_number', order_item.get("OrderItemId")
                                ).first()
                                if not cqs:
                                    CancelQueue.insert({                          
                                        "cancel_date": datetime.now(),
                                        "desktopshipper_cancel": 0,
                                        "skubana_cancel": 0,
                                        "created_at": datetime.now(),
                                        "updated_at": datetime.now(),
                                    })
                                else:
                                    my_logger.debug(f"Order ID: {order.get('AmazonOrderId')} is already in the queue, skipping.")

                    my_logger.info(f'LastUpdateDate | {order.get("LastUpdateDate")}')
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
        resp = None
        my_logger.error(f"Exception in request_report | {str(e)}")
        raise e
