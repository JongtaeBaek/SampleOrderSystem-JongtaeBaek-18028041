from model.order import Order, OrderStatus

_TABLE_WIDTH = 72
_TABLE_HEADER = f"{'주문ID':<10} {'시료ID':<12} {'고객명':<20} {'수량':>6} {'상태':<12}"


class OrderView:
    def prompt_reserve(self) -> tuple[str, str, int]:
        sample_id = input("시료 ID: ").strip()
        customer_name = input("고객명: ").strip()
        quantity = int(input("주문 수량: ").strip())
        return sample_id, customer_name, quantity

    def show_order_list(self, orders: list[Order]) -> None:
        if not orders:
            print("주문이 없습니다.")
            return
        print(_TABLE_HEADER)
        print("-" * _TABLE_WIDTH)
        for o in orders:
            print(f"{o.order_id:<10} {o.sample_id:<12} {o.customer_name:<20} {o.quantity:>6} {o.status.value:<12}")

    def show_reserve_success(self, order_id: str) -> None:
        print(f"주문 예약 완료: {order_id}")

    def prompt_order_id(self, action: str) -> str:
        return input(f"{action}할 주문 ID: ").strip()

    def show_reserved_list(self, orders: list[Order]) -> None:
        if not orders:
            print("접수된 주문이 없습니다.")
            return
        self.show_order_list(orders)

    def show_approve_success(self, order_id: str, status: OrderStatus) -> None:
        print(f"승인 완료: {order_id} → {status.value}")

    def show_reject_success(self, order_id: str) -> None:
        print(f"거절 완료: {order_id} → REJECTED")

    def show_confirmed_list(self, orders: list[Order]) -> None:
        if not orders:
            print("출고 대기 중인 주문이 없습니다.")
            return
        self.show_order_list(orders)

    def show_release_success(self, order_id: str) -> None:
        print(f"출고 완료: {order_id} → RELEASE")
