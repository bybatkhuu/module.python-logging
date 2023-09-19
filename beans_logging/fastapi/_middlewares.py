# -*- coding: utf-8 -*-

import json
import time
from uuid import uuid4

from fastapi import Request, Response
from fastapi.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

from beans_logging import logger


class HttpAccessLogMiddleware(BaseHTTPMiddleware):
    """Http access log middleware for FastAPI.

    Inherits:
        BaseHTTPMiddleware: Base HTTP middleware class from starlette.

    Attributes:
        _DEBUG_FORMAT     (str ): Default http access log debug message format. Defaults to '<n>[{request_id}]</n> {client_host} {user_id} "<u>{method} {url_path}</u> HTTP/{http_version}"'.
        _MSG_FORMAT       (str ): Default http access log message format. Defaults to '<n><w>[{request_id}]</w></n> {client_host} {user_id} "<u>{method} {url_path}</u> HTTP/{http_version}" {status_code} {content_length}B {response_time}ms'.

        has_proxy_headers (bool): If True, use proxy headers to get http request info. Defaults to False.
        has_cf_headers    (bool): If True, use cloudflare headers to get http request info. Defaults to False.
        debug_format      (str ): Http access log debug message format. Defaults to `HttpAccessLogMiddleware._DEBUG_FORMAT`.
        msg_format        (str ): Http access log message format. Defaults to `HttpAccessLogMiddleware._MSG_FORMAT`.
        use_debug_log     (bool): If True, use debug log to log http access log. Defaults to True.
    """

    _DEBUG_FORMAT = '<n>[{request_id}]</n> {client_host} {user_id} "<u>{method} {url_path}</u> HTTP/{http_version}"'
    _MSG_FORMAT = '<n><w>[{request_id}]</w></n> {client_host} {user_id} "<u>{method} {url_path}</u> HTTP/{http_version}" {status_code} {content_length}B {response_time}ms'

    def __init__(
        self,
        app,
        has_proxy_headers: bool = False,
        has_cf_headers: bool = False,
        debug_format: str = _DEBUG_FORMAT,
        msg_format: str = _MSG_FORMAT,
        use_debug_log: bool = True,
    ):
        super().__init__(app)
        self.has_proxy_headers = has_proxy_headers
        self.has_cf_headers = has_cf_headers
        self.debug_format = debug_format
        self.msg_format = msg_format
        self.use_debug_log = use_debug_log

    async def dispatch(self, request: Request, call_next) -> Response:
        _logger = logger.opt(colors=True, record=True)

        _http_info = {}
        _http_info["request_id"] = uuid4().hex
        if "X-Request-ID" in request.headers:
            _http_info["request_id"] = request.headers.get("X-Request-ID")
        elif "X-Correlation-ID" in request.headers:
            _http_info["request_id"] = request.headers.get("X-Correlation-ID")

        ## Set request_id to request state:
        request.state.request_id = _http_info["request_id"]

        _http_info["client_host"] = request.client.host
        _http_info["request_proto"] = request.url.scheme
        _http_info["request_host"] = (
            request.url.hostname if request.url.hostname else ""
        )
        if (request.url.port != 80) and (request.url.port != 443):
            _http_info[
                "request_host"
            ] = f"{_http_info['request_host']}:{request.url.port}"

        _http_info["request_port"] = request.url.port
        _http_info["http_version"] = request.scope["http_version"]

        if self.has_proxy_headers:
            if "X-Real-IP" in request.headers:
                _http_info["client_host"] = request.headers.get("X-Real-IP")
            elif "X-Forwarded-For" in request.headers:
                _http_info["client_host"] = request.headers.get(
                    "X-Forwarded-For"
                ).split(",")[0]
                _http_info["h_x_forwarded_for"] = request.headers.get("X-Forwarded-For")

            if "X-Forwarded-Proto" in request.headers:
                _http_info["request_proto"] = request.headers.get("X-Forwarded-Proto")

            if "X-Forwarded-Host" in request.headers:
                _http_info["request_host"] = request.headers.get("X-Forwarded-Host")
            elif "Host" in request.headers:
                _http_info["request_host"] = request.headers.get("Host")

            if "X-Forwarded-Port" in request.headers:
                try:
                    _http_info["request_port"] = int(
                        request.headers.get("X-Forwarded-Port")
                    )
                except ValueError:
                    logger.warning(
                        f"`X-Forwarded-Port` header value '{request.headers.get('X-Forwarded-Port')}' is invalid, should be parseable to <int>!"
                    )

            if "Via" in request.headers:
                _http_info["h_via"] = request.headers.get("Via")

            if self.has_cf_headers:
                if "CF-Connecting-IP" in request.headers:
                    _http_info["client_host"] = request.headers.get("CF-Connecting-IP")
                    _http_info["h_cf_connecting_ip"] = request.headers.get(
                        "CF-Connecting-IP"
                    )
                elif "True-Client-IP" in request.headers:
                    _http_info["client_host"] = request.headers.get("True-Client-IP")
                    _http_info["h_true_client_ip"] = request.headers.get(
                        "True-Client-IP"
                    )

                if "CF-IPCountry" in request.headers:
                    _http_info["client_country"] = request.headers.get("CF-IPCountry")
                    _http_info["h_cf_ipcountry"] = request.headers.get("CF-IPCountry")

                if "CF-RAY" in request.headers:
                    _http_info["h_cf_ray"] = request.headers.get("CF-RAY")

                if "cf-ipcontinent" in request.headers:
                    _http_info["h_cf_ipcontinent"] = request.headers.get(
                        "cf-ipcontinent"
                    )

                if "cf-ipcity" in request.headers:
                    _http_info["h_cf_ipcity"] = request.headers.get("cf-ipcity")

                if "cf-iplongitude" in request.headers:
                    _http_info["h_cf_iplongitude"] = request.headers.get(
                        "cf-iplongitude"
                    )

                if "cf-iplatitude" in request.headers:
                    _http_info["h_cf_iplatitude"] = request.headers.get("cf-iplatitude")

                if "cf-postal-code" in request.headers:
                    _http_info["h_cf_postal_code"] = request.headers.get(
                        "cf-postal-code"
                    )

                if "cf-timezone" in request.headers:
                    _http_info["h_cf_timezone"] = request.headers.get("cf-timezone")

        _http_info["method"] = request.method
        _http_info["url_path"] = request.url.path
        if request.url.query:
            _http_info["url_path"] = f"{request.url.path}?{request.url.query}"

        _http_info["url_query_params"] = request.query_params._dict
        _http_info["url_path_params"] = request.path_params

        _http_info["h_referer"] = request.headers.get("Referer", "-")
        _http_info["h_user_agent"] = request.headers.get("User-Agent", "-")
        _http_info["h_accept"] = request.headers.get("Accept", "")
        _http_info["h_content_type"] = request.headers.get("Content-Type", "")

        if "Origin" in request.headers:
            _http_info["h_origin"] = request.headers.get("Origin")

        _http_info["user_id"] = "-"
        if hasattr(request.state, "user_id"):
            _http_info["user_id"] = str(request.state.user_id)

        ## Debug log:
        if self.use_debug_log:
            _debug_msg = self.debug_format.format(**_http_info)
            # _logger.debug(_debug_msg)
            await run_in_threadpool(
                _logger.debug,
                _debug_msg,
            )
        ## Debug log

        ## Set http info to request state:
        request.state.http_info = _http_info

        ## Process request:
        _start_time = time.time()
        response = await call_next(request)
        _http_info["response_time"] = round((time.time() - _start_time) * 1000, 1)
        ## Response processed

        if "X-Process-Time" in response.headers:
            try:
                _http_info["response_time"] = float(
                    response.headers.get("X-Process-Time")
                )
            except ValueError:
                logger.warning(
                    f"`X-Process-Time` header value '{response.headers.get('X-Process-Time')}' is invalid, should be parseable to <float>!"
                )
        else:
            response.headers["X-Process-Time"] = str(_http_info["response_time"])

        if "X-Request-ID" not in response.headers:
            response.headers["X-Request-ID"] = _http_info["request_id"]

        if hasattr(request.state, "user_id"):
            _http_info["user_id"] = str(request.state.user_id)

        _http_info["status_code"] = response.status_code
        _http_info["content_length"] = 0
        if "Content-Length" in response.headers:
            try:
                _http_info["content_length"] = int(
                    response.headers.get("Content-Length")
                )
            except ValueError:
                logger.warning(
                    f"`Content-Length` header value '{response.headers.get('Content-Length')}' is invalid, should be parseable to <int>!"
                )

        try:
            json.dumps(_http_info)
        except TypeError:
            logger.warning(
                "Can not serialize `http_info` to json string in HttpAccessLogMiddleware!"
            )

        ## Http access log:
        _LEVEL = "INFO"
        _msg_format = self.msg_format
        if _http_info["status_code"] < 200:
            _LEVEL = "DEBUG"
            _msg_format = f'<d>{_msg_format.replace("{status_code}", "<n><b><k>{status_code}</k></b></n>")}</d>'
        elif (200 <= _http_info["status_code"]) and (_http_info["status_code"] < 300):
            _LEVEL = "SUCCESS"
            _msg_format = f'<w>{_msg_format.replace("{status_code}", "<lvl>{status_code}</lvl>")}</w>'
        elif (300 <= _http_info["status_code"]) and (_http_info["status_code"] < 400):
            _LEVEL = "INFO"
            _msg_format = f'<d>{_msg_format.replace("{status_code}", "<n><b><c>{status_code}</c></b></n>")}</d>'
        elif (400 <= _http_info["status_code"]) and (_http_info["status_code"] < 500):
            _LEVEL = "WARNING"
            _msg_format = _msg_format.replace("{status_code}", "<r>{status_code}</r>")
        elif 500 <= _http_info["status_code"]:
            _LEVEL = "ERROR"
            _msg_format = (
                f'{_msg_format.replace("{status_code}", "<n>{status_code}</n>")}'
            )

        _msg = _msg_format.format(**_http_info)
        # _logger.bind(http_info=_http_info).log(_LEVEL, _msg)
        await run_in_threadpool(
            _logger.bind(http_info=_http_info).log,
            _LEVEL,
            _msg,
        )
        ## Http access log

        return response
