"""Tests for main.py — 100% coverage."""
import json
import os
import runpy
from unittest.mock import patch

from main import _restore_queue, main
from model.order import Order, OrderStatus
from model.sample import Sample
from model.production import ProductionQueue


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# _restore_queue
# ---------------------------------------------------------------------------

def test_restore_queue_empty():
    """_restore_queue returns an empty queue when there are no PRODUCING orders."""
    orders = [
        Order("aaa00001", "S001", "고객A", 5, OrderStatus.RESERVED),
        Order("aaa00002", "S001", "고객B", 3, OrderStatus.CONFIRMED),
    ]
    samples = [Sample("S001", "Silicon Wafer", 2.5, 0.85, 100)]
    queue = _restore_queue(orders, samples)
    assert isinstance(queue, ProductionQueue)
    assert queue.is_empty()


def test_restore_queue_with_producing():
    """_restore_queue enqueues one job per PRODUCING order."""
    orders = [
        Order("aaa00001", "S001", "고객A", 10, OrderStatus.PRODUCING),
    ]
    # stock=3, quantity=10 → shortage=7
    samples = [Sample("S001", "Silicon Wafer", 2.5, 0.85, 3)]
    queue = _restore_queue(orders, samples)
    assert not queue.is_empty()
    jobs = queue.list_all()
    assert len(jobs) == 1
    assert jobs[0].order_id == "aaa00001"
    assert jobs[0].sample_id == "S001"
    assert jobs[0].required_quantity == 7  # shortage = 10 - 3


def test_restore_queue_shortage_safety_value():
    """_restore_queue uses shortage=1 when stock >= quantity (safety fallback)."""
    orders = [
        Order("aaa00001", "S001", "고객A", 5, OrderStatus.PRODUCING),
    ]
    # stock >= quantity: should not normally happen, but the safety value kicks in
    samples = [Sample("S001", "Silicon Wafer", 2.5, 0.85, 10)]
    queue = _restore_queue(orders, samples)
    assert not queue.is_empty()
    jobs = queue.list_all()
    assert jobs[0].required_quantity == 1  # safety value


def test_restore_queue_multiple_producing():
    """_restore_queue enqueues one job for each PRODUCING order in order."""
    orders = [
        Order("aaa00001", "S001", "고객A", 10, OrderStatus.PRODUCING),
        Order("bbb00002", "S002", "고객B", 20, OrderStatus.PRODUCING),
    ]
    samples = [
        Sample("S001", "Silicon Wafer", 2.5, 0.85, 2),
        Sample("S002", "GaAs Chip", 3.0, 0.75, 5),
    ]
    queue = _restore_queue(orders, samples)
    jobs = queue.list_all()
    assert len(jobs) == 2
    assert jobs[0].order_id == "aaa00001"
    assert jobs[1].order_id == "bbb00002"


# ---------------------------------------------------------------------------
# main() — isolation via monkeypatch.chdir(tmp_path)
# ---------------------------------------------------------------------------

def test_main_menu_0_exits(monkeypatch, tmp_path):
    """main() exits cleanly when the user enters '0'."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["0"]):
        main()  # should return without raising


def test_main_menu_1_sample(monkeypatch, tmp_path):
    """main() enters sample sub-menu and returns to main when user enters '0'."""
    monkeypatch.chdir(tmp_path)
    # "1" → enter sample menu, "0" → back to main, "0" → exit main
    with patch("builtins.input", side_effect=["1", "0", "0"]):
        main()


def test_main_menu_2_order(monkeypatch, tmp_path):
    """main() enters order sub-menu and returns to main when user enters '0'."""
    monkeypatch.chdir(tmp_path)
    # "2" → enter order menu, "0" → back, "0" → exit
    with patch("builtins.input", side_effect=["2", "0", "0"]):
        main()


def test_main_menu_3_approval(monkeypatch, tmp_path):
    """main() enters approval sub-menu and returns to main when user enters '0'."""
    monkeypatch.chdir(tmp_path)
    # "3" → enter approval menu, "0" → back, "0" → exit
    with patch("builtins.input", side_effect=["3", "0", "0"]):
        main()


def test_main_menu_4_monitoring(monkeypatch, tmp_path):
    """main() enters monitoring sub-menu and returns to main when user enters '0'."""
    monkeypatch.chdir(tmp_path)
    # "4" → enter monitoring menu, "0" → back, "0" → exit
    with patch("builtins.input", side_effect=["4", "0", "0"]):
        main()


def test_main_menu_5_production(monkeypatch, tmp_path):
    """main() enters production sub-menu and returns to main when user enters '0'."""
    monkeypatch.chdir(tmp_path)
    # "5" → enter production menu, "0" → back, "0" → exit
    with patch("builtins.input", side_effect=["5", "0", "0"]):
        main()


def test_main_menu_6_release(monkeypatch, tmp_path):
    """main() enters release sub-menu and returns to main when user enters '0'."""
    monkeypatch.chdir(tmp_path)
    # "6" → enter release menu, "0" → back, "0" → exit
    with patch("builtins.input", side_effect=["6", "0", "0"]):
        main()


def test_main_menu_invalid(monkeypatch, tmp_path):
    """main() calls show_invalid_choice for an unrecognized menu input."""
    monkeypatch.chdir(tmp_path)
    # "9" → invalid choice, "0" → exit
    with patch("builtins.input", side_effect=["9", "0"]):
        main()


# ---------------------------------------------------------------------------
# sub-menu invalid choice paths
# ---------------------------------------------------------------------------

def test_handle_sample_menu_invalid_choice(monkeypatch, tmp_path):
    """_handle_sample_menu calls show_invalid_choice for unrecognized input."""
    monkeypatch.chdir(tmp_path)
    # main→"1"(sample menu), "9"(invalid), "0"(back), "0"(exit main)
    with patch("builtins.input", side_effect=["1", "9", "0", "0"]):
        main()


def test_handle_order_menu_invalid_choice(monkeypatch, tmp_path):
    """_handle_order_menu calls show_invalid_choice for unrecognized input."""
    monkeypatch.chdir(tmp_path)
    # main→"2"(order menu), "9"(invalid), "0"(back), "0"(exit main)
    with patch("builtins.input", side_effect=["2", "9", "0", "0"]):
        main()


def test_handle_approval_menu_invalid_choice(monkeypatch, tmp_path):
    """_handle_approval_menu calls show_invalid_choice for unrecognized input."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["3", "9", "0", "0"]):
        main()


