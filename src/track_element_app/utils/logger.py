import logging
import logging.config
from typing import Any


def setup_logger() -> None:
    """
    アプリ全体のロギングを設定する。
    fileConfig ではなく dictConfig を使用することで、
    柔軟なフィルター制御と、disable_existing_loggers=False による外部ライブラリロガーの保護を両立。
    """
    log_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,  # TrueにするとSpotipy内部のログが消え去る罠を防ぐ
        "formatters": {
            "default": {
                # 遅延フォーマット評価（%s）を前提とした標準フォーマット
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }
    logging.config.dictConfig(log_config)

    # 遅延フォーマット評価の挙動検証用
    logger = logging.getLogger("track_element_app")
    logger.info("Logger initialized successfully using dictConfig.")
