from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from model.order import Order, OrderStatus


class ReleaseController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository) -> None:
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def list_confirmed(self) -> list[Order]:
        orders = self._order_repo.load()
        return [o for o in orders if o.status == OrderStatus.CONFIRMED]

    def release(self, order_id: str) -> bool:
        orders = self._order_repo.load()
        order = next((o for o in orders if o.order_id == order_id), None)
        if order is None or order.status != OrderStatus.CONFIRMED:
            print(f"오류: 출고 가능한 주문이 아닙니다 — {order_id}")
            return False
        samples = self._sample_repo.load()
        sample = next((s for s in samples if s.sample_id == order.sample_id), None)
        sample.stock -= order.quantity
        order.status = OrderStatus.RELEASE
        self._sample_repo.save(samples)
        self._order_repo.save(orders)
        return True
