import functools
import logging
import timeit
from collections.abc import Callable
from typing import Any, Protocol, cast

logger = logging.getLogger("track_element_app.services.spotify_client")


# 実行時間属性を持つ関数オブジェクトの型定義
class MeasurableFunction(Protocol):
    execution_time: float
    __name__: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


# =====================================================================
# 1. 実行時間計測デコレータ
# =====================================================================
def measure_time[F: Callable[..., Any]](func: F) -> F:
    """関数の実行時間を計測し、ログ出力および関数属性へのメタデータ保持を行う。"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()

        elapsed_time = end_time - start_time

        # FastHTMLのUI表示用に実行時間を関数オブジェクトへ記録
        measurable_wrapper = cast(MeasurableFunction, wrapper)
        measurable_wrapper.execution_time = elapsed_time

        # 遅延フォーマット評価（%s）を徹底したロギング
        logger.info("Execution time for %s: %f seconds", func.__name__, elapsed_time)
        return result

    return cast(F, wrapper)


# =====================================================================
# 2. ログ出力デコレータ
# =====================================================================
def log_action(action_name: str) -> Callable[[Any], Any]:
    """関数の実行開始と終了（正常終了）をログに記録するシンプルなデコレータ。"""

    def decorator[F: Callable[..., Any]](func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info("Starting action: %s", action_name)
            result = func(*args, **kwargs)
            logger.info("Successfully completed action: %s", action_name)
            return result

        return cast(F, wrapper)

    return decorator
