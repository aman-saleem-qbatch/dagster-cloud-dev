from dagster import job
from ops.apis.helpers.insert_new_additions_into_asinhelper import insert_new_additions_into_asinhelper
from ops.apis.helpers.update_asinhelper_from_inventory_report import update_asinhelper_from_air_report
from ops.apis.sync_missing_asins import sync_missing_asins

@job(tags={"job_type": 'amz_sync_missing_asins' })
def amz_sync_missing_asins():
    result = insert_new_additions_into_asinhelper()
    respone = update_asinhelper_from_air_report(result)
    sync_missing_asins(respone)
