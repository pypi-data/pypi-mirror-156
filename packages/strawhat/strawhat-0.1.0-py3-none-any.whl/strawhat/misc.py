import time
import base64
from functools import wraps

# ------------------- Decorators -------------------


def time_it(input_function):
    "print execution time of a function"

    @wraps(input_function)
    def wrapper_function(*args, **kwargs):
        start_time = time.time()
        response = input_function(*args, **kwargs)
        end_time = time.time()
        print(
            'Function "%s" executed in: %.3f seconds'
            % (input_function.__name__, (end_time - start_time))
        )
        return response

    return wrapper_function


def base64encode_UTFdecode(input_function):
    "string -> bas64encode -> UTFdecode"

    @wraps(input_function)
    def wrapper_function(*args, **kwargs):
        response = input_function(*args, **kwargs)
        return base64.b64encode(response).decode("UTF-8")

    return wrapper_function
