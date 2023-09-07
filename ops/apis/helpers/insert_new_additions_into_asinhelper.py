from dagster import op
from sqlalchemy.sql import text
from ...helpers.db_config import db_conn
from models.amazon_asin_helper import AmazonAsinHelper
from ... import my_logger

conn = db_conn()

@op()
def insert_new_additions_into_asinhelper():
    try:
        sql = text('''
			SELECT
				pm.product_id,
				pvm.variant_id,
				pm.upc,
				air.asin
			FROM
				price_master pm
				INNER JOIN product_variant_map pvm ON pvm.sk_product_id=pm.product_id
				LEFT OUTER JOIN amazon_inventory_report air ON air.sku=pm.sku
				LEFT OUTER JOIN amazon_asinhelper aa ON aa.product_id=pm.product_id
			WHERE
				aa.product_id IS NULL
				AND LENGTH(pm.upc)>11
				;
		''')
        missing_products = conn.execute(sql, {}).all()
        my_logger.info('\n\n missing products', len(missing_products))
        
        result = []
        for product in missing_products:
            product_id = product[0]
            variant_id = product[1]
            upc = product[2]
            asin = product[3]
            result.append(AmazonAsinHelper(product_id, variant_id, upc, asin))
        conn.add_all(result)
        conn.commit()
        my_logger.info("Inserted New Entries into Amazon_AsinHelper Table: {} Rows"
			.format(len(result))
		)

    except Exception as e:
        my_logger.error(f"Exception in while Inserted New Entries into Amazon_AsinHelper Table  | {str(e)}")
        raise e
