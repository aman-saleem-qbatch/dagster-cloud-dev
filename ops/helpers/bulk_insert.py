import pymysql
from retrying import retry
from .database import db_client
from .. import my_logger


def retry_if_pymysql_error(exception):
    """Return True if we should retry (in this case when it's an IOError), False otherwise"""
    return isinstance(exception, pymysql.OperationalError)


@retry(
    retry_on_exception=retry_if_pymysql_error,
    stop_max_attempt_number=5,
    wait_fixed=2000,
)
def bulk_insert(table, columns, values):
    try:
        conn = db_client()
        cursor = conn.cursor()
        chunk_size = 500
        my_logger.info(f'TOTAL values: {len(values)}')
        for i in range(0, len(values), chunk_size):
            value = values[i: i + chunk_size]
            my_logger.info(f"CHUNK SIZE {len(value)}")
            value_placeholder = list(
                map(lambda s: "NULLIF(CAST(%s AS CHAR), '')", columns))
            sql = f"INSERT INTO {table}(" + ",".join(columns) + ") VALUES (" + ",".join(
                value_placeholder) + ");"
            try:
                cursor.executemany(sql, value)
                my_logger.info(
                    f"SAVE REPORT in TABLE {table} :   {cursor.rowcount}")
                conn.commit()
            except (pymysql.OperationalError, pymysql.Error) as e:
                my_logger.error(e)
                raise e
    finally:
        cursor.close()
