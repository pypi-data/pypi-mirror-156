from airflow_commons.internal.salesforce.constants import (
    ASYNC_PATH,
    DATA_EXTENSION_KEY_PATH,
    ASYNC_JOB_RESULT_PATH,
)


def get_headers(access_token: str):
    """
    Builds a request header with given token.
    :param access_token: Active access token
    :return:
    """
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }


def get_async_operation_url(base_url: str, key: str):
    """
    Builds an async operation url
    :param base_url:
    :param key:
    :return:
    """
    return base_url + ASYNC_PATH + DATA_EXTENSION_KEY_PATH.format(key=key)


def get_async_operation_result_url(base_url: str, request_id: str):
    """
    Builds an async operation result url
    :param base_url:
    :param request_id:
    :return:
    """
    return base_url + ASYNC_PATH + ASYNC_JOB_RESULT_PATH.format(request_id=request_id)