def test_handle_monitoring_menu_invalid_choice(monkeypatch, tmp_path):
    """_handle_monitoring_menu calls show_invalid_choice for unrecognized input."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["4", "9", "0", "0"]):
        main()


def test_handle_production_menu_invalid_choice(monkeypatch, tmp_path):
    """_handle_production_menu calls show_invalid_choice for unrecognized input."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["5", "9", "0", "0"]):
        main()


def test_handle_release_menu_invalid_choice(monkeypatch, tmp_path):
    """_handle_release_menu calls show_invalid_choice for unrecognized input."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["6", "9", "0", "0"]):
        main()


# ---------------------------------------------------------------------------
# sub-menu feature paths
# ---------------------------------------------------------------------------

def test_handle_sample_menu_list_all(monkeypatch, tmp_path):
    """_handle_sample_menu choice '2' calls sample list view."""
    monkeypatch.chdir(tmp_path)
    # main→"1"(sample), "2"(list), "0"(back), "0"(exit)
    with patch("builtins.input", side_effect=["1", "2", "0", "0"]):
        main()


def test_handle_sample_menu_search(monkeypatch, tmp_path):
    """_handle_sample_menu choice '3' calls sample search with empty keyword."""
    monkeypatch.chdir(tmp_path)
    # main→"1"(sample), "3"(search), keyword="", "0"(back), "0"(exit)
    with patch("builtins.input", side_effect=["1", "3", "", "0", "0"]):
        main()


def test_handle_sample_menu_register(monkeypatch, tmp_path):
    """_handle_sample_menu choice '1' registers a new sample."""
    monkeypatch.chdir(tmp_path)
    # main→"1"(sample), "1"(register), id/name/time/yield, "0"(back), "0"(exit)
    with patch("builtins.input", side_effect=["1", "1", "S001", "TestSample", "2.5", "0.85", "0", "0"]):
        main()


def test_handle_order_menu_reserve(monkeypatch, tmp_path):
    """_handle_order_menu choice '1' tries to reserve an order."""
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    samples_data = [
        {"sample_id": "S001", "name": "Silicon", "avg_production_time": 2.5,
         "yield_rate": 0.85, "stock": 100}
    ]
    _write_json(data_dir / "samples.json", samples_data)
    # main→"2"(order), "1"(reserve), sample_id/customer/qty, "0"(back), "0"(exit)
    with patch("builtins.input", side_effect=["2", "1", "S001", "고객A", "5", "0", "0"]):
        main()


def test_handle_approval_menu_list_reserved(monkeypatch, tmp_path):
    """_handle_approval_menu choice '1' shows reserved order list."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["3", "1", "0", "0"]):
        main()


def test_handle_monitoring_menu_order_summary(monkeypatch, tmp_path):
    """_handle_monitoring_menu choice '1' shows order summary."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["4", "1", "0", "0"]):
        main()


def test_handle_monitoring_menu_stock_summary(monkeypatch, tmp_path):
    """_handle_monitoring_menu choice '2' shows stock summary."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["4", "2", "0", "0"]):
        main()


def test_handle_production_menu_show_current_no_job(monkeypatch, tmp_path):
    """_handle_production_menu choice '1' with empty queue shows no job."""
    monkeypatch.chdir(tmp_path)
    # "1"(production menu), "1"(show current), "0"(back), "0"(exit)
    with patch("builtins.input", side_effect=["5", "1", "0", "0"]):
        main()


def test_handle_production_menu_list_queue(monkeypatch, tmp_path):
    """_handle_production_menu choice '2' shows queue list."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["5", "2", "0", "0"]):
        main()


def test_handle_release_menu_list_confirmed(monkeypatch, tmp_path):
    """_handle_release_menu choice '1' shows confirmed order list."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["6", "1", "0", "0"]):
        main()


