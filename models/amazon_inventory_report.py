from orator import Model
from ops.helpers.db_config import db_conn

Model.set_connection_resolver(db_conn())


class AmazonInventoryReport(Model):
    __table__ = "amazon_inventory_report"
    __fillable__ = [
        "sku",
        "asin",
        "price",
        "quantity",
        "marketplace_id",
        "Business Price",
        "Quantity Price Type",
        "Quantity Lower Bound 1",
        "Quantity Price 1",
        "Quantity Lower Bound 2",
        "Quantity Price 2",
        "Quantity Lower Bound 3",
        "Quantity Price 3",
        "Quantity Lower Bound 4",
        "Quantity Price 4",
        "Quantity Lower Bound 5",
        "Quantity Price 5",
        "created_at",
        "updated_at",
    ]
