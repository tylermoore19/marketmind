import time
import logging
from flask import request, g

def register_request_logging(app, logger=None):
    # accept injected logger to avoid circular import; fallback to local logger
    if logger is None:
        logger = logging.getLogger('request_logger')
        if not logger.handlers:
            h = logging.StreamHandler()
            h.setLevel(logging.INFO)
            fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')
            h.setFormatter(fmt)
            logger.addHandler(h)
            logger.setLevel(logging.INFO)
            
    @app.before_request
    def _start_timer():
        g._request_start_time = time.time()
        g._request_start_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(g._request_start_time))

    @app.after_request
    def _log_request(response):
        try:
            start = getattr(g, '_request_start_time', None)
            end = time.time()
            duration = (end - start) if start is not None else None
            start_dt = getattr(g, '_request_start_datetime', None)

            # status
            status_code = getattr(response, 'status_code', None)

            # response data - limit to a reasonable size
            data_text = None
            try:
                # get_data returns bytes for Response, convert to text
                raw = response.get_data(as_text=True)
                max_len = 2000
                data_text = raw if len(raw) <= max_len else raw[:max_len] + '...<truncated>'
            except Exception:
                data_text = '<unavailable>'

            logger.info(
                "Request log: method=%s path=%s start=%s end=%s duration=%.4fs status=%s data=%s",
                request.method,
                request.path,
                start_dt,
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end)),
                duration if duration is not None else -1,
                status_code,
                data_text
            )
        except Exception as e:
            # don't break response flow on logging errors
            logger.exception('Failed to log request: %s', e)

        return response
