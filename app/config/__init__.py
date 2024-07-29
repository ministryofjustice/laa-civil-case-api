import os


class Config(object):
    ENVIRONMENT = os.environ.get("CLA_ENVIRONMENT", "unknown")
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
