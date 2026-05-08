"""Tests for controller/monitoring_controller.py — 100% coverage (Phase 6)."""
from unittest.mock import MagicMock

from model.order import Order, OrderStatus
from model.sample import Sample
from controller.monitoring_controller import MonitoringController


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_controller(existing_samples=None, existing_orders=None):
    """Return (controller, order_repo_mock, sample_repo_mock)."""
    order_repo = MagicMock()
    sample_repo = MagicMock()
    order_repo.load.return_value = list(existing_orders or [])
    sample_repo.load.return_value = list(existing_samples or [])
    ctrl = MonitoringController(order_repo, sample_repo)
    return ctrl, order_repo, sample_repo


def _make_order(order_id="aaaaaaaa", sample_id="S001", customer_name="홍길동",
                quantity=10, status=OrderStatus.RESERVED):
    return Order(order_id=order_id, sample_id=sample_id,
                 customer_name=customer_name, quantity=quantity, status=status)


def _make_sample(sample_id="S001", name="Silicon Wafer",
                 avg_production_time=2.5, yield_rate=0.85, stock=50):
    return Sample(sample_id=sample_id, name=name,
                  avg_production_time=avg_production_time,
                  yield_rate=yield_rate, stock=stock)


# ---------------------------------------------------------------------------
# order_summary — all statuses present
# ---------------------------------------------------------------------------

def test_order_summary_all_statuses():
    """order_summary returns 4-key dict with correct counts for each status."""
    orders = [
        _make_order("o1", status=OrderStatus.RESERVED),
        _make_order("o2", status=OrderStatus.RESERVED),
        _make_order("o3", status=OrderStatus.PRODUCING),
        _make_order("o4", status=OrderStatus.CONFIRMED),
        _make_order("o5", status=OrderStatus.CONFIRMED),
        _make_order("o6", status=OrderStatus.CONFIRMED),
        _make_order("o7", status=OrderStatus.RELEASE),
    ]
    ctrl, _, _ = _make_controller(existing_orders=orders)
    result = ctrl.order_summary()

    assert set(result.keys()) == {"RESERVED", "PRODUCING", "CONFIRMED", "RELEASE"}
    assert result["RESERVED"] == 2
    assert result["PRODUCING"] == 1
    assert result["CONFIRMED"] == 3
    assert result["RELEASE"] == 1


# ---------------------------------------------------------------------------
# order_summary — REJECTED excluded
# ---------------------------------------------------------------------------

def test_order_summary_excludes_rejected():
    """order_summary does not include REJECTED key, even if such orders exist."""
    orders = [
        _make_order("o1", status=OrderStatus.RESERVED),
        _make_order("o2", status=OrderStatus.REJECTED),
    ]
    ctrl, _, _ = _make_controller(existing_orders=orders)
    result = ctrl.order_summary()

    assert "REJECTED" not in result
    assert result["RESERVED"] == 1


# ---------------------------------------------------------------------------
# order_summary — empty order list
# ---------------------------------------------------------------------------

def test_order_summary_empty_orders():
    """order_summary returns all 4 keys with value 0 when no orders exist."""
    ctrl, _, _ = _make_controller(existing_orders=[])
    result = ctrl.order_summary()

    assert set(result.keys()) == {"RESERVED", "PRODUCING", "CONFIRMED", "RELEASE"}
    assert result["RESERVED"] == 0
    assert result["PRODUCING"] == 0
    assert result["CONFIRMED"] == 0
    assert result["RELEASE"] == 0


# ---------------------------------------------------------------------------
# stock_summary — surplus (여유)
# ---------------------------------------------------------------------------

