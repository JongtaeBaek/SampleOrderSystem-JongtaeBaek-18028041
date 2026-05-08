"""Tests for controller/order_controller.py — 100% coverage (Phase 3: reserve)."""
import pytest
from unittest.mock import MagicMock

from model.order import Order, OrderStatus
from model.sample import Sample
from controller.order_controller import OrderController


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_controller(existing_samples=None, existing_orders=None):
    """Return (controller, order_repo_mock, sample_repo_mock)."""
    order_repo = MagicMock()
    sample_repo = MagicMock()
    order_repo.load.return_value = list(existing_orders or [])
    sample_repo.load.return_value = list(existing_samples or [])
    ctrl = OrderController(order_repo, sample_repo)
    return ctrl, order_repo, sample_repo


def _saved_new_order(order_repo):
    """Return the last order from the list passed to order_repo.save."""
    return order_repo.save.call_args[0][0][-1]


@pytest.fixture
def sample_s001():
    return Sample("S001", "Silicon Wafer", 2.5, 0.85, 100)


# ---------------------------------------------------------------------------
# reserve — success path
# ---------------------------------------------------------------------------

def test_reserve_success(sample_s001):
    """reserve returns True when the sample exists and saves the new order."""
    ctrl, order_repo, _ = _make_controller(existing_samples=[sample_s001])
    assert ctrl.reserve("S001", "홍길동", 10) is True


def test_reserve_success_calls_save(sample_s001):
    """reserve calls order_repo.save exactly once on success."""
    ctrl, order_repo, _ = _make_controller(existing_samples=[sample_s001])
    ctrl.reserve("S001", "홍길동", 10)
    order_repo.save.assert_called_once()


def test_reserve_success_order_status_is_reserved(sample_s001):
    """reserve creates the new Order with status RESERVED."""
    ctrl, order_repo, _ = _make_controller(existing_samples=[sample_s001])
    ctrl.reserve("S001", "홍길동", 10)
    assert _saved_new_order(order_repo).status == OrderStatus.RESERVED


def test_reserve_success_order_fields(sample_s001):
    """reserve stores the correct sample_id, customer_name, and quantity."""
    ctrl, order_repo, _ = _make_controller(existing_samples=[sample_s001])
    ctrl.reserve("S001", "홍길동", 10)
    new_order = _saved_new_order(order_repo)
    assert new_order.sample_id == "S001"
    assert new_order.customer_name == "홍길동"
    assert new_order.quantity == 10


def test_reserve_appends_to_existing_orders(sample_s001):
    """reserve preserves existing orders and appends the new one."""
    existing_order = Order("prev0001", "S001", "기존고객", 5, OrderStatus.RESERVED)
    ctrl, order_repo, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[existing_order],
    )
    ctrl.reserve("S001", "새고객", 3)
    saved_orders = order_repo.save.call_args[0][0]
    assert len(saved_orders) == 2
    assert saved_orders[0].order_id == "prev0001"


# ---------------------------------------------------------------------------
# reserve — order_id format
# ---------------------------------------------------------------------------

def test_reserve_order_id_is_8_chars(sample_s001):
    """reserve generates an order_id that is exactly 8 characters long."""
    ctrl, order_repo, _ = _make_controller(existing_samples=[sample_s001])
    ctrl.reserve("S001", "홍길동", 10)
    assert len(_saved_new_order(order_repo).order_id) == 8


def test_reserve_order_id_is_string(sample_s001):
    """reserve generates an order_id of type str."""
    ctrl, order_repo, _ = _make_controller(existing_samples=[sample_s001])
    ctrl.reserve("S001", "홍길동", 10)
    assert isinstance(_saved_new_order(order_repo).order_id, str)


# ---------------------------------------------------------------------------
# reserve — sample not found path
# ---------------------------------------------------------------------------

def test_reserve_sample_not_found_returns_false():
    """reserve returns False when the sample_id does not exist."""
    ctrl, order_repo, _ = _make_controller(existing_samples=[])
    assert ctrl.reserve("NONEXIST", "홍길동", 10) is False


def test_reserve_sample_not_found_does_not_call_save():
    """reserve does not call order_repo.save when sample_id is not found."""
    ctrl, order_repo, _ = _make_controller(existing_samples=[])
    ctrl.reserve("NONEXIST", "홍길동", 10)
    order_repo.save.assert_not_called()


def test_reserve_sample_not_found_prints_error(capsys):
    """reserve prints an error message containing the missing sample_id."""
    ctrl, _, _ = _make_controller(existing_samples=[])
    ctrl.reserve("NONEXIST", "홍길동", 10)
    captured = capsys.readouterr()
    assert "오류" in captured.out
    assert "NONEXIST" in captured.out


def test_reserve_sample_not_found_among_others_returns_false(sample_s001):
    """reserve returns False when the requested sample_id is not in the list."""
    ctrl, order_repo, _ = _make_controller(existing_samples=[sample_s001])
    assert ctrl.reserve("S999", "홍길동", 5) is False
    order_repo.save.assert_not_called()
