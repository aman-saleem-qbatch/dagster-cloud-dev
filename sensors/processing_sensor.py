import json
import boto3
import os
import time
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import select, delete
from ops.helpers.db_config import db_conn
from models.reports_processing_consumer import ReportsProcessingConsumer
from dagster import sensor, RunRequest, SkipReason, get_dagster_logger

load_dotenv()

conn = db_conn()
my_logger = get_dagster_logger()


@sensor(job_name="amz_process_done_reports", minimum_interval_seconds=100)
def report_process_sensor():
    try:
        sqs_client = boto3.client(
            "sqs",
            aws_access_key_id=os.getenv("sqs_access_key"),
            aws_secret_access_key=os.getenv("sqs_secret_key"),
            region_name="us-east-1",
        )
        queue_url = os.getenv("sqs_queue_url")

        start_time = time.time()
        seconds = 25
        count = 0
        x = 0
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time > seconds:
                my_logger.info("Finished iterating in: " +
                            str(int(elapsed_time)) + " seconds")
                break
            try:
                resp = sqs_client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=10,
                )
            except Exception as e:
                my_logger.error(e)
                return
            if not resp:
                yield SkipReason("No file ")
                return
            messages = resp.get("Messages")
            if messages:
                delete_entities = []
                for message in messages:
                    count = count + 1
                    report_data = json.loads(message["Body"])
                    processed_report = report_data["payload"]["reportProcessingFinishedNotification"]
                    print(
                        f'\n processed_report["processingStatus"]: {processed_report["processingStatus"]}')
                    stmt = (
                        select(ReportsProcessingConsumer)
                        .where(
                            ReportsProcessingConsumer.report_id == processed_report['reportId'],
                            ReportsProcessingConsumer.report_type == processed_report['reportType']
                        )
                    )
                    report_info = conn.execute(stmt).scalar()
                    if report_info:
                        report = {
                            "report_id": report_info.report_id,
                            "seller_id": report_info.seller_id,
                            "report_type": report_info.report_type,
                            "marketplace_id": report_info.marketplace_id,
                            "created_at": report_info.created_at.isoformat(),
                            "updated_at": report_info.updated_at.isoformat()
                        }
                        if processed_report["processingStatus"] == "CANCELLED" or processed_report["processingStatus"] == "FATAL":
                            stmt = (
                                delete(ReportsProcessingConsumer)
                                .where(ReportsProcessingConsumer.report_id == processed_report['reportId'])
                            )
                            conn.execute(stmt)
                            conn.commit()
                        else:
                            my_logger.info(
                                f'\n processed_report["processingStatus"]: {processed_report["processingStatus"]}')
                            processed_report["message_receipt_handle"] = message["ReceiptHandle"]
                            processed_report['message_id'] = message["MessageId"]
                            resource_dict = {**processed_report, **report}
                            record_id = datetime.now().timestamp()
                            report_run_key = str(record_id) + \
                                "_" + str(report.get("id"))
                            yield RunRequest(
                                run_key=report_run_key,
                                run_config={
                                    "resources": {
                                        "report_details": {
                                            "config": {"id": json.dumps(resource_dict)}
                                        }
                                    },
                                },
                                tags={"job_type": 'amz_process_done_reports' }
                            )
                            x = x+1
                    delete_entities.append(
                        {
                            "Id": message["MessageId"],
                            "ReceiptHandle": message["ReceiptHandle"],
                        }
                    )

                if delete_entities:
                    batch_delete = sqs_client.delete_message_batch(
                        QueueUrl=queue_url, Entries=delete_entities
                    )
                    my_logger.info("batch_delete res: ", batch_delete)

            else:
                my_logger.info("No message in sqs queue")

        my_logger.info(
            f'REQUEST MESSAGES COUNT: {count} and PROCESSED MESSAGES COUNT : {x}')
        
    except Exception as e:
        my_logger.error(e)
        raise e
