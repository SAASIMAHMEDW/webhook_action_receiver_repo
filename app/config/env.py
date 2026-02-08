from os import getenv
from dotenv import load_dotenv

load_dotenv()


def get_env(key: str, required: bool = True, default=None) -> str:
    value = getenv(key)

    if value is None or value.strip() == "":
        if required and default is None:
            raise RuntimeError(f"Environment variable {key} is missing")
        return default

    return value


def load_env():
    return {
        "PORT": int(get_env("PORT", required=False, default=5000)),
        "FLASK_ENV": get_env("FLASK_ENV", required=False, default="development"),
        "FLASK_DEBUG": get_env("FLASK_DEBUG", required=False, default="False").lower() == "true",
        "SECRET_KEY": get_env("SECRET_KEY", required=False, default="supersecretkey"),
        "MONGO_URI": get_env("MONGO_URI", required=True),
        "LOG_LEVEL": get_env("LOG_LEVEL", required=False, default="INFO").upper(),
    }

ENV = load_env()