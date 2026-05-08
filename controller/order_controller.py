import uuid

from model.order import Order, OrderStatus
from model.production import ProductionJob, ProductionQueue
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

    def list_reserved(self) -> list[Order]:
        orders = self._order_repo.load()
        return [o for o in orders if o.status == OrderStatus.RESERVED]

    def approve(self, order_id: str, production_queue: ProductionQueue) -> bool:
        orders = self._order_repo.load()
        order = self._find_reserved_order(orders, order_id)
        if order is None:
            print(f"오류: 승인 가능한 주문이 아닙니다 — {order_id}")
            return False
        samples = self._sample_repo.load()
        sample = next(s for s in samples if s.sample_id == order.sample_id)
        if sample.stock >= order.quantity:
            self._confirm_with_stock(order, sample, orders, samples)
        else:
            self._enqueue_for_production(order, sample, orders, production_queue)
        return True

    def reject(self, order_id: str) -> bool:
        orders = self._order_repo.load()
        order = self._find_reserved_order(orders, order_id)
        if order is None:
            print(f"오류: 거절 가능한 주문이 아닙니다 — {order_id}")
            return False
        order.status = OrderStatus.REJECTED
        self._order_repo.save(orders)
        return True

    def _find_reserved_order(self, orders: list[Order], order_id: str) -> Order | None:
        order = next((o for o in orders if o.order_id == order_id), None)
        if order is None or order.status != OrderStatus.RESERVED:
            return None
        return order

    def _confirm_with_stock(self, order: Order, sample, orders: list[Order], samples: list) -> None:
        sample.stock -= order.quantity
        order.status = OrderStatus.CONFIRMED
        self._sample_repo.save(samples)
        self._order_repo.save(orders)

    def _enqueue_for_production(self, order: Order, sample, orders: list[Order], production_queue: ProductionQueue) -> None:
        shortage = order.quantity - sample.stock
        job = ProductionJob.create(
            order.order_id, order.sample_id, shortage,
            sample.yield_rate, sample.avg_production_time
        )
        production_queue.enqueue(job)
        order.status = OrderStatus.PRODUCING
        self._order_repo.save(orders)
