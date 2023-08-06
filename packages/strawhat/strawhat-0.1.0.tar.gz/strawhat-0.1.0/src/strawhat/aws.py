import json
from functools import wraps
from decimal import Decimal

from boto3 import resource, client
from boto3.dynamodb.conditions import Key, Attr

# ------------------- Decorator -------------------


def dynamodb_response_handler(query_function):
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError

    @wraps(query_function)
    def wrapper_fuction(*args, **kwargs):
        response = query_function(*args, **kwargs)
        if "Items" in response and response["Items"] != []:
            data = response["Items"]
            while "LastEvaluatedKey" in response:
                response = query_function(
                    *args, **kwargs, lek=response["LastEvaluatedKey"]
                )
                if "Items" in response and response["Items"] == []:
                    break
                data.extend(response["Items"])
            return json.loads(json.dumps(data, default=decimal_default))

    return wrapper_fuction


def dynamodb_single_response_handler(query_function):
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError

    @wraps(query_function)
    def wrapper_fuction(*args, **kwargs):
        response = query_function(*args, **kwargs)
        if "Item" in response and response["Item"] != []:
            data = response["Item"]
            return json.loads(json.dumps(data, default=decimal_default))

    return wrapper_fuction


# ------------------- Serivce Class -------------------


class AWS:
    def __init__(
        self, access_key, secret_access_key, region="ap-south-1", local=False
    ):
        self.local = local
        if not self.local:
            self.access_key = access_key
            self.secret_access_key = secret_access_key
            self.region = region

    def resource(self, service):
        if self.local:
            return resource(service, endpoint_url="http://localhost:8000")
        else:
            return resource(
                service,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region,
            )

    def client(self, service):
        if self.local:
            return client(service, endpoint_url="http://localhost:8000")
        else:
            return client(
                service,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region,
            )


# ------------------- Dynamodb Class -------------------


class Dynamodb:
    def __init__(self, dynamodb_resource):
        self.resource = dynamodb_resource
        self.table = dict()

    def connect2table(self, table_name):
        self.table[table_name] = self.resource.Table(table_name)

    def __float_to_decimal(self, data):
        return json.loads(json.dumps(data), parse_float=Decimal)

    @dynamodb_response_handler
    def scan_table(self, table_name, conditions, lek=None):
        if lek:
            conditions["ExclusiveStartKey"] = lek
        return self.table[table_name].scan(**conditions)

    @dynamodb_response_handler
    def query_table(self, table_name, conditions, lek=None):
        if lek:
            conditions["ExclusiveStartKey"] = lek
        return self.table[table_name].query(**conditions)

    def put_data(self, table_name, data):
        data = self.__float_to_decimal(data)
        self.table[table_name].put_item(Item=data)

    @dynamodb_single_response_handler
    def get_data(self, table_name, conditions):
        return self.table[table_name].get_item(**conditions)

    def update_row(self, table_name, conditions):
        self.table[table_name].update_item(**conditions)

    def delete_row(self, table_name, conditions):
        self.table[table_name].delete_item(**conditions)

    def batch_write(self, table_name, data_list):
        with self.table[table_name].batch_writer() as batch:
            for data in data_list:
                data = self.__float_to_decimal(data)
                batch.put_item(Item=data)


# ------------------- S3 Class -------------------


class S3:
    def __init__(self, s3_resource):
        self.resource = s3_resource

    def read_object(self, bucket_name, bucket_object):
        obj = self.resource.Object(bucket_name, bucket_object)
        return obj.get()["Body"].read()

    def put_object(self, bucket_name, bucket_object, content):
        return s3.Object(bucket_name, bucket_object).put(Body=content)
