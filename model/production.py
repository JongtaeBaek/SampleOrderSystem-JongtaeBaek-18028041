import math
from collections import deque
from dataclasses import dataclass

_YIELD_SAFETY_FACTOR = 0.9


@dataclass
class ProductionJob:
    order_id: str
    sample_id: str
    required_quantity: int
    actual_production: int
    total_time: float

    @staticmethod
    def create(order_id: str, sample_id: str, required_quantity: int,
               yield_rate: float, avg_production_time: float) -> "ProductionJob":
        actual_production = math.ceil(required_quantity / (yield_rate * _YIELD_SAFETY_FACTOR))
        total_time = avg_production_time * actual_production
        return ProductionJob(
            order_id=order_id,
            sample_id=sample_id,
            required_quantity=required_quantity,
            actual_production=actual_production,
            total_time=total_time,
        )


class ProductionQueue:
    def __init__(self) -> None:
        self._queue: deque[ProductionJob] = deque()

    def enqueue(self, job: ProductionJob) -> None:
        self._queue.append(job)

    def dequeue(self) -> ProductionJob:
        return self._queue.popleft()

    def peek(self) -> ProductionJob | None:
        return self._queue[0] if self._queue else None

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def list_all(self) -> list[ProductionJob]:
        return list(self._queue)
