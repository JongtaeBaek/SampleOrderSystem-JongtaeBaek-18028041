"""Tests for view/monitoring_view.py — 100% coverage (Phase 5: 생산현황 / Phase 6: 주문량·재고량 현황)."""
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


# ---------------------------------------------------------------------------
# Phase 6 — show_order_summary
# ---------------------------------------------------------------------------

def test_show_order_summary(view, capsys):
    """show_order_summary prints header and all 4 status counts correctly."""
    summary = {
        "RESERVED": 3,
        "PRODUCING": 1,
        "CONFIRMED": 2,
        "RELEASE": 4,
    }
    view.show_order_summary(summary)
    out = capsys.readouterr().out
    assert "주문량 현황" in out
    assert "RESERVED" in out
    assert "PRODUCING" in out
    assert "CONFIRMED" in out
    assert "RELEASE" in out
    assert "3" in out
    assert "1" in out
    assert "2" in out
    assert "4" in out


# ---------------------------------------------------------------------------
# Phase 6 — show_stock_summary (empty)
# ---------------------------------------------------------------------------

def test_show_stock_summary_empty(view, capsys):
    """show_stock_summary prints '등록된 시료가 없습니다.' when list is empty."""
    view.show_stock_summary([])
    out = capsys.readouterr().out
    assert "등록된 시료가 없습니다." in out


def test_show_stock_summary_empty_no_header(view, capsys):
    """show_stock_summary does not print table header when list is empty."""
    view.show_stock_summary([])
    out = capsys.readouterr().out
    assert "시료ID" not in out


# ---------------------------------------------------------------------------
# Phase 6 — show_stock_summary (with data)
# ---------------------------------------------------------------------------

def test_show_stock_summary_with_data(view, capsys):
    """show_stock_summary prints header, separator, and row data when list has items."""
    summaries = [
        {
            "sample_id": "S001",
            "name": "Silicon Wafer",
            "stock": 20,
            "active_quantity": 10,
            "stock_status": "여유",
        }
    ]
    view.show_stock_summary(summaries)
    out = capsys.readouterr().out
    assert "시료ID" in out
    assert "S001" in out
    assert "Silicon Wafer" in out
    assert "20" in out
    assert "10" in out
    assert "여유" in out


def test_show_stock_summary_with_data_shortage_status(view, capsys):
    """show_stock_summary prints '부족' status string for shortage rows."""
    summaries = [
        {
            "sample_id": "S002",
            "name": "GaAs Wafer",
            "stock": 3,
            "active_quantity": 15,
            "stock_status": "부족",
        }
    ]
    view.show_stock_summary(summaries)
    out = capsys.readouterr().out
    assert "부족" in out
    assert "S002" in out


def test_show_stock_summary_with_data_depleted_status(view, capsys):
    """show_stock_summary prints '고갈' status string for depleted rows."""
    summaries = [
        {
            "sample_id": "S003",
            "name": "InP Wafer",
            "stock": 0,
            "active_quantity": 5,
            "stock_status": "고갈",
        }
    ]
    view.show_stock_summary(summaries)
    out = capsys.readouterr().out
    assert "고갈" in out
    assert "S003" in out


def test_show_stock_summary_with_multiple_rows(view, capsys):
    """show_stock_summary prints all rows when multiple summaries are given."""
    summaries = [
        {
            "sample_id": "S001",
            "name": "Silicon Wafer",
            "stock": 20,
            "active_quantity": 10,
            "stock_status": "여유",
        },
        {
            "sample_id": "S002",
            "name": "GaAs Wafer",
            "stock": 0,
            "active_quantity": 5,
            "stock_status": "고갈",
        },
    ]
    view.show_stock_summary(summaries)
    out = capsys.readouterr().out
    assert "S001" in out
    assert "S002" in out
    assert "여유" in out
    assert "고갈" in out


def test_show_stock_summary_with_data_no_empty_message(view, capsys):
    """show_stock_summary does not print empty message when data is present."""
    summaries = [
        {
            "sample_id": "S001",
            "name": "Silicon Wafer",
            "stock": 10,
            "active_quantity": 5,
            "stock_status": "여유",
        }
    ]
    view.show_stock_summary(summaries)
    assert "등록된 시료가 없습니다." not in capsys.readouterr().out
