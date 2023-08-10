from dagster import repository

# from sensors import (
   
# )
# from schedulers import (
    
# )
from jobs import (
    amz_test_job
)


@repository
def ss_jobs_repo():
    return [
        # Jobs
       amz_test_job.amz_test_job
        # Schedulars
       
        # Sensors
        
    ]
