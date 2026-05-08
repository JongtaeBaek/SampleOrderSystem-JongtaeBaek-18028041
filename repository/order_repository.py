import json
import dataclasses
from pathlib import Path

from model.order import Order, OrderStatus

_DEFAULT_PATH = Path("data/orders.json")


class OrderRepository:
    def __init__(self, path: Path = _DEFAULT_PATH) -> None:
        self._path = path

    def load(self) -> list[Order]:
        if not self._path.exists():
            return []
        with self._path.open(encoding="utf-8") as f:
            records = json.load(f)
        return [
            Order(
                order_id=r["order_id"],
                sample_id=r["sample_id"],
                customer_name=r["customer_name"],
                quantity=r["quantity"],
                status=OrderStatus(r["status"]),
            )
            for r in records
        ]

    def save(self, orders: list[Order]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        serialized = [
            {**dataclasses.asdict(order), "status": order.status.value}
            for order in orders
        ]
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(serialized, f, ensure_ascii=False, indent=2)
