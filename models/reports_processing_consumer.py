from orator import Model
from ops.helpers.db_config import db_conn

Model.set_connection_resolver(db_conn())

class ReportsProcessingConsumer(Model):
    __table__ = "reports_processing_consumer"
    __fillable__ = [
        "report_id",
        "seller_id",
        "report_type",
        "marketplace_id",
        "created_at",
        "updated_at",
    ]