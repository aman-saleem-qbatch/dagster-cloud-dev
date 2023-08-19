import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def db_conn():
    engine = create_engine('{}://{}:{}@{}/{}'.format(
        "mysql+pymysql",
        os.getenv("db_username"),
        os.getenv("db_password"),
        os.getenv("db_server"),
        os.getenv("db_dbname")
    ), echo=False)

    Session = sessionmaker(bind=engine)

    return Session()
