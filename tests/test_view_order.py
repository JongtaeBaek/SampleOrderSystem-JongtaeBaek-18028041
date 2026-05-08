"""Tests for view/order_view.py — 100% coverage."""
from unittest.mock import patch

from model.order import Order, OrderStatus
from view.order_view import OrderView, _TABLE_WIDTH


# ---------------------------------------------------------------------------
# prompt_reserve
# ---------------------------------------------------------------------------

def test_prompt_reserve_returns_tuple():
    """prompt_reserve calls input 3 times and returns (str, str, int)."""
    view = OrderView()
    inputs = ["S001", "홍길동", "10"]
    with patch("builtins.input", side_effect=inputs) as mock_input:
        result = view.prompt_reserve()
    assert mock_input.call_count == 3
    sample_id, customer_name, quantity = result
    assert isinstance(sample_id, str)
    assert isinstance(customer_name, str)
    assert isinstance(quantity, int)
    assert sample_id == "S001"
    assert customer_name == "홍길동"
    assert quantity == 10


def test_prompt_reserve_strips_whitespace():
    """prompt_reserve strips leading/trailing whitespace from string inputs."""
    view = OrderView()
    inputs = [" S001 ", " 홍길동 ", "5"]
    with patch("builtins.input", side_effect=inputs):
        sample_id, customer_name, quantity = view.prompt_reserve()
    assert sample_id == "S001"
    assert customer_name == "홍길동"
    assert quantity == 5


# ---------------------------------------------------------------------------
# show_order_list — empty branch
# ---------------------------------------------------------------------------

def test_show_order_list_empty(capsys):
    """show_order_list prints '주문이 없습니다.' when the list is empty."""
    view = OrderView()
    view.show_order_list([])
    captured = capsys.readouterr()
    assert "주문이 없습니다." in captured.out


def test_show_order_list_empty_no_header(capsys):
    """show_order_list does not print a header when the list is empty."""
    view = OrderView()
    view.show_order_list([])
    captured = capsys.readouterr()
    assert "주문ID" not in captured.out


# ---------------------------------------------------------------------------
# show_order_list — non-empty branch
# ---------------------------------------------------------------------------

def test_show_order_list_with_orders(capsys):
    """show_order_list prints header, separator line, and order rows."""
    view = OrderView()
    orders = [
        Order("abcd1234", "S001", "홍길동", 10, OrderStatus.RESERVED),
    ]
    view.show_order_list(orders)
    captured = capsys.readouterr()
    # Header fields present
    assert "주문ID" in captured.out
    assert "시료ID" in captured.out
    assert "고객명" in captured.out
    assert "수량" in captured.out
    assert "상태" in captured.out
    # Separator line present
    assert "-" * _TABLE_WIDTH in captured.out
    # Row data present
    assert "abcd1234" in captured.out
    assert "S001" in captured.out
    assert "홍길동" in captured.out
    assert "10" in captured.out
    assert "RESERVED" in captured.out


def test_show_order_list_multiple_rows(capsys):
    """show_order_list prints all orders when there are multiple."""
    view = OrderView()
    orders = [
        Order("aaaaaaaa", "S001", "고객A", 5, OrderStatus.RESERVED),
        Order("bbbbbbbb", "S002", "고객B", 3, OrderStatus.CONFIRMED),
    ]
    view.show_order_list(orders)
    captured = capsys.readouterr()
    assert "aaaaaaaa" in captured.out
    assert "bbbbbbbb" in captured.out
    assert "고객A" in captured.out
    assert "고객B" in captured.out


def test_show_order_list_with_orders_no_empty_message(capsys):
    """show_order_list does not print '주문이 없습니다.' when orders exist."""
    view = OrderView()
    orders = [
        Order("abcd1234", "S001", "홍길동", 10, OrderStatus.RESERVED),
    ]
    view.show_order_list(orders)
    captured = capsys.readouterr()
    assert "주문이 없습니다." not in captured.out


# ---------------------------------------------------------------------------
# show_reserve_success
# ---------------------------------------------------------------------------

def test_show_reserve_success(capsys):
    """show_reserve_success prints '주문 예약 완료: <order_id>'."""
    view = OrderView()
    view.show_reserve_success("abcd1234")
    captured = capsys.readouterr()
    assert "주문 예약 완료: abcd1234" in captured.out


def test_show_reserve_success_contains_order_id(capsys):
    """show_reserve_success output contains the exact order_id passed."""
    view = OrderView()
    order_id = "xyz98765"
    view.show_reserve_success(order_id)
    captured = capsys.readouterr()
    assert order_id in captured.out
