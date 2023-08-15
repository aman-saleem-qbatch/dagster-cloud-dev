import os
from dotenv import load_dotenv

load_dotenv()

def sp_credentials():
    return dict(
        refresh_token=os.getenv("refresh_token"),
        lwa_app_id=os.getenv("lwa_app_id"),
        lwa_client_secret=os.getenv("lwa_client_secret"),
        aws_secret_key=os.getenv("aws_secret_key"),
        aws_access_key=os.getenv("aws_access_key"),
        role_arn=os.getenv("role_arn"),
    )
