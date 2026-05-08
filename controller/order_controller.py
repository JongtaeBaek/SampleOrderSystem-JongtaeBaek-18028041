import uuid

from model.order import Order, OrderStatus
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class OrderController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository) -> None:
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def reserve(self, sample_id: str, customer_name: str, quantity: int) -> bool:
        samples = self._sample_repo.load()
        if not any(s.sample_id == sample_id for s in samples):
            print(f"오류: 존재하지 않는 시료 ID입니다 — {sample_id}")
            return False
        order_id = str(uuid.uuid4())[:8]
        orders = self._order_repo.load()
        orders.append(Order(order_id, sample_id, customer_name, quantity, OrderStatus.RESERVED))
        self._order_repo.save(orders)
        return True
