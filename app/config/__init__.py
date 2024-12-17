import os
from dotenv import load_dotenv
from app.config.logging import LOCAL_LOGGING, STRUCTURED_LOGGING

load_dotenv()


class BaseConfig(object):
    ENVIRONMENT = os.environ.get("CLA_ENVIRONMENT", "unknown")

    # The default DB parameters are set to allow you to connect to the Docker DB
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5436")
    DB_NAME = os.environ.get("DB_NAME", "case_api")

    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    DB_LOGGING = os.environ.get("DB_LOGGING", "False") == "True"

    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    SECRET_KEY = os.environ.get("SECRET_KEY", "TEST_KEY")

    LOGGER_CONFIG = STRUCTURED_LOGGING


class LocalConfig(BaseConfig):
    """Local development config overrides"""

    ENVIRONMENT = "local"
    LOGGER_CONFIG = LOCAL_LOGGING


def get_config():
    env = os.environ.get("CLA_ENVIRONMENT", "local").lower()
    if env == "local":
        return LocalConfig()
    return BaseConfig()


Config = get_config()
