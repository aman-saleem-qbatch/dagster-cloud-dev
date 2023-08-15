from datetime import datetime
import numpy as np
from models.amazon_inventory_report import AmazonInventoryReport
from ops.helpers.bulk_insert import bulk_insert


def save_listing_report(report_df, data):
    report_data = report_df.filter(
        [
            "seller-sku",
            "price",
            "quantity",
            "asin1"
        ]
    )
    report_data.columns = [
        "sku",
        "price",
        "quantity",
        "asin"
    ]
    report_data.replace({np.nan: "!"}, inplace=True)
    report_data.replace({"!": ""}, inplace=True)
    report_dict = report_data.to_dict("records")
    inventory_list = []
    for report in report_dict:
        s_sku = list(report.values())
        s_sku.append(datetime.now())
        s_sku.append(datetime.now())
        s_sku.append(data['marketplace_id'])
        inventory_list.append(tuple(s_sku))
    inventory_list_keys = list(report_dict[0].keys())
    inventory_list_keys.append("created_at")
    inventory_list_keys.append("updated_at")
    inventory_list_keys.append("marketplace_id")

    # Truncating & Inserting Data
    for inventories in AmazonInventoryReport.chunk(500):
        skus_list = []
        for inventory in inventories:
            skus_list.append(inventory.sku)
        AmazonInventoryReport.where_raw(f"sku IN {tuple(skus_list)}").delete()

    bulk_insert(
        "amazon_inventory_report", inventory_list_keys, inventory_list)
    return True
