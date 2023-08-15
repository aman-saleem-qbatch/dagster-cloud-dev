from orator import Model
from ops.helpers.db_config import db_conn

Model.set_connection_resolver(db_conn())


class AmazonAsinHelper(Model):
    __table__ = "amazon_asinhelper"
    __fillable__ = [
        "id",
        "product_id",
        "variant_id",
        "asin",
        "upc",
        "created_at",
        "updated_at",
    ]
