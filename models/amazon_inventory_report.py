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
        "created_at",
        "updated_at",
    ]