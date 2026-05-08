"""Tests for controller/order_controller.py — 100% coverage (Phase 3: reserve, Phase 4: list_reserved/approve/reject)."""
import pytest
from unittest.mock import MagicMock

from model.order import Order, OrderStatus
from model.sample import Sample
from model.production import ProductionQueue
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


# ---------------------------------------------------------------------------
# Phase 4: list_reserved
# ---------------------------------------------------------------------------

def test_list_reserved(sample_s001):
    """list_reserved returns only RESERVED orders, filtering out other statuses."""
    orders = [
        Order("aaaaaaaa", "S001", "고객A", 10, OrderStatus.RESERVED),
        Order("bbbbbbbb", "S001", "고객B", 5, OrderStatus.CONFIRMED),
        Order("cccccccc", "S001", "고객C", 3, OrderStatus.PRODUCING),
        Order("dddddddd", "S001", "고객D", 7, OrderStatus.RESERVED),
    ]
    ctrl, _, _ = _make_controller(existing_samples=[sample_s001], existing_orders=orders)
    result = ctrl.list_reserved()
    assert len(result) == 2
    assert all(o.status == OrderStatus.RESERVED for o in result)
    order_ids = [o.order_id for o in result]
    assert "aaaaaaaa" in order_ids
    assert "dddddddd" in order_ids


# ---------------------------------------------------------------------------
# Phase 4: approve — sufficient stock
# ---------------------------------------------------------------------------

def test_approve_sufficient_stock_returns_true(sample_s001):
    """approve returns True when stock is sufficient."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.RESERVED)
    ctrl, _, sample_repo = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    assert ctrl.approve("aaaaaaaa", pq) is True


def test_approve_sufficient_stock_decrements_stock(sample_s001):
    """approve deducts quantity from sample.stock when stock >= quantity."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.RESERVED)
    ctrl, _, sample_repo = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    # sample_s001.stock was 100, quantity=10 → should be 90
    saved_samples = sample_repo.save.call_args[0][0]
    saved_sample = next(s for s in saved_samples if s.sample_id == "S001")
    assert saved_sample.stock == 90


def test_approve_sufficient_stock_status_confirmed(sample_s001):
    """approve sets order status to CONFIRMED when stock is sufficient."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.RESERVED)
    ctrl, order_repo, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    saved_orders = order_repo.save.call_args[0][0]
    saved_order = next(o for o in saved_orders if o.order_id == "aaaaaaaa")
    assert saved_order.status == OrderStatus.CONFIRMED


def test_approve_sufficient_stock_saves_samples_and_orders(sample_s001):
    """approve calls both sample_repo.save and order_repo.save when stock is sufficient."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.RESERVED)
    ctrl, order_repo, sample_repo = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    sample_repo.save.assert_called_once()
    order_repo.save.assert_called_once()


