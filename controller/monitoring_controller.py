from model.order import OrderStatus
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class MonitoringController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository) -> None:
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def order_summary(self) -> dict[str, int]:
        orders = self._order_repo.load()
        target = [OrderStatus.RESERVED, OrderStatus.PRODUCING, OrderStatus.CONFIRMED, OrderStatus.RELEASE]
        return {s.value: sum(1 for o in orders if o.status == s) for s in target}

    def stock_summary(self) -> list[dict]:
        samples = self._sample_repo.load()
        orders = self._order_repo.load()
        result = []
        for s in samples:
            active_quantity = sum(
                o.quantity for o in orders
                if o.sample_id == s.sample_id and o.status in (OrderStatus.RESERVED, OrderStatus.PRODUCING)
            )
            if s.stock == 0:
                stock_status = "고갈"
            elif s.stock < active_quantity:
                stock_status = "부족"
            else:
                stock_status = "여유"
            result.append({
                "sample_id": s.sample_id,
                "name": s.name,
                "stock": s.stock,
                "active_quantity": active_quantity,
                "stock_status": stock_status,
            })
        return result
