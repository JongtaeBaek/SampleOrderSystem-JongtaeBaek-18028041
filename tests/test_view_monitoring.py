"""Tests for view/monitoring_view.py — 100% coverage (Phase 5: production현황 부분)."""
import pytest

from model.production import ProductionJob
from view.monitoring_view import MonitoringView


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

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
def view():
    return MonitoringView()


# ---------------------------------------------------------------------------
# show_production_current — None (empty queue)
# ---------------------------------------------------------------------------

def test_show_production_current_none(view, capsys):
    """show_production_current prints '현재 생산 중인 작업이 없습니다.' when job is None."""
    view.show_production_current(None)
    assert "현재 생산 중인 작업이 없습니다." in capsys.readouterr().out


def test_show_production_current_none_no_job_info(view, capsys):
    """show_production_current does not print job fields when job is None."""
    view.show_production_current(None)
    out = capsys.readouterr().out
    assert "주문 ID" not in out
    assert "시료 ID" not in out


# ---------------------------------------------------------------------------
# show_production_current — with job
# ---------------------------------------------------------------------------

def test_show_production_current_with_job_order_id(view, capsys):
    """show_production_current prints order_id when job is present."""
    job = _make_job(order_id="aaaaaaaa")
    view.show_production_current(job)
    assert "aaaaaaaa" in capsys.readouterr().out


def test_show_production_current_with_job_sample_id(view, capsys):
    """show_production_current prints sample_id when job is present."""
    job = _make_job(sample_id="S001")
    view.show_production_current(job)
    assert "S001" in capsys.readouterr().out


def test_show_production_current_with_job_required_quantity(view, capsys):
    """show_production_current prints required_quantity when job is present."""
    job = _make_job(required_quantity=10)
    view.show_production_current(job)
    assert "10" in capsys.readouterr().out


def test_show_production_current_with_job_actual_production(view, capsys):
    """show_production_current prints actual_production when job is present."""
    job = _make_job(actual_production=12)
    view.show_production_current(job)
    assert "12" in capsys.readouterr().out


def test_show_production_current_with_job_total_time(view, capsys):
    """show_production_current prints total_time (formatted) when job is present."""
    job = _make_job(total_time=30.0)
    view.show_production_current(job)
    assert "30.0" in capsys.readouterr().out


def test_show_production_current_with_job_no_empty_message(view, capsys):
    """show_production_current does not print empty message when job is present."""
    job = _make_job()
    view.show_production_current(job)
    assert "현재 생산 중인 작업이 없습니다." not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# show_production_queue — empty list
# ---------------------------------------------------------------------------

def test_show_production_queue_empty(view, capsys):
    """show_production_queue prints '대기 중인 생산 작업이 없습니다.' when list is empty."""
    view.show_production_queue([])
    assert "대기 중인 생산 작업이 없습니다." in capsys.readouterr().out


def test_show_production_queue_empty_no_job_info(view, capsys):
    """show_production_queue does not print job details when list is empty."""
    view.show_production_queue([])
    assert "#1" not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# show_production_queue — with jobs
# ---------------------------------------------------------------------------

def test_show_production_queue_with_one_job(view, capsys):
    """show_production_queue prints '#1' prefix for the first job."""
    job = _make_job(order_id="aaaaaaaa", sample_id="S001", required_quantity=10)
    view.show_production_queue([job])
    out = capsys.readouterr().out
    assert "#1" in out
    assert "aaaaaaaa" in out
    assert "S001" in out
    assert "10" in out


def test_show_production_queue_with_two_jobs(view, capsys):
    """show_production_queue prints '#1' and '#2' for two jobs."""
    job1 = _make_job(order_id="aaaaaaaa", sample_id="S001", required_quantity=10)
    job2 = _make_job(order_id="bbbbbbbb", sample_id="S002", required_quantity=5)
    view.show_production_queue([job1, job2])
    out = capsys.readouterr().out
    assert "#1" in out
    assert "#2" in out
    assert "aaaaaaaa" in out
    assert "bbbbbbbb" in out
    assert "S001" in out
    assert "S002" in out


def test_show_production_queue_with_jobs_no_empty_message(view, capsys):
    """show_production_queue does not print empty message when jobs exist."""
    job = _make_job()
    view.show_production_queue([job])
    assert "대기 중인 생산 작업이 없습니다." not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# show_complete_success
# ---------------------------------------------------------------------------

def test_show_complete_success(view, capsys):
    """show_complete_success prints '생산 완료: 주문 <order_id>' message."""
    job = _make_job(order_id="aaaaaaaa", actual_production=12)
    view.show_complete_success(job)
    assert "생산 완료: 주문 aaaaaaaa" in capsys.readouterr().out


def test_show_complete_success_contains_actual_production(view, capsys):
    """show_complete_success output includes the actual_production count."""
    job = _make_job(order_id="aaaaaaaa", actual_production=15)
    view.show_complete_success(job)
    assert "15" in capsys.readouterr().out


def test_show_complete_success_format(view, capsys):
    """show_complete_success follows the exact format with em dash separator."""
    job = _make_job(order_id="cccccccc", actual_production=7)
    view.show_complete_success(job)
    out = capsys.readouterr().out
    assert "생산 완료: 주문 cccccccc" in out
    assert "7개 생산" in out