def test_approve_sufficient_stock_queue_empty(sample_s001):
    """approve does not enqueue a job when stock is sufficient."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.RESERVED)
    ctrl, _, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    assert pq.is_empty()


# ---------------------------------------------------------------------------
# Phase 4: approve — insufficient stock
# ---------------------------------------------------------------------------

def test_approve_insufficient_stock_returns_true():
    """approve returns True when stock is insufficient."""
    sample = Sample("S001", "Silicon Wafer", 2.5, 0.85, 5)
    order = Order("aaaaaaaa", "S001", "홍길동", 20, OrderStatus.RESERVED)
    ctrl, _, _ = _make_controller(
        existing_samples=[sample],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    assert ctrl.approve("aaaaaaaa", pq) is True


def test_approve_insufficient_stock_status_producing():
    """approve sets order status to PRODUCING when stock is insufficient."""
    sample = Sample("S001", "Silicon Wafer", 2.5, 0.85, 5)
    order = Order("aaaaaaaa", "S001", "홍길동", 20, OrderStatus.RESERVED)
    ctrl, order_repo, _ = _make_controller(
        existing_samples=[sample],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    saved_orders = order_repo.save.call_args[0][0]
    saved_order = next(o for o in saved_orders if o.order_id == "aaaaaaaa")
    assert saved_order.status == OrderStatus.PRODUCING


def test_approve_insufficient_stock_enqueues_job():
    """approve enqueues a ProductionJob when stock is insufficient."""
    sample = Sample("S001", "Silicon Wafer", 2.5, 0.85, 5)
    order = Order("aaaaaaaa", "S001", "홍길동", 20, OrderStatus.RESERVED)
    ctrl, _, _ = _make_controller(
        existing_samples=[sample],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    assert not pq.is_empty()
    job = pq.peek()
    assert job.order_id == "aaaaaaaa"
    assert job.sample_id == "S001"
    # shortage = quantity(20) - stock(5) = 15
    assert job.required_quantity == 15


def test_approve_insufficient_stock_does_not_save_samples():
    """approve does NOT call sample_repo.save when stock is insufficient."""
    sample = Sample("S001", "Silicon Wafer", 2.5, 0.85, 5)
    order = Order("aaaaaaaa", "S001", "홍길동", 20, OrderStatus.RESERVED)
    ctrl, _, sample_repo = _make_controller(
        existing_samples=[sample],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    sample_repo.save.assert_not_called()


def test_approve_insufficient_stock_saves_orders():
    """approve calls order_repo.save exactly once when stock is insufficient."""
    sample = Sample("S001", "Silicon Wafer", 2.5, 0.85, 5)
    order = Order("aaaaaaaa", "S001", "홍길동", 20, OrderStatus.RESERVED)
    ctrl, order_repo, _ = _make_controller(
        existing_samples=[sample],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    order_repo.save.assert_called_once()


def test_approve_insufficient_stock_does_not_decrement_stock():
    """approve does not change sample.stock when stock is insufficient."""
    sample = Sample("S001", "Silicon Wafer", 2.5, 0.85, 5)
    order = Order("aaaaaaaa", "S001", "홍길동", 20, OrderStatus.RESERVED)
    ctrl, _, _ = _make_controller(
        existing_samples=[sample],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    # stock should remain 5 (not changed)
    assert sample.stock == 5


# ---------------------------------------------------------------------------
# Phase 4: approve — not found / wrong status
# ---------------------------------------------------------------------------

def test_approve_not_found_returns_false():
    """approve returns False when the order_id does not exist."""
    ctrl, order_repo, _ = _make_controller(existing_orders=[])
    pq = ProductionQueue()
    assert ctrl.approve("nonexist", pq) is False


def test_approve_not_found_does_not_call_save():
    """approve does not call save when the order_id does not exist."""
    ctrl, order_repo, sample_repo = _make_controller(existing_orders=[])
    pq = ProductionQueue()
    ctrl.approve("nonexist", pq)
    order_repo.save.assert_not_called()
    sample_repo.save.assert_not_called()


def test_approve_not_found_prints_error(capsys):
    """approve prints an error message when the order_id does not exist."""
    ctrl, _, _ = _make_controller(existing_orders=[])
    pq = ProductionQueue()
    ctrl.approve("nonexist", pq)
    captured = capsys.readouterr()
    assert "오류" in captured.out
    assert "nonexist" in captured.out


def test_approve_wrong_status_returns_false(sample_s001):
    """approve returns False when the order is already CONFIRMED (not RESERVED)."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.CONFIRMED)
    ctrl, order_repo, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    assert ctrl.approve("aaaaaaaa", pq) is False


def test_approve_wrong_status_does_not_call_save(sample_s001):
    """approve does not call save when order status is not RESERVED."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.CONFIRMED)
    ctrl, order_repo, sample_repo = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    ctrl.approve("aaaaaaaa", pq)
    order_repo.save.assert_not_called()
    sample_repo.save.assert_not_called()


# ---------------------------------------------------------------------------
# Phase 4: reject — success
# ---------------------------------------------------------------------------

def test_reject_success_returns_true(sample_s001):
    """reject returns True when the order exists and is RESERVED."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.RESERVED)
    ctrl, _, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    assert ctrl.reject("aaaaaaaa") is True


def test_reject_success_status_rejected(sample_s001):
    """reject sets order status to REJECTED."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.RESERVED)
    ctrl, order_repo, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    ctrl.reject("aaaaaaaa")
    saved_orders = order_repo.save.call_args[0][0]
    saved_order = next(o for o in saved_orders if o.order_id == "aaaaaaaa")
    assert saved_order.status == OrderStatus.REJECTED


def test_reject_success_saves_orders(sample_s001):
    """reject calls order_repo.save exactly once on success."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.RESERVED)
    ctrl, order_repo, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    ctrl.reject("aaaaaaaa")
    order_repo.save.assert_called_once()


# ---------------------------------------------------------------------------
# Phase 4: reject — not found / wrong status
# ---------------------------------------------------------------------------

def test_reject_not_found_returns_false():
    """reject returns False when the order_id does not exist."""
    ctrl, _, _ = _make_controller(existing_orders=[])
    assert ctrl.reject("nonexist") is False


def test_reject_not_found_does_not_call_save():
    """reject does not call save when the order_id does not exist."""
    ctrl, order_repo, _ = _make_controller(existing_orders=[])
    ctrl.reject("nonexist")
    order_repo.save.assert_not_called()


def test_reject_not_found_prints_error(capsys):
    """reject prints an error message when the order_id does not exist."""
    ctrl, _, _ = _make_controller(existing_orders=[])
    ctrl.reject("nonexist")
    captured = capsys.readouterr()
    assert "오류" in captured.out
    assert "nonexist" in captured.out


def test_reject_wrong_status_returns_false(sample_s001):
    """reject returns False when the order is in PRODUCING status (not RESERVED)."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.PRODUCING)
    ctrl, _, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    assert ctrl.reject("aaaaaaaa") is False


def test_reject_wrong_status_does_not_call_save(sample_s001):
    """reject does not call save when order status is not RESERVED."""
    order = Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.PRODUCING)
    ctrl, order_repo, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order],
    )
    ctrl.reject("aaaaaaaa")
    order_repo.save.assert_not_called()
