import logging
import logging.config
import contextvars

request_id_var = contextvars.ContextVar("request_id", default=None)

class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("-")
        return True
    
    def setup_Logging(level: str = "INFO"):
        LOGGING = {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_id_filter": {
                    "()": RequestIDFilter,
                }
            },
            "formatters": {
                "standard": {
                    "format": "[%(asctime)s] [%(levelname)s] [%(request_id)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "filters": ["request_id_filter"],
                    "level": level,
                },
            },
            "loggers": {
                "": {  # root logger
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }