from datetime import datetime
from typing import Any, Callable, List
from bytewax.outputs import DynamicSink, StatelessSinkPartition

class _ConsolePartition(StatelessSinkPartition):
    def __init__(self, formatter: Callable[[Any], str]):
        self._formatter = formatter

    def write_batch(self, items: List[Any]) -> None:
        for item in items:
            line = self._formatter(item)
            if line is not None:
                stamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{stamp}] {line}")

class ConsoleSink(DynamicSink):
    def __init__(self, formatter: Callable[[Any], str]):
        self._formatter = formatter

    def build(self, step_id: str, worker_index: int, worker_count: int) -> _ConsolePartition:
        return _ConsolePartition(self._formatter)
