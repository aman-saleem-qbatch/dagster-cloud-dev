from dagster import op, job


@op()
def testOp(context):
    context.log.info(f"No. of days: {1}")


@job
def amz_test_job():
    testOp()
