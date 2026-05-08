"""Tests for view/sample_view.py — 100% coverage."""
from unittest.mock import patch

from model.sample import Sample
from view.sample_view import SampleView, _TABLE_WIDTH


# ---------------------------------------------------------------------------
# prompt_register
# ---------------------------------------------------------------------------

def test_prompt_register_returns_stripped_values():
    """prompt_register collects and returns all four fields stripped."""
    view = SampleView()
    inputs = ["S001", " Silicon Wafer ", "2.5", "0.85"]
    with patch("builtins.input", side_effect=inputs):
        result = view.prompt_register()
    assert result == ("S001", "Silicon Wafer", 2.5, 0.85)


def test_prompt_register_numeric_conversion():
    """prompt_register converts avg_time to float and yield_rate to float."""
    view = SampleView()
    inputs = ["S002", "GaAs", "3.0", "0.75"]
    with patch("builtins.input", side_effect=inputs):
        sample_id, name, avg_time, yield_rate = view.prompt_register()
    assert isinstance(avg_time, float)
    assert isinstance(yield_rate, float)
    assert avg_time == 3.0
    assert yield_rate == 0.75


# ---------------------------------------------------------------------------
# prompt_search_keyword
# ---------------------------------------------------------------------------

def test_prompt_search_keyword_returns_stripped_string():
    """prompt_search_keyword returns the user input stripped."""
    view = SampleView()
    with patch("builtins.input", return_value="  wafer  "):
        result = view.prompt_search_keyword()
    assert result == "wafer"


def test_prompt_search_keyword_empty_string():
    """prompt_search_keyword handles empty input (all whitespace stripped)."""
    view = SampleView()
    with patch("builtins.input", return_value=""):
        result = view.prompt_search_keyword()
    assert result == ""


# ---------------------------------------------------------------------------
# show_sample_list — empty list branch
# ---------------------------------------------------------------------------

def test_show_sample_list_empty(capsys):
    """show_sample_list prints no-sample message when list is empty."""
    view = SampleView()
    view.show_sample_list([])
    captured = capsys.readouterr()
    assert "등록된 시료가 없습니다." in captured.out


# ---------------------------------------------------------------------------
# show_sample_list — non-empty list branch
# ---------------------------------------------------------------------------

def test_show_sample_list_header_and_row(capsys):
    """show_sample_list prints header and each sample row."""
    view = SampleView()
    samples = [
        Sample(sample_id="S001", name="Silicon Wafer", avg_production_time=2.5,
               yield_rate=0.85, stock=100),
    ]
    view.show_sample_list(samples)
    captured = capsys.readouterr()
    assert "ID" in captured.out
    assert "이름" in captured.out
    assert "S001" in captured.out
    assert "Silicon Wafer" in captured.out
    assert "2.5" in captured.out
    assert "0.85" in captured.out
    assert "100" in captured.out


def test_show_sample_list_separator_line(capsys):
    """show_sample_list prints a separator line of dashes."""
    view = SampleView()
    samples = [
        Sample(sample_id="S002", name="GaAs Chip", avg_production_time=3.0,
               yield_rate=0.75, stock=50),
    ]
    view.show_sample_list(samples)
    captured = capsys.readouterr()
    assert "-" * _TABLE_WIDTH in captured.out


def test_show_sample_list_multiple_rows(capsys):
    """show_sample_list prints all samples when there are multiple."""
    view = SampleView()
    samples = [
        Sample("A001", "Alpha", 1.0, 0.9, 10),
        Sample("B002", "Beta", 2.0, 0.8, 20),
        Sample("C003", "Gamma", 3.0, 0.7, 30),
    ]
    view.show_sample_list(samples)
    captured = capsys.readouterr()
    assert "A001" in captured.out
    assert "B002" in captured.out
    assert "C003" in captured.out


# ---------------------------------------------------------------------------
# show_search_result — empty list branch
# ---------------------------------------------------------------------------

def test_show_search_result_empty(capsys):
    """show_search_result prints no-result message when list is empty."""
    view = SampleView()
    view.show_search_result([])
    captured = capsys.readouterr()
    assert "검색 결과가 없습니다." in captured.out


# ---------------------------------------------------------------------------
# show_search_result — non-empty list delegates to show_sample_list
# ---------------------------------------------------------------------------

def test_show_search_result_delegates_to_show_sample_list(capsys):
    """show_search_result with results delegates output to show_sample_list."""
    view = SampleView()
    samples = [
        Sample(sample_id="S001", name="Silicon Wafer", avg_production_time=2.5,
               yield_rate=0.85, stock=100),
    ]
    view.show_search_result(samples)
    captured = capsys.readouterr()
    # Header from show_sample_list should be present
    assert "ID" in captured.out
    assert "S001" in captured.out


# ---------------------------------------------------------------------------
# show_register_success
# ---------------------------------------------------------------------------

def test_show_register_success_prints_sample_id(capsys):
    """show_register_success prints a success message containing the sample_id."""
    view = SampleView()
    view.show_register_success("S999")
    captured = capsys.readouterr()
    assert "S999" in captured.out
    assert "등록 완료" in captured.out
