import json
import csv
import os
import pandas as pd
from dagster import op
from sqlalchemy import delete
from ..helpers.db_config import db_conn
from models.reports_processing_consumer import ReportsProcessingConsumer
from ops.helpers.save_reports_data import (
    listing_report_data,
)
from .. import my_logger

conn = db_conn()


def delete_record(file_name, data):
    if os.path.exists(file_name):
        my_logger.info("Deleting the Processed File...")
        os.remove(file_name)
    stmt = delete(ReportsProcessingConsumer).where(
        ReportsProcessingConsumer.report_id == data["reportId"]
    )
    conn.execute(stmt)
    conn.commit()


@op(required_resource_keys={"report_details"})
def save_report(context, file_name):
    try:
        if file_name:
            result = context.resources.report_details
            data = json.loads(result["data"])
            tsv_file = open(file_name, encoding="windows-1252")
            with open(file_name, "r", encoding="latin1") as f:
                reader = csv.reader(f)
                header = next(reader)
                print("header", header)
                header = header[0].split("\t")
                if "seller-sku" in header:
                    dtype = {"seller-sku": str}
                else:
                    dtype = None

            report_df = pd.read_csv(tsv_file, sep="\t", dtype=dtype)
            resp = listing_report_data.save_listing_report(report_df, data)
            if resp:
                delete_record(file_name, data)
            return True
    except Exception as e:
        delete_record(file_name, data)
        my_logger.error(f"Error in Saving Report {e}")
        raise e
