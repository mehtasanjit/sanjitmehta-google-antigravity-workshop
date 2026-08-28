import time
import uuid
import logging
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware

request_id_var: ContextVar = ContextVar('request_id', default=None)


def get_request_id():
    return request_id_var.get()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get('X-Request-ID') or uuid.uuid4().hex
        token = request_id_var.set(rid)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers['X-Request-ID'] = rid
        logging.getLogger('app.access').info(
            'request',
            extra={
                'request_id': rid,
                'method': request.method,
                'path': request.url.path,
                'status': response.status_code,
                'duration_ms': duration_ms
            }
        )
        return response
