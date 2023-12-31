import json, pytz
from dotenv import load_dotenv
from datetime import datetime
from dagster import sensor, RunRequest, SkipReason, get_dagster_logger
from models.cancel_queue import CancelQueue
from ops.helpers.db_config import db_conn

conn = db_conn()
load_dotenv()

my_logger = get_dagster_logger()


@sensor(job_name="amz_submit_cancel_orders", minimum_interval_seconds=60)
def process_submit_cancel_orders():
    pacific_zone = pytz.timezone('US/Pacific')
    orders_list = (
        conn.query(CancelQueue.order_number)
        .where(
            CancelQueue.desktopshipper_cancel == 1,
            CancelQueue.skubana_cancel == 1,
            CancelQueue.amazon_cancel == 0,
            CancelQueue.last_processed_at <= datetime.now(pacific_zone),
            CancelQueue.processing_status.in_(tuple(['PENDING', 'FAILED']))
        )
        .distinct()
        .all()
    )

    if len(orders_list) < 1:
        yield SkipReason("No New Order ")
        return
    result = []
    for order in orders_list:
        print('\n\n', 'order.order_number', order.order_number)
        item_list = (
            conn.query(
                CancelQueue.cancel_id,
                CancelQueue.order_item_id,
                CancelQueue.buyer_cancellation_reason
            )
            .where(
                CancelQueue.order_number == order.order_number)
            .all()
        )
        order_items = []
        for item in item_list:
            order_items.append({
                "cancel_id": item.cancel_id,
                "order_item_id": item.order_item_id,
                "buyer_cancellation_reason": item.buyer_cancellation_reason
            })
        result.append({
            order.order_number: order_items
        })
    record_timestamp = datetime.now().timestamp()
    run_key = str(record_timestamp) + "_orders_" + str(len(orders_list))
    yield RunRequest(
        run_key,
        run_config={
            "resources": {
                "report_details": {"config": {"id": json.dumps({"cqs": result})}}
            },
        },
        tags={"job_type": 'amz_submit_cancel_orders'},
    )
