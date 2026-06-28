# coding=utf-8
import time


class Profiler:
    """
    轻量级耗时收集器，用于子系统 onUpdate/onRender 及各调度器的性能诊断。

    使用方式:
        from architect.core.profiler import profiler

        with profiler.record('MySystem.onUpdate'):
            do_work()

        snap = profiler.flush()  # { 'MySystem.onUpdate': { 'avg_ms': 1.2, 'max_ms': 3.4, 'count': 60 } }
    """
    def __init__(self):
        self._records = {}  # type: dict[str, list[float]]
        self._enabled = True

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def record(self, key):
        # type: (str) -> _TimerContext
        """
        返回一个上下文管理器，进入 with 块时开始计时，
        退出 with 块时将耗时（秒）记录到 key 下。
        """
        return _TimerContext(self, key)

    def _add(self, key, elapsed_seconds):
        # type: (str, float) -> None
        if not self._enabled:
            return
        self._records.setdefault(key, []).append(elapsed_seconds)

    def flush(self):
        # type: () -> dict
        """
        返回当前所有记录的统计快照并重置。

        :return: { key: { 'avg_ms': float, 'max_ms': float, 'count': int } }
        """
        snap = {}
        for key, times in self._records.items():
            if times:
                snap[key] = {
                    'avg_ms': sum(times) / len(times) * 1000.0,
                    'max_ms': max(times) * 1000.0,
                    'count': len(times)
                }
        self._records.clear()
        return snap

    def snapshot(self):
        # type: () -> dict
        """
        返回当前所有记录的统计快照但不重置。

        :return: { key: { 'avg_ms': float, 'max_ms': float, 'count': int } }
        """
        snap = {}
        for key, times in self._records.items():
            if times:
                snap[key] = {
                    'avg_ms': sum(times) / len(times) * 1000.0,
                    'max_ms': max(times) * 1000.0,
                    'count': len(times)
                }
        return snap


class _TimerContext(object):
    def __init__(self, profiler_instance, key):
        self._profiler = profiler_instance
        self._key = key
        self._start = None

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self._start
        self._profiler._add(self._key, elapsed)
        return False


# 全局 Profiler 实例，供所有模块共用
profiler = Profiler()


from .log import info as _log_info


def TimeCost(func):
    """
    函数级耗时装饰器（保留原有行为，底层使用 profiler）。
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        _log_info('Time cost: {}s', end - start)
        return result
    return wrapper
