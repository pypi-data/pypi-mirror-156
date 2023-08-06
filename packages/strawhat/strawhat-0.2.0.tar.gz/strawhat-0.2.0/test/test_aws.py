#!/usr/bin/env python3
from strawhat.aws import AWS, Dynamodb

# ------------------- Init -------------------

# init aws resource
aws = AWS(None, None, None, True)
ddb_resource = aws.resource("dynamodb")

# init dynamodb
ddb = Dynamodb(ddb_resource)
TEST_TABLE = "my_table"
ddb.connect2table(TEST_TABLE)

# ------------------- Test Cases -------------------


def test_offline_aws_connect():
    assert aws.__dict__ == {"local": True}


def test_ddb_scan_data():
    response = ddb.scan_table(TEST_TABLE, {})
    assert response == [{"id": "hello"}]
