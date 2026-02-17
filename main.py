import os
import sentry_sdk
from dotenv import load_dotenv




load_dotenv()

SENTRY_DSN=os.getenv("SENTRY_DSN")


sentry_sdk.init(
    dsn=SENTRY_DSN
)


