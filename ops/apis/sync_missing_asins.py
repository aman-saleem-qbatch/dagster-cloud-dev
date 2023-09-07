import time
from dagster import op
from sqlalchemy.sql import text
from models.amazon_asin_helper import AmazonAsinHelper
from ..apis.helpers.search_catalog_items import search_catalog_items
from ..helpers.db_config import db_conn
from .. import my_logger

conn = db_conn()

def lookup_upc(upc):
    try:
        asin = search_catalog_items(
            marketplace_ids=["ATVPDKIKX0DER"],
            upc=[upc]
        )
        if asin != 'None':
            my_logger.info("UPC: {} = ASIN: {}".format(upc, asin))
            return asin

    except Exception as ex:
        my_logger.error("Exception: {}".format(ex))
    return 'CANTFIND'

@op()
def sync_missing_asins():
    try:
        sql = text('''
            SELECT 
                pm.product_id,
                pm.upc,
                pvm.variant_id,
                aa.asin,
                pvm.stock,
                pvm.sku
            FROM 
                amazon_asinhelper aa
                INNER JOIN product_variant_map pvm ON pvm.sk_product_id=aa.product_id
                INNER JOIN price_master pm on pvm.sk_product_id=pm.product_id
                INNER JOIN variant_detail vd ON vd.variant_id=pvm.variant_id
                LEFT OUTER JOIN amazon_disco_asin ada ON ada.variant_id=pvm.variant_id
                LEFT OUTER JOIN amazon_fba_skus afs ON afs.variant_id=pvm.variant_id
            WHERE
                1=1
                AND COALESCE(aa.asin, 'NEW') IN ('NEW', 'CANTFIND')
                AND LENGTH(pm.upc)>11
                AND NOT (vd.status IN ('Perm Phaseout', 'Clearance') and pvm.stock=0 and pvm.awaiting=0)
                AND ada.asin IS NULL
                AND afs.asin IS NULL
                AND vd.brand_id NOT IN (150, 149)
            ;
        ''')

        rows = conn.execute(sql, {}).all()
        my_logger.info('\n\n', 'missing asins', len(rows))
        i = 0
        added = 0
        for row in rows:
            i += 1

            product_id = int(row[0])
            upc = str(row[1])
            variant_id = int(row[2])
            asin = str(row[3])
            sku = str(row[5])

            my_logger.info("{}. Product_ID: {}, Sku: {}, UPC: {}, ASIN: {}"
                .format(i, product_id, sku, upc, asin)
            )

            ah = conn.query(AmazonAsinHelper).filter_by(product_id=product_id).first()
            if ah is None:
                ah = AmazonAsinHelper(product_id, variant_id, upc)

            try:
                new_asin = lookup_upc(upc)
                ah.asin = new_asin

                conn.merge(ah)
                conn.commit()

                added += 1
                time.sleep(10)
            except Exception as ex:
                my_logger.error("{}. Exception: {}".format(i, ex))

        my_logger.info("{} Rows found, {} added to AsinHelper".format(i, added))

    except Exception as ex:
        my_logger.error("Exception: {}".format(ex))
        raise ex
