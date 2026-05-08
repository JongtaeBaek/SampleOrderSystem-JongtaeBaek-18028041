"""Tests for controller/release_controller.py — 100% coverage (Phase 7)."""
from unittest.mock import MagicMock

from model.order import Order, OrderStatus
from model.sample import Sample
from controller.release_controller import ReleaseController


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_controller(existing_samples=None, existing_orders=None):
    """Return (controller, order_repo_mock, sample_repo_mock)."""
    order_repo = MagicMock()
    sample_repo = MagicMock()
    order_repo.load.return_value = list(existing_orders or [])
    sample_repo.load.return_value = list(existing_samples or [])
    ctrl = ReleaseController(order_repo, sample_repo)
    return ctrl, order_repo, sample_repo


def _make_order(order_id="abcd1234", sample_id="S001", customer_name="홍길동",
                quantity=10, status=OrderStatus.CONFIRMED):
    return Order(order_id, sample_id, customer_name, quantity, status)


def _make_sample(sample_id="S001", stock=100):
    return Sample(sample_id, "Silicon Wafer", 2.5, 0.85, stock)


# ---------------------------------------------------------------------------
# list_confirmed
# ---------------------------------------------------------------------------

def test_list_confirmed():
    """list_confirmed returns only CONFIRMED orders."""
    orders = [
        _make_order("aaaa0001", status=OrderStatus.CONFIRMED),
        _make_order("aaaa0002", status=OrderStatus.RESERVED),
        _make_order("aaaa0003", status=OrderStatus.PRODUCING),
        _make_order("aaaa0004", status=OrderStatus.RELEASE),
        _make_order("aaaa0005", status=OrderStatus.REJECTED),
    ]
    ctrl, _, _ = _make_controller(existing_orders=orders)
    result = ctrl.list_confirmed()
    assert len(result) == 1
    assert result[0].order_id == "aaaa0001"
    assert result[0].status == OrderStatus.CONFIRMED


def test_list_confirmed_empty():
    """list_confirmed returns [] when there are no CONFIRMED orders."""
    orders = [
        _make_order("aaaa0001", status=OrderStatus.RESERVED),
        _make_order("aaaa0002", status=OrderStatus.PRODUCING),
    ]
    ctrl, _, _ = _make_controller(existing_orders=orders)
    result = ctrl.list_confirmed()
    assert result == []


# ---------------------------------------------------------------------------
# release — success path
# ---------------------------------------------------------------------------

def test_release_success():
    """release returns True and saves both samples and orders on success."""
    order = _make_order("abcd1234", status=OrderStatus.CONFIRMED, quantity=10)
    sample = _make_sample("S001", stock=50)
    ctrl, order_repo, sample_repo = _make_controller(
        existing_samples=[sample], existing_orders=[order]
    )
    result = ctrl.release("abcd1234")
    assert result is True
    sample_repo.save.assert_called_once()
    order_repo.save.assert_called_once()


def test_release_stock_decreases_by_quantity():
    """release subtracts order.quantity from sample.stock exactly."""
    order = _make_order("abcd1234", sample_id="S001", status=OrderStatus.CONFIRMED, quantity=15)
    sample = _make_sample("S001", stock=50)
    ctrl, _, _ = _make_controller(existing_samples=[sample], existing_orders=[order])
    ctrl.release("abcd1234")
    assert sample.stock == 35  # 50 - 15


def test_release_changes_status_to_release():
    """release transitions order status from CONFIRMED to RELEASE."""
    order = _make_order("abcd1234", status=OrderStatus.CONFIRMED)
    sample = _make_sample("S001", stock=100)
    ctrl, _, _ = _make_controller(existing_samples=[sample], existing_orders=[order])
    ctrl.release("abcd1234")
    assert order.status == OrderStatus.RELEASE


def test_release_saves_correct_orders_list():
    """release passes the full orders list (with updated status) to order_repo.save."""
    order = _make_order("abcd1234", status=OrderStatus.CONFIRMED)
    sample = _make_sample("S001", stock=100)
    ctrl, order_repo, _ = _make_controller(existing_samples=[sample], existing_orders=[order])
    ctrl.release("abcd1234")
    saved_orders = order_repo.save.call_args[0][0]
    assert any(o.status == OrderStatus.RELEASE for o in saved_orders)


def test_release_saves_correct_samples_list():
    """release passes the full samples list (with updated stock) to sample_repo.save."""
    order = _make_order("abcd1234", sample_id="S001", status=OrderStatus.CONFIRMED, quantity=10)
    sample = _make_sample("S001", stock=30)
    ctrl, _, sample_repo = _make_controller(existing_samples=[sample], existing_orders=[order])
    ctrl.release("abcd1234")
    saved_samples = sample_repo.save.call_args[0][0]
    assert any(s.stock == 20 for s in saved_samples)


# ---------------------------------------------------------------------------
# release — error paths
# ---------------------------------------------------------------------------

def test_release_not_found():
    """release returns False and does not call save when order_id does not exist."""
    ctrl, order_repo, sample_repo = _make_controller(existing_orders=[])
    result = ctrl.release("nonexistent")
    assert result is False
    order_repo.save.assert_not_called()
    sample_repo.save.assert_not_called()


def test_release_not_found_prints_error(capsys):
    """release prints an error message when order_id is not found."""
    ctrl, _, _ = _make_controller(existing_orders=[])
    ctrl.release("nonexistent")
    captured = capsys.readouterr()
    assert "오류" in captured.out
    assert "nonexistent" in captured.out


def test_release_wrong_status_reserved():
    """release returns False when order status is RESERVED."""
    order = _make_order("abcd1234", status=OrderStatus.RESERVED)
    ctrl, order_repo, sample_repo = _make_controller(existing_orders=[order])
    result = ctrl.release("abcd1234")
    assert result is False
    order_repo.save.assert_not_called()
    sample_repo.save.assert_not_called()


def test_release_wrong_status_reserved_prints_error(capsys):
    """release prints an error message when order status is RESERVED."""
    order = _make_order("abcd1234", status=OrderStatus.RESERVED)
    ctrl, _, _ = _make_controller(existing_orders=[order])
    ctrl.release("abcd1234")
    captured = capsys.readouterr()
    assert "오류" in captured.out
    assert "abcd1234" in captured.out


def test_release_wrong_status_producing():
    """release returns False when order status is PRODUCING."""
    order = _make_order("abcd1234", status=OrderStatus.PRODUCING)
    ctrl, order_repo, sample_repo = _make_controller(existing_orders=[order])
    result = ctrl.release("abcd1234")
    assert result is False
    order_repo.save.assert_not_called()
    sample_repo.save.assert_not_called()


def test_release_wrong_status_producing_prints_error(capsys):
    """release prints an error message when order status is PRODUCING."""
    order = _make_order("abcd1234", status=OrderStatus.PRODUCING)
    ctrl, _, _ = _make_controller(existing_orders=[order])
    ctrl.release("abcd1234")
    captured = capsys.readouterr()
    assert "오류" in captured.out
    assert "abcd1234" in captured.out