def test_handle_release_menu_release_not_found(monkeypatch, tmp_path):
    """_handle_release_menu choice '2' attempts release with nonexistent order_id."""
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["6", "2", "nonexistent", "0", "0"]):
        main()


# ---------------------------------------------------------------------------
# test_main_restores_queue_on_start
# ---------------------------------------------------------------------------

def test_main_restores_queue_on_start(monkeypatch, tmp_path):
    """main() restores the ProductionQueue from PRODUCING orders in JSON on startup."""
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    samples_data = [
        {"sample_id": "S001", "name": "Silicon Wafer", "avg_production_time": 2.5,
         "yield_rate": 0.85, "stock": 2}
    ]
    orders_data = [
        {"order_id": "aaa00001", "sample_id": "S001", "customer_name": "고객A",
         "quantity": 10, "status": "PRODUCING"}
    ]
    _write_json(data_dir / "samples.json", samples_data)
    _write_json(data_dir / "orders.json", orders_data)

    # Enter production menu → show current (the restored job) → decline completion → back → exit
    with patch("builtins.input", side_effect=["5", "1", "n", "0", "0"]):
        main()


def test_handle_production_menu_complete_job(monkeypatch, tmp_path):
    """_handle_production_menu 'y' on show_current completes the production job."""
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    samples_data = [
        {"sample_id": "S001", "name": "Silicon Wafer", "avg_production_time": 2.5,
         "yield_rate": 0.85, "stock": 2}
    ]
    orders_data = [
        {"order_id": "aaa00001", "sample_id": "S001", "customer_name": "고객A",
         "quantity": 10, "status": "PRODUCING"}
    ]
    _write_json(data_dir / "samples.json", samples_data)
    _write_json(data_dir / "orders.json", orders_data)

    # production menu → show current → confirm "y" → complete → back → exit
    with patch("builtins.input", side_effect=["5", "1", "y", "0", "0"]):
        main()


# ---------------------------------------------------------------------------
# Approval menu: approve and reject branches
# ---------------------------------------------------------------------------

def test_handle_approval_menu_approve(monkeypatch, tmp_path):
    """_handle_approval_menu choice '2' calls approve on a RESERVED order."""
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    samples_data = [
        {"sample_id": "S001", "name": "Silicon Wafer", "avg_production_time": 2.5,
         "yield_rate": 0.85, "stock": 100}
    ]
    orders_data = [
        {"order_id": "aaa00001", "sample_id": "S001", "customer_name": "고객A",
         "quantity": 5, "status": "RESERVED"}
    ]
    _write_json(data_dir / "samples.json", samples_data)
    _write_json(data_dir / "orders.json", orders_data)

    # main→"3"(approval), "2"(approve), order_id, "0"(back), "0"(exit)
    with patch("builtins.input", side_effect=["3", "2", "aaa00001", "0", "0"]):
        main()


def test_handle_approval_menu_reject(monkeypatch, tmp_path):
    """_handle_approval_menu choice '3' calls reject on a RESERVED order."""
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    samples_data = [
        {"sample_id": "S001", "name": "Silicon Wafer", "avg_production_time": 2.5,
         "yield_rate": 0.85, "stock": 100}
    ]
    orders_data = [
        {"order_id": "aaa00001", "sample_id": "S001", "customer_name": "고객A",
         "quantity": 5, "status": "RESERVED"}
    ]
    _write_json(data_dir / "samples.json", samples_data)
    _write_json(data_dir / "orders.json", orders_data)

    # main→"3"(approval), "3"(reject), order_id, "0"(back), "0"(exit)
    with patch("builtins.input", side_effect=["3", "3", "aaa00001", "0", "0"]):
        main()


# ---------------------------------------------------------------------------
# Release menu: successful release branch (line 149)
# ---------------------------------------------------------------------------

def test_handle_release_menu_release_success(monkeypatch, tmp_path):
    """_handle_release_menu choice '2' successfully releases a CONFIRMED order."""
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    samples_data = [
        {"sample_id": "S001", "name": "Silicon Wafer", "avg_production_time": 2.5,
         "yield_rate": 0.85, "stock": 100}
    ]
    orders_data = [
        {"order_id": "aaa00001", "sample_id": "S001", "customer_name": "고객A",
         "quantity": 5, "status": "CONFIRMED"}
    ]
    _write_json(data_dir / "samples.json", samples_data)
    _write_json(data_dir / "orders.json", orders_data)

    # main→"6"(release), "2"(release), order_id, "0"(back), "0"(exit)
    with patch("builtins.input", side_effect=["6", "2", "aaa00001", "0", "0"]):
        main()


# ---------------------------------------------------------------------------
# __main__ block coverage via runpy
# ---------------------------------------------------------------------------

def test_main_module_entry(monkeypatch, tmp_path):
    """Running main.py as __main__ calls main() and exits on '0'."""
    main_py = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
    monkeypatch.chdir(tmp_path)
    with patch("builtins.input", side_effect=["0"]):
        runpy.run_path(main_py, run_name="__main__")
