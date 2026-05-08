"""Tests for controller/production_controller.py — 100% coverage (Phase 5)."""
import pytest
from unittest.mock import MagicMock

from model.order import Order, OrderStatus
from model.sample import Sample
from model.production import ProductionJob, ProductionQueue
from controller.production_controller import ProductionController


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_controller(existing_samples=None, existing_orders=None):
    """Return (controller, order_repo_mock, sample_repo_mock)."""
    order_repo = MagicMock()
    sample_repo = MagicMock()
    order_repo.load.return_value = list(existing_orders or [])
    sample_repo.load.return_value = list(existing_samples or [])
    ctrl = ProductionController(order_repo, sample_repo)
    return ctrl, order_repo, sample_repo


def _make_job(order_id="aaaaaaaa", sample_id="S001", required_quantity=10,
              actual_production=12, total_time=30.0):
    return ProductionJob(
        order_id=order_id,
        sample_id=sample_id,
        required_quantity=required_quantity,
        actual_production=actual_production,
        total_time=total_time,
    )


@pytest.fixture
def sample_s001():
    return Sample("S001", "Silicon Wafer", 2.5, 0.85, 50)


@pytest.fixture
def order_producing():
    return Order("aaaaaaaa", "S001", "홍길동", 10, OrderStatus.PRODUCING)


# ---------------------------------------------------------------------------
# show_current — empty queue
# ---------------------------------------------------------------------------

def test_show_current_empty_queue():
    """show_current returns None when the queue is empty."""
    ctrl, _, _ = _make_controller()
    pq = ProductionQueue()
    result = ctrl.show_current(pq)
    assert result is None


# ---------------------------------------------------------------------------
# show_current — queue with job
# ---------------------------------------------------------------------------

def test_show_current_with_job():
    """show_current returns the front job without dequeuing it."""
    ctrl, _, _ = _make_controller()
    pq = ProductionQueue()
    job = _make_job()
    pq.enqueue(job)
    result = ctrl.show_current(pq)
    assert result is job


def test_show_current_does_not_dequeue():
    """show_current (peek) does not remove the job from the queue."""
    ctrl, _, _ = _make_controller()
    pq = ProductionQueue()
    job = _make_job()
    pq.enqueue(job)
    ctrl.show_current(pq)
    assert not pq.is_empty()
    assert pq.peek() is job


# ---------------------------------------------------------------------------
# complete — empty queue
# ---------------------------------------------------------------------------

def test_complete_empty_queue_returns_false():
    """complete returns False when the queue is empty."""
    ctrl, _, _ = _make_controller()
    pq = ProductionQueue()
    result = ctrl.complete(pq)
    assert result is False


def test_complete_empty_queue_prints_error(capsys):
    """complete prints an error message when the queue is empty."""
    ctrl, _, _ = _make_controller()
    pq = ProductionQueue()
    ctrl.complete(pq)
    assert "생산 중인 작업이 없습니다." in capsys.readouterr().out


def test_complete_empty_queue_does_not_call_save():
    """complete does not call save on either repo when the queue is empty."""
    ctrl, order_repo, sample_repo = _make_controller()
    pq = ProductionQueue()
    ctrl.complete(pq)
    order_repo.save.assert_not_called()
    sample_repo.save.assert_not_called()


# ---------------------------------------------------------------------------
# complete — success path
# ---------------------------------------------------------------------------

def test_complete_success_returns_true(sample_s001, order_producing):
    """complete returns True when the queue has a job."""
    ctrl, _, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order_producing],
    )
    pq = ProductionQueue()
    job = _make_job(order_id="aaaaaaaa", sample_id="S001", actual_production=12)
    pq.enqueue(job)
    result = ctrl.complete(pq)
    assert result is True


def test_complete_success_dequeues_job(sample_s001, order_producing):
    """complete removes the job from the queue."""
    ctrl, _, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order_producing],
    )
    pq = ProductionQueue()
    pq.enqueue(_make_job(order_id="aaaaaaaa", sample_id="S001", actual_production=12))
    ctrl.complete(pq)
    assert pq.is_empty()


