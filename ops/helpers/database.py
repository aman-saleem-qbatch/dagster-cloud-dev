import os
import pymysql.cursors


def db_client():
    return pymysql.connect(
        host=os.getenv("db_server"),
        user=os.getenv("db_username"),
        password=os.getenv("db_password"),
        database=os.getenv("db_dbname"),
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
    )