def test_stock_summary_surplus():
    """stock_summary returns '여유' when stock >= active_quantity."""
    sample = _make_sample(sample_id="S001", stock=20)
    # active orders: RESERVED qty=5, PRODUCING qty=5 → active_quantity=10
    orders = [
        _make_order("o1", sample_id="S001", quantity=5, status=OrderStatus.RESERVED),
        _make_order("o2", sample_id="S001", quantity=5, status=OrderStatus.PRODUCING),
    ]
    ctrl, _, _ = _make_controller(existing_samples=[sample], existing_orders=orders)
    result = ctrl.stock_summary()

    assert len(result) == 1
    row = result[0]
    assert row["sample_id"] == "S001"
    assert row["stock"] == 20
    assert row["active_quantity"] == 10
    assert row["stock_status"] == "여유"


# ---------------------------------------------------------------------------
# stock_summary — shortage (부족)
# ---------------------------------------------------------------------------

def test_stock_summary_shortage():
    """stock_summary returns '부족' when 0 < stock < active_quantity."""
    sample = _make_sample(sample_id="S001", stock=5)
    # active_quantity = 15 → stock(5) < active_quantity(15)
    orders = [
        _make_order("o1", sample_id="S001", quantity=10, status=OrderStatus.RESERVED),
        _make_order("o2", sample_id="S001", quantity=5, status=OrderStatus.PRODUCING),
    ]
    ctrl, _, _ = _make_controller(existing_samples=[sample], existing_orders=orders)
    result = ctrl.stock_summary()

    assert len(result) == 1
    row = result[0]
    assert row["stock"] == 5
    assert row["active_quantity"] == 15
    assert row["stock_status"] == "부족"


# ---------------------------------------------------------------------------
# stock_summary — depleted (고갈)
# ---------------------------------------------------------------------------

def test_stock_summary_depleted():
    """stock_summary returns '고갈' when stock == 0."""
    sample = _make_sample(sample_id="S001", stock=0)
    orders = [
        _make_order("o1", sample_id="S001", quantity=5, status=OrderStatus.RESERVED),
    ]
    ctrl, _, _ = _make_controller(existing_samples=[sample], existing_orders=orders)
    result = ctrl.stock_summary()

    assert len(result) == 1
    row = result[0]
    assert row["stock"] == 0
    assert row["stock_status"] == "고갈"


# ---------------------------------------------------------------------------
# stock_summary — depleted takes precedence over active_quantity == 0
# ---------------------------------------------------------------------------

def test_stock_summary_depleted_even_with_no_active_orders():
    """stock_summary returns '고갈' when stock == 0 even if active_quantity == 0."""
    sample = _make_sample(sample_id="S001", stock=0)
    ctrl, _, _ = _make_controller(existing_samples=[sample], existing_orders=[])
    result = ctrl.stock_summary()

    assert result[0]["stock_status"] == "고갈"
    assert result[0]["active_quantity"] == 0


# ---------------------------------------------------------------------------
# stock_summary — no active orders, stock > 0 (여유)
# ---------------------------------------------------------------------------

def test_stock_summary_no_active_orders():
    """stock_summary returns '여유' when active_quantity == 0 and stock > 0."""
    sample = _make_sample(sample_id="S001", stock=30)
    # Only CONFIRMED and RELEASE orders — not counted in active_quantity
    orders = [
        _make_order("o1", sample_id="S001", quantity=10, status=OrderStatus.CONFIRMED),
        _make_order("o2", sample_id="S001", quantity=5, status=OrderStatus.RELEASE),
    ]
    ctrl, _, _ = _make_controller(existing_samples=[sample], existing_orders=orders)
    result = ctrl.stock_summary()

    assert len(result) == 1
    row = result[0]
    assert row["active_quantity"] == 0
    assert row["stock"] == 30
    assert row["stock_status"] == "여유"


# ---------------------------------------------------------------------------
# stock_summary — empty samples list
# ---------------------------------------------------------------------------

def test_stock_summary_empty_samples():
    """stock_summary returns empty list when no samples are registered."""
    ctrl, _, _ = _make_controller(existing_samples=[], existing_orders=[])
    result = ctrl.stock_summary()

    assert result == []
