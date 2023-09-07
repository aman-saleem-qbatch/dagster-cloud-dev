import os
import json
from dagster import op
from datetime import datetime, timedelta
from sqlalchemy import update
from models.cancel_queue import CancelQueue
from ops.apis.helpers import submit_order_feed, check_feed_status
from ..helpers.db_config import db_conn
from .. import my_logger

conn = db_conn()


"""
Create the Amazon Cancel Order Acknowledgement XML Request for each ready order in the queue and 
then submit to Amazon to cancel the order.
"""


@op(required_resource_keys={"report_details"})
def process_cancels(context):
    result = context.resources.report_details
    data = json.loads(result["data"])
    if data:
        cancels = 0
        cancel_ids = []
        for cq in data.get('cqs', []):
            cancels += 1
            order_number = list(cq.keys())[0]
            my_logger.info("Cancel {}:  CQ: {}".format(cancels, order_number))

            feed_body = f"""
            <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
            <Header>
                    <DocumentVersion>1.01</DocumentVersion>
                    <MerchantIdentifier>{os.getenv("seller_id")}</MerchantIdentifier>
            </Header>
            <MessageType>OrderAcknowledgement</MessageType>
            <Message>
                    <MessageID>1</MessageID>
                    <OrderAcknowledgement>
                    <AmazonOrderID>{order_number}</AmazonOrderID>
                    <StatusCode>Failure</StatusCode>"""
            for item in cq[order_number]:
                cancel_ids.append(item.get('cancel_id'))
                feed_body += f"""
                    <Item>
                        <AmazonOrderItemCode>{item.get('order_item_number')}</AmazonOrderItemCode>
                        <CancelReason>{item.get('buyer_cancellation_reason')}</CancelReason>
                    </Item>"""
            feed_body += f"""
                    </OrderAcknowledgement>
            </Message>
            </AmazonEnvelope>
            """
            feed_body = feed_body.encode('utf-8')

            submission_id = submit_order_feed.submit_feed(feed_body)
            if submission_id:
                stmt = (
                    update(CancelQueue)
                    .where(CancelQueue.order_number == order_number)
                    .values(
                        processing_status='IN PROGRESS',
                        amazon_cancel_date = datetime.now(),
                        updated_at=datetime.now()
                    )
                )
                conn.execute(stmt)
                conn.commit()

                resp = check_feed_status.request_feed_status(submission_id)
                if resp.get('status') != "FAILED":
                    my_logger.info(f'status {resp.get("status")}')
                    # Updating CancelQueue Status
                    update_stmt = (
                        update(CancelQueue)
                        .where(CancelQueue.cancel_id.in_(tuple(cancel_ids)))
                        .values(
                            amazon_cancel=1,
                            last_processed_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                    )
                    conn.execute(update_stmt)
                    conn.commit()
                else:
                    update_stmt = (
                        update(CancelQueue)
                        .where(CancelQueue.cancel_id.in_(tuple(cancel_ids)))
                        .values(
                            last_processed_at=datetime.now() + timedelta(hours=2),
                            processing_status=resp.get('status'),
                            error_message=resp.get('error_message'),
                            updated_at=datetime.now()
                        )
                    )
                    conn.execute(update_stmt)
                    conn.commit()
                    my_logger.info(
                        "Did not update database for cq.cancel_id: {} Order ID: {}, because... Status=={}"
                        .format(cq.get('cancel_id'), cq.get('order_number'), resp.get('status'))
                    )
            else:
                my_logger.info('No submission_feed_id ...')

        if cancels == 0:
            my_logger.info("No Amazon Orders to Cancel this time...")
        else:
            my_logger.info("Cancelled total of {} Orders".format(cancels))
