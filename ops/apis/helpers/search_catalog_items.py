from retrying import retry
from sp_api.api import CatalogItems
from ops.helpers import credentials
from ... import my_logger, retry_if_error, SP_EXCEPTIONS


@retry(
    retry_on_exception=retry_if_error,
    stop_max_attempt_number=5,
    wait_fixed=5000,
)
def search_catalog_items(marketplace_ids, upc):
    try:
        resp = CatalogItems(credentials=credentials.sp_credentials()).search_catalog_items(
            marketplaceIds=marketplace_ids,
            keywords=upc,
            includedData=['summaries']
        )
        asin = ''
        if resp:
            asin = resp.payload.get('items')[0].get('asin') if len(resp.payload.get('items')) > 0 else None
        return asin

    except SP_EXCEPTIONS as e:
        resp = None
        my_logger.error(f"Exception in the while requesting Search Catalog Item | {str(e)}")
        raise e
