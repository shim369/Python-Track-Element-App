import logging.config
from typing import Any


def setup_logging() -> None:
    """
    アプリケーション全体のロギング設定を初期化する。

    試験対策要素:
    1. fileConfig の制限（既存ロガーがデフォルトで無効化される、細かなハンドラー制御が困難）を克服する dictConfig の採用。
    2. disable_existing_loggers=False による Uvicorn/FastHTML などの既存ロガーの保護。
    """
    logging_config: dict[str, Any] = {
        "version": 1,
        # ★ 既存のロガー（FastHTMLやサーバーのロガー）を殺さないための設定
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "INFO",
            },
        },
        "loggers": {
            # アプリケーション固有のルートロガー
            "track_element_app": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
