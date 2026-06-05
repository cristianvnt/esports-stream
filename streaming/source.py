import queue
from typing import Any, List
from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition

class _QueuePartition(StatefulSourcePartition):
    def __init__(self, q: "queue.Queue"):
        self._q = q

    def next_batch(self) -> List[Any]:
        items: List[Any] = []
        try:
            while True:
                items.append(self._q.get_nowait())
        except queue.Empty:
            pass
        return items
    
    def snapshot(self) -> None:
        return None
    
class QueueSource(FixedPartitionedSource):
    def __init__(self, q: "queue.Queue"):
        self._q = q

    def list_parts(self) -> List[str]:
        return ["singleton"]
    
    def build_part(self, step_id: str, for_part: str, resume_state) -> _QueuePartition:
        return _QueuePartition(self._q)
