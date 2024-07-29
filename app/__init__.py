from app.main import create_app
from config import Config
import sentry_sdk


if Config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=0.01,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=0.2,
        # This can either be dev, uat, staging, or production.
        # It is set by CLA_ENVIRONMENT in the helm charts.
        environment=Config.ENVIRONMENT,
    )


case_api = create_app()


@case_api.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
