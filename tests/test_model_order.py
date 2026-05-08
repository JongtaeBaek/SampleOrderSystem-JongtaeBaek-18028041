"""Tests for model/order.py — 100% coverage."""
import dataclasses

from model.order import Order, OrderStatus


class TestOrderStatus:
    """Tests for OrderStatus Enum."""

    def test_all_enum_values_exist(self):
        """All five OrderStatus members are present with correct string values."""
        assert OrderStatus.RESERVED.value == "RESERVED"
        assert OrderStatus.CONFIRMED.value == "CONFIRMED"
        assert OrderStatus.PRODUCING.value == "PRODUCING"
        assert OrderStatus.RELEASE.value == "RELEASE"
        assert OrderStatus.REJECTED.value == "REJECTED"

    def test_enum_from_value(self):
        """OrderStatus can be reconstructed from its string value."""
        assert OrderStatus("RESERVED") == OrderStatus.RESERVED
        assert OrderStatus("CONFIRMED") == OrderStatus.CONFIRMED
        assert OrderStatus("PRODUCING") == OrderStatus.PRODUCING
        assert OrderStatus("RELEASE") == OrderStatus.RELEASE
        assert OrderStatus("REJECTED") == OrderStatus.REJECTED

    def test_enum_members_count(self):
        """Exactly 5 members are defined."""
        assert len(OrderStatus) == 5

    def test_enum_identity(self):
        """Enum members are singletons."""
        assert OrderStatus.RESERVED is OrderStatus("RESERVED")


class TestOrder:
    """Tests for Order dataclass."""

    def test_order_creation(self):
        """Order is created with all required fields."""
        o = Order(
            order_id="abc12345",
            sample_id="S001",
            customer_name="ACME Corp",
            quantity=50,
            status=OrderStatus.RESERVED,
        )
        assert o.order_id == "abc12345"
        assert o.sample_id == "S001"
        assert o.customer_name == "ACME Corp"
        assert o.quantity == 50
        assert o.status == OrderStatus.RESERVED

    def test_order_status_transition(self):
        """Order.status field can be updated to reflect state transitions."""
        o = Order("id001", "S001", "Customer A", 10, OrderStatus.RESERVED)
        o.status = OrderStatus.CONFIRMED
        assert o.status == OrderStatus.CONFIRMED

        o.status = OrderStatus.RELEASE
        assert o.status == OrderStatus.RELEASE

    def test_order_status_producing(self):
        """Order can be placed in PRODUCING status."""
        o = Order("id002", "S002", "Customer B", 100, OrderStatus.PRODUCING)
        assert o.status == OrderStatus.PRODUCING

    def test_order_status_rejected(self):
        """Order can be placed in REJECTED status."""
        o = Order("id003", "S003", "Customer C", 5, OrderStatus.REJECTED)
        assert o.status == OrderStatus.REJECTED

    def test_order_is_dataclass(self):
        """Order is a proper dataclass; asdict works but status becomes Enum object."""
        o = Order("id004", "S001", "Customer D", 20, OrderStatus.CONFIRMED)
        d = dataclasses.asdict(o)
        assert d["order_id"] == "id004"
        assert d["sample_id"] == "S001"
        assert d["customer_name"] == "Customer D"
        assert d["quantity"] == 20
        # dataclasses.asdict on an Enum field returns the Enum value directly
        assert d["status"] == OrderStatus.CONFIRMED

    def test_order_equality(self):
        """Two Order instances with the same values are equal."""
        o1 = Order("id001", "S001", "Cust", 5, OrderStatus.RESERVED)
        o2 = Order("id001", "S001", "Cust", 5, OrderStatus.RESERVED)
        assert o1 == o2

    def test_order_inequality(self):
        """Two Order instances with different statuses are not equal."""
        o1 = Order("id001", "S001", "Cust", 5, OrderStatus.RESERVED)
        o2 = Order("id001", "S001", "Cust", 5, OrderStatus.CONFIRMED)
        assert o1 != o2
