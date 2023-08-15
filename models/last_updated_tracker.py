from orator import Model
from ops.helpers.db_config import db_conn

Model.set_connection_resolver(db_conn())


class LastUpdatedTracker(Model):
    __table__ = "last_updated_tracker"
    __fillable__ = [
        "id",
        "tracker_type",
        "last_updated_at",
        "created_at",
        "updated_at",
    ]
