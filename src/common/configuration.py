import os

class AppSettings:
    app_env: str = os.environ.get("APP_ENV", "development")
    host: str = os.environ.get("APP_HOST", "0.0.0.0")
    port: int = int(os.environ.get("APP_PORT", 8000))
    workers: int = int(os.environ.get("APP_WORKERS_COUNT", 1))
