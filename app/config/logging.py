import sys
import logging.config
import structlog
from typing import Dict, Any
from uvicorn.logging import DefaultFormatter


class CustomConsoleRenderer(DefaultFormatter):
    def __init__(self):
        super().__init__(fmt="%(levelprefix)s %(message)s", use_colors=True)

    def __call__(self, logger, name, event_dict):
        # Create message with any additional structured logging arguments
        message = event_dict.pop("event", "")

        level = event_dict.get("level", "info").upper()
        log_level = getattr(logging, level, logging.INFO)

        excluded_event_keys = {
            "timestamp",
            "logger",
            "level",
        }  # These shouldn't display in the local logs

        extra_args = " - ".join(
            f"{key}: {value}"
            for key, value in event_dict.items()
            if key not in excluded_event_keys
        )

        return self.format(
            logging.LogRecord(
                name=logger.name,
                level=log_level,
                pathname="",
                lineno=0,
                msg=f"{message}{' - ' + extra_args if extra_args else ''}",
                args=(),
                exc_info=None,
            )
        )


STRUCTURED_LOG_PROCESSORS = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]

LOCAL_LOGGING: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "custom": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": CustomConsoleRenderer(),
            "foreign_pre_chain": [
                *STRUCTURED_LOG_PROCESSORS,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
        },
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": True,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
        "custom": {
            "formatter": "custom",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "": {  # Root logger using custom formatter
            "handlers": ["custom"],
            "level": "INFO",
        },
    },
}

STRUCTURED_LOGGING: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": STRUCTURED_LOG_PROCESSORS,
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
    },
}

LoggingConfig = STRUCTURED_LOGGING | LOCAL_LOGGING


def setup_logging(logger_config: LoggingConfig) -> None:
    structlog.configure(
        processors=[
            *STRUCTURED_LOG_PROCESSORS,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logging.config.dictConfig(logger_config)
