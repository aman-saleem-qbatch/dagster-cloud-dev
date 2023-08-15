import os
from orator import DatabaseManager

def db_conn():
    config = {
        'mysql': {
            'driver': 'mysql',
            'host': os.getenv("db_server"),
            'database': os.getenv("db_dbname"),
            'user': os.getenv("db_username"),
            'password': os.getenv("db_password"),
            'port': 3306
        }
    }
    return DatabaseManager(config)