def test_complete_success_order_status_confirmed(sample_s001, order_producing):
    """complete sets the order status to CONFIRMED."""
    ctrl, order_repo, _ = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order_producing],
    )
    pq = ProductionQueue()
    pq.enqueue(_make_job(order_id="aaaaaaaa", sample_id="S001", actual_production=12))
    ctrl.complete(pq)
    saved_orders = order_repo.save.call_args[0][0]
    saved_order = next(o for o in saved_orders if o.order_id == "aaaaaaaa")
    assert saved_order.status == OrderStatus.CONFIRMED


def test_complete_success_saves_samples_and_orders(sample_s001, order_producing):
    """complete calls both sample_repo.save and order_repo.save exactly once."""
    ctrl, order_repo, sample_repo = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order_producing],
    )
    pq = ProductionQueue()
    pq.enqueue(_make_job(order_id="aaaaaaaa", sample_id="S001", actual_production=12))
    ctrl.complete(pq)
    sample_repo.save.assert_called_once()
    order_repo.save.assert_called_once()


# ---------------------------------------------------------------------------
# complete — stock increment verification
# ---------------------------------------------------------------------------

def test_complete_stock_increases_by_actual_production(sample_s001, order_producing):
    """complete increments sample.stock by exactly job.actual_production."""
    initial_stock = sample_s001.stock  # 50
    actual_production = 15
    ctrl, _, sample_repo = _make_controller(
        existing_samples=[sample_s001],
        existing_orders=[order_producing],
    )
    pq = ProductionQueue()
    pq.enqueue(_make_job(order_id="aaaaaaaa", sample_id="S001", actual_production=actual_production))
    ctrl.complete(pq)
    saved_samples = sample_repo.save.call_args[0][0]
    saved_sample = next(s for s in saved_samples if s.sample_id == "S001")
    assert saved_sample.stock == initial_stock + actual_production


def test_complete_stock_increases_exact_value():
    """complete: stock goes from 20 to 20+8=28 when actual_production=8."""
    sample = Sample("S002", "GaAs Wafer", 3.0, 0.90, 20)
    order = Order("bbbbbbbb", "S002", "이순신", 5, OrderStatus.PRODUCING)
    ctrl, _, sample_repo = _make_controller(
        existing_samples=[sample],
        existing_orders=[order],
    )
    pq = ProductionQueue()
    pq.enqueue(_make_job(order_id="bbbbbbbb", sample_id="S002", actual_production=8))
    ctrl.complete(pq)
    saved_samples = sample_repo.save.call_args[0][0]
    saved_sample = next(s for s in saved_samples if s.sample_id == "S002")
    assert saved_sample.stock == 28


# ---------------------------------------------------------------------------
# list_queue — empty
# ---------------------------------------------------------------------------

def test_list_queue_empty():
    """list_queue returns an empty list when the queue is empty."""
    ctrl, _, _ = _make_controller()
    pq = ProductionQueue()
    result = ctrl.list_queue(pq)
    assert result == []


# ---------------------------------------------------------------------------
# list_queue — with jobs
# ---------------------------------------------------------------------------

def test_list_queue_with_jobs():
    """list_queue returns all jobs in FIFO order."""
    ctrl, _, _ = _make_controller()
    pq = ProductionQueue()
    job1 = _make_job(order_id="aaaaaaaa")
    job2 = _make_job(order_id="bbbbbbbb")
    pq.enqueue(job1)
    pq.enqueue(job2)
    result = ctrl.list_queue(pq)
    assert len(result) == 2
    assert result[0] is job1
    assert result[1] is job2


def test_list_queue_does_not_mutate_queue():
    """list_queue does not remove jobs from the queue."""
    ctrl, _, _ = _make_controller()
    pq = ProductionQueue()
    pq.enqueue(_make_job(order_id="aaaaaaaa"))
    ctrl.list_queue(pq)
    assert not pq.is_empty()
