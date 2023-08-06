import json
import requests

from functools import wraps

# ------------------- Decorator Function -------------------


def process_response(input_function):
    "converts api response to python dict"

    @wraps(input_function)
    def wrapper_function(*args, **kwargs):
        response = input_function(*args, **kwargs)
        return json.loads(response.text)

    return wrapper_function


# ------------------- API Class -------------------


class API:
    def __init__(self, base_url, headers, timeout=10):
        self.timeout = timeout
        self.base_url = base_url
        self.headers = headers

    def __str__(self):
        return self.base_url

    @process_response
    def post(self, data, end_point_url=""):
        return requests.post(
            url=self.base_url + end_point_url,
            headers=self.headers,
            data=json.dumps(data),
            timeout=self.timeout,
        )

    @process_response
    def put(self, data, end_point_url=""):
        return requests.put(
            url=self.base_url + end_point_url,
            headers=self.headers,
            data=json.dumps(data),
            timeout=self.timeout,
        )

    @process_response
    def get(self, end_point_url=""):
        return requests.get(
            url=self.base_url + end_point_url,
            headers=self.headers,
            timeout=self.timeout,
        )

    @process_response
    def delete(self, end_point_url=""):
        return requests.delete(
            url=self.base_url + end_point_url,
            headers=self.headers,
            timeout=self.timeout,
        )
