from model.order import OrderStatus
from model.production import ProductionJob, ProductionQueue
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class ProductionController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository) -> None:
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def show_current(self, production_queue: ProductionQueue) -> ProductionJob | None:
        return production_queue.peek()

    def complete(self, production_queue: ProductionQueue) -> bool:
        if production_queue.is_empty():
            print("생산 중인 작업이 없습니다.")
            return False
        job = production_queue.dequeue()
        samples = self._sample_repo.load()
        sample = next((s for s in samples if s.sample_id == job.sample_id), None)
        sample.stock += job.actual_production
        self._sample_repo.save(samples)
        orders = self._order_repo.load()
        order = next((o for o in orders if o.order_id == job.order_id), None)
        order.status = OrderStatus.CONFIRMED
        self._order_repo.save(orders)
        return True

    def list_queue(self, production_queue: ProductionQueue) -> list[ProductionJob]:
        return production_queue.list_all()
