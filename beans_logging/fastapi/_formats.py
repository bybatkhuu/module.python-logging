# -*- coding: utf-8 -*-


def http_file_format(record: dict) -> str:
    """Http access log file format.

    Args:
        record (dict): Log record as dictionary.

    Returns:
        str: Format for http access log record.
    """

    _MSG_FORMAT = '{client_host} {request_id} {user_id} [{datetime}] "{method} {url_path} HTTP/{http_version}" {status_code} {content_length} "{h_referer}" "{h_user_agent}" {response_time}'

    if "http_info" not in record["extra"]:
        return ""

    if "http_message" not in record:
        _http_info = record["extra"]["http_info"]
        if "datetime" not in _http_info:
            _http_info["datetime"] = record["time"].isoformat()
            record["extra"]["http_info"] = _http_info

        _msg_format = _MSG_FORMAT
        if "http_file_msg_format" in record["extra"]:
            _msg_format = record["extra"]["http_file_msg_format"]

        _msg = _msg_format.format(**_http_info)
        record["http_message"] = _msg

    return "{http_message}\n"


def http_file_json_format(record: dict) -> str:
    """Http access json log file format.

    Args:
        record (dict): Log record as dictionary.

    Returns:
        str: Format for http access json log record.
    """

    if "http_info" not in record["extra"]:
        return ""

    _http_info = record["extra"]["http_info"]
    if "datetime" not in _http_info:
        _http_info["datetime"] = record["time"].isoformat()
        record["extra"]["http_info"] = _http_info

    return "{extra[http_info]}\n"
