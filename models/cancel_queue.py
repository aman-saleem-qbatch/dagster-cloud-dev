from orator import Model
from ops.helpers.db_config import db_conn

Model.set_connection_resolver(db_conn())


class CancelQueue(Model):
    __table__ = "cancel_queue"
    __fillable__ = [
        "cancel_id",
        "order_number",
        "order_item_number",
        "sku",
        "skubana_cancel",
        "desktopshipper_cancel",
        "amazon_cancel",
        "cancel_date",
        "created_at",
        "updated_at",
    ]
