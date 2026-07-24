from datetime import datetime
import logging
import os


def setup_logger() -> None:
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = f"{log_directory}/app_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, "a", "utf-8"),
            logging.StreamHandler(),  # コンソールにも出力
        ],
    )

    logging.info("ロガーを初期化しました.")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
