from pydantic import BaseSettings

DOTENV_FILE = "./.env"


class Settings(BaseSettings):
    """
    Server config settings
    """

    class Config:
        env_file = DOTENV_FILE
        env_file_encoding = "utf-8"

    LOG_LEVEL: int = 0
    # макисмальная длина текста чтобы разместить его на одной линии с уровнем лога
    MAX_WITH_LOG_OF_OBJ: int = 120
    # https://loguru.readthedocs.io/en/stable/resources/recipes.html#adapting-colors-and-format-of-logged-messages-dynamically
    # https://docs-python.ru/standart-library/modul-string-python/klass-template-modulja-string/
    # https://loguru.readthedocs.io/en/stable/api/logger.html#color
    # https://rich.readthedocs.io/en/stable/style.html

    LOGURU_EXCEPTION_FORMAT_LONG: str = "{extra[msg]}\n{exception}\n"
    LOGURU_DIAGNOSE: str = "NO"

    MIN_WIDTH: int = 12
    MAX_WIDTH: int = 15
    RATIO_MAIN: int = 80
    RATIO_FROM: int = 40


config = Settings()
