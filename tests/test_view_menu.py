"""Tests for view/menu_view.py — 100% coverage."""
from unittest.mock import patch

from view.menu_view import MenuView, _W


# ---------------------------------------------------------------------------
# show_main_menu
# ---------------------------------------------------------------------------

def test_show_main_menu_contains_title(capsys):
    """show_main_menu prints the system title."""
    view = MenuView()
    view.show_main_menu(n_samples=3, reserved=2, producing=1, confirmed=4)
    captured = capsys.readouterr()
    assert "반도체 시료 생산 주문 관리 시스템" in captured.out


def test_show_main_menu_contains_dashboard(capsys):
    """show_main_menu prints the dashboard with n_samples, reserved, producing, confirmed."""
    view = MenuView()
    view.show_main_menu(n_samples=5, reserved=3, producing=2, confirmed=7)
    captured = capsys.readouterr()
    assert "시료: 5종" in captured.out
    assert "접수: 3건" in captured.out
    assert "생산중: 2건" in captured.out
    assert "출고대기: 7건" in captured.out


def test_show_main_menu_contains_all_menu_items(capsys):
    """show_main_menu prints all 7 menu items (1~6 and 0)."""
    view = MenuView()
    view.show_main_menu(n_samples=0, reserved=0, producing=0, confirmed=0)
    captured = capsys.readouterr()
    assert "1. 시료 관리" in captured.out
    assert "2. 시료 주문" in captured.out
    assert "3. 주문 승인/거절" in captured.out
    assert "4. 모니터링" in captured.out
    assert "5. 생산 라인 조회" in captured.out
    assert "6. 출고 처리" in captured.out
    assert "0. 종료" in captured.out


def test_show_main_menu_contains_separator_lines(capsys):
    """show_main_menu prints '=' and '-' separator lines of width _W."""
    view = MenuView()
    view.show_main_menu(n_samples=0, reserved=0, producing=0, confirmed=0)
    captured = capsys.readouterr()
    assert "=" * _W in captured.out
    assert "-" * _W in captured.out


def test_show_main_menu_zero_values(capsys):
    """show_main_menu works with all-zero dashboard values."""
    view = MenuView()
    view.show_main_menu(n_samples=0, reserved=0, producing=0, confirmed=0)
    captured = capsys.readouterr()
    assert "시료: 0종" in captured.out
    assert "접수: 0건" in captured.out
    assert "생산중: 0건" in captured.out
    assert "출고대기: 0건" in captured.out


# ---------------------------------------------------------------------------
# prompt_main_choice
# ---------------------------------------------------------------------------

def test_prompt_main_choice_calls_input_once():
    """prompt_main_choice calls input exactly once."""
    view = MenuView()
    with patch("builtins.input", return_value="1") as mock_input:
        view.prompt_main_choice()
    assert mock_input.call_count == 1


def test_prompt_main_choice_returns_stripped_value():
    """prompt_main_choice returns the stripped input value."""
    view = MenuView()
    with patch("builtins.input", return_value="  3  "):
        result = view.prompt_main_choice()
    assert result == "3"


def test_prompt_main_choice_returns_zero():
    """prompt_main_choice returns '0' when user enters '0'."""
    view = MenuView()
    with patch("builtins.input", return_value="0"):
        result = view.prompt_main_choice()
    assert result == "0"


# ---------------------------------------------------------------------------
# show_sub_menu
# ---------------------------------------------------------------------------

def test_show_sub_menu_contains_title(capsys):
    """show_sub_menu prints the title in brackets."""
    view = MenuView()
    view.show_sub_menu("시료 관리", ["시료 등록", "시료 조회"])
    captured = capsys.readouterr()
    assert "[ 시료 관리 ]" in captured.out


def test_show_sub_menu_contains_options(capsys):
    """show_sub_menu prints all options with numbering."""
    view = MenuView()
    view.show_sub_menu("테스트", ["옵션A", "옵션B", "옵션C"])
    captured = capsys.readouterr()
    assert "1. 옵션A" in captured.out
    assert "2. 옵션B" in captured.out
    assert "3. 옵션C" in captured.out


def test_show_sub_menu_contains_back_option(capsys):
    """show_sub_menu always prints '0. 돌아가기'."""
    view = MenuView()
    view.show_sub_menu("타이틀", ["항목1"])
    captured = capsys.readouterr()
    assert "0. 돌아가기" in captured.out


def test_show_sub_menu_contains_separator_lines(capsys):
    """show_sub_menu prints '=' and '-' separator lines of width _W."""
    view = MenuView()
    view.show_sub_menu("타이틀", ["항목1"])
    captured = capsys.readouterr()
    assert "=" * _W in captured.out
    assert "-" * _W in captured.out


def test_show_sub_menu_empty_options(capsys):
    """show_sub_menu with empty options still prints title and '0. 돌아가기'."""
    view = MenuView()
    view.show_sub_menu("빈 메뉴", [])
    captured = capsys.readouterr()
    assert "[ 빈 메뉴 ]" in captured.out
    assert "0. 돌아가기" in captured.out


# ---------------------------------------------------------------------------
# prompt_sub_choice
# ---------------------------------------------------------------------------

def test_prompt_sub_choice_calls_input_once():
    """prompt_sub_choice calls input exactly once."""
    view = MenuView()
    with patch("builtins.input", return_value="1") as mock_input:
        view.prompt_sub_choice()
    assert mock_input.call_count == 1


def test_prompt_sub_choice_returns_stripped_value():
    """prompt_sub_choice returns the stripped input value."""
    view = MenuView()
    with patch("builtins.input", return_value="  2  "):
        result = view.prompt_sub_choice()
    assert result == "2"


def test_prompt_sub_choice_returns_zero():
    """prompt_sub_choice returns '0' when user enters '0'."""
    view = MenuView()
    with patch("builtins.input", return_value="0"):
        result = view.prompt_sub_choice()
    assert result == "0"


# ---------------------------------------------------------------------------
# show_invalid_choice
# ---------------------------------------------------------------------------

def test_show_invalid_choice_prints_error_message(capsys):
    """show_invalid_choice prints the expected error message."""
    view = MenuView()
    view.show_invalid_choice()
    captured = capsys.readouterr()
    assert "잘못된 입력입니다. 다시 선택하세요." in captured.out


def test_show_invalid_choice_output_is_non_empty(capsys):
    """show_invalid_choice produces non-empty output."""
    view = MenuView()
    view.show_invalid_choice()
    captured = capsys.readouterr()
    assert captured.out.strip() != ""
