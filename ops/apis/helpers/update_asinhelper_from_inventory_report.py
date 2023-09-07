from sqlalchemy.sql import text
from dagster import op
from ...helpers.db_config import db_conn
from ... import my_logger

conn = db_conn()

@op
def update_asinhelper_from_air_report():
    try:
        sql = text('''
			UPDATE
				amazon_asinhelper aa
				INNER JOIN (
					SELECT
						iair.sku,
						iair.asin,
						iaa.product_id
					FROM
						price_master ipm
						INNER JOIN amazon_inventory_report iair ON iair.sku=ipm.sku
						LEFT OUTER JOIN amazon_asinhelper iaa ON ipm.product_id=iaa.product_id
					WHERE
						iaa.asin='CANTFIND'
				) d ON d.product_id=aa.product_id
			SET
				aa.asin=d.asin
			WHERE
				aa.asin='CANTFIND'
				AND d.asin != aa.asin
			;
		''')
        update = conn.execute(sql, {})
        my_logger.info("Updated Existing Entries into Amazon_AsinHelper Table: {} Rows"
			.format(update.rowcount)
		)

    except Exception as e:
        my_logger.error(f"Exception in while Updated Existing Entries into Amazon_AsinHelper Table  | {str(e)}")
        raise e
