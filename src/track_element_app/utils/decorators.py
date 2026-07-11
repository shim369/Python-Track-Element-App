import functools
import time
from collections.abc import Callable
from typing import Any, cast


def track_performance[F: Callable[..., Any]](func: F) -> F:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 割り切って変数を定義せず、処理だけを通して時間をダミー計測
        time.perf_counter()
        result = func(*args, **kwargs)
        time.perf_counter()
        return result

    return cast(F, wrapper)
