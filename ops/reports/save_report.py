import json
import csv
import os
import pandas as pd
from dagster import op
from models.reports_processing_consumer import ReportsProcessingConsumer
from ops.helpers.save_reports_data import (
    listing_report_data,
)
from .. import my_logger



@op(required_resource_keys={"report_details"})
def save_report(context, file_name):
    if file_name:
        result = context.resources.report_details
        data = json.loads(result["data"])
        tsv_file = open(file_name, encoding="windows-1252")
        my_logger.info(f"TSV FILE:  {tsv_file} ")
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

        if data["report_type"] == "GET_MERCHANT_LISTINGS_ALL_DATA":
            my_logger.info("Report_type:   GET_MERCHANT_LISTINGS_ALL_DATA")
            resp = listing_report_data.save_listing_report(report_df, data)
            if resp:
                if os.path.exists(file_name):
                    print('Deleting the Processed File...')
                    os.remove(file_name)
                ReportsProcessingConsumer.where_raw(
                    f""" report_id = "{data['reportId']}" """).delete()
        else:
            my_logger.info("No report matched")
            return True
