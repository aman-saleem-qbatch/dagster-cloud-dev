import numpy as np
from datetime import datetime
from sqlalchemy import select, delete
from ...helpers.db_config import db_conn
from models.amazon_inventory_report import AmazonInventoryReport
from ops.helpers.bulk_insert import bulk_insert

conn = db_conn()


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
    stmt = (
        select(AmazonInventoryReport.sku)
        .limit(500)
    )
    res = conn.execute(stmt).fetchall()
    while (len(res) > 0):
        skus_list = []
        for skus in res:
            skus_list.append(skus.sku)
        conn.execute(
            delete(AmazonInventoryReport)
            .where(AmazonInventoryReport.sku.in_(tuple(skus_list)))
        )
        conn.commit()
        res = conn.execute(stmt).fetchall()

    conn.close()

    bulk_insert(
        "amazon_inventory_report", inventory_list_keys, inventory_list)
    return True
