"""Tests for model/sample.py — 100% coverage."""
import dataclasses

from model.sample import Sample


def test_sample_creation_with_all_fields():
    """Sample dataclass can be created with all fields explicitly set."""
    s = Sample(
        sample_id="S001",
        name="Silicon Wafer",
        avg_production_time=2.5,
        yield_rate=0.85,
        stock=100,
    )
    assert s.sample_id == "S001"
    assert s.name == "Silicon Wafer"
    assert s.avg_production_time == 2.5
    assert s.yield_rate == 0.85
    assert s.stock == 100


def test_sample_stock_default_is_zero():
    """Sample.stock defaults to 0 when not provided."""
    s = Sample(
        sample_id="S002",
        name="GaAs Chip",
        avg_production_time=3.0,
        yield_rate=0.75,
    )
    assert s.stock == 0


def test_sample_is_dataclass():
    """Sample is a proper dataclass (supports asdict, fields)."""
    s = Sample("S003", "InP Wafer", 1.5, 0.9, 50)
    d = dataclasses.asdict(s)
    assert d == {
        "sample_id": "S003",
        "name": "InP Wafer",
        "avg_production_time": 1.5,
        "yield_rate": 0.9,
        "stock": 50,
    }


def test_sample_equality():
    """Two Sample instances with the same values are equal (dataclass default)."""
    s1 = Sample("S001", "Wafer A", 2.0, 0.8, 10)
    s2 = Sample("S001", "Wafer A", 2.0, 0.8, 10)
    assert s1 == s2


def test_sample_inequality():
    """Two Sample instances with different values are not equal."""
    s1 = Sample("S001", "Wafer A", 2.0, 0.8, 10)
    s2 = Sample("S001", "Wafer A", 2.0, 0.8, 20)
    assert s1 != s2


def test_sample_stock_mutation():
    """Sample.stock field can be mutated directly."""
    s = Sample("S004", "Nitride", 1.0, 0.95, 0)
    s.stock += 50
    assert s.stock == 50


def test_sample_yield_rate_boundary_values():
    """Sample accepts boundary yield_rate values 0.0 and 1.0."""
    s_min = Sample("S005", "Min Yield", 1.0, 0.0, 0)
    s_max = Sample("S006", "Max Yield", 1.0, 1.0, 0)
    assert s_min.yield_rate == 0.0
    assert s_max.yield_rate == 1.0
