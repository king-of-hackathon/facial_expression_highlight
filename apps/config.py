from pathlib import Path

basedir = Path(__file__).parent.parent

class BaseConfig:
    UPLOAD_FOLDER = str(Path(basedir, "apps", "uploads"))
    SECRET_KEY = "super secret key"

class LocalConfig(BaseConfig):
    WTF_CSRF_ENABLED = True

class TestingConfig(BaseConfig):
    WTF_CSRF_ENABLED = False


config = {
    "testing": TestingConfig,
    "local": LocalConfig,
}