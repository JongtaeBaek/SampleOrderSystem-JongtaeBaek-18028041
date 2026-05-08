"""Tests for controller/sample_controller.py — 100% coverage."""
from unittest.mock import MagicMock

from model.sample import Sample
from controller.sample_controller import SampleController


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_controller(existing_samples=None):
    """Return (controller, mock_repo) with the given initial sample list."""
    repo = MagicMock()
    repo.load.return_value = list(existing_samples or [])
    ctrl = SampleController(repo)
    return ctrl, repo


# ---------------------------------------------------------------------------
# register — successful path
# ---------------------------------------------------------------------------

def test_register_new_sample_returns_true():
    """register returns True when the sample_id does not already exist."""
    ctrl, repo = _make_controller(existing_samples=[])
    result = ctrl.register("S001", "Silicon Wafer", 2.5, 0.85)
    assert result is True


def test_register_new_sample_calls_save():
    """register calls repo.save with the new sample appended."""
    ctrl, repo = _make_controller(existing_samples=[])
    ctrl.register("S001", "Silicon Wafer", 2.5, 0.85)
    repo.save.assert_called_once()
    saved_samples = repo.save.call_args[0][0]
    assert len(saved_samples) == 1
    assert saved_samples[0].sample_id == "S001"
    assert saved_samples[0].name == "Silicon Wafer"
    assert saved_samples[0].avg_production_time == 2.5
    assert saved_samples[0].yield_rate == 0.85


def test_register_preserves_existing_samples():
    """register keeps existing samples intact and appends the new one."""
    existing = [Sample("E001", "Existing", 1.0, 0.9, 50)]
    ctrl, repo = _make_controller(existing_samples=existing)
    ctrl.register("S002", "New Sample", 3.0, 0.75)
    saved_samples = repo.save.call_args[0][0]
    assert len(saved_samples) == 2
    ids = [s.sample_id for s in saved_samples]
    assert "E001" in ids
    assert "S002" in ids


def test_register_new_sample_stock_defaults_to_zero():
    """register creates a new Sample with stock defaulting to 0."""
    ctrl, repo = _make_controller(existing_samples=[])
    ctrl.register("S001", "Test", 1.0, 0.9)
    saved_samples = repo.save.call_args[0][0]
    assert saved_samples[0].stock == 0


# ---------------------------------------------------------------------------
# register — duplicate ID path
# ---------------------------------------------------------------------------

def test_register_duplicate_id_returns_false():
    """register returns False when sample_id already exists."""
    existing = [Sample("S001", "Existing", 1.0, 0.9, 10)]
    ctrl, repo = _make_controller(existing_samples=existing)
    result = ctrl.register("S001", "Duplicate", 2.0, 0.8)
    assert result is False


def test_register_duplicate_id_does_not_call_save():
    """register does not call repo.save when sample_id is duplicate."""
    existing = [Sample("S001", "Existing", 1.0, 0.9, 10)]
    ctrl, repo = _make_controller(existing_samples=existing)
    ctrl.register("S001", "Duplicate", 2.0, 0.8)
    repo.save.assert_not_called()


def test_register_duplicate_id_prints_error(capsys):
    """register prints an error message containing the duplicate ID."""
    existing = [Sample("S001", "Existing", 1.0, 0.9, 10)]
    ctrl, repo = _make_controller(existing_samples=existing)
    ctrl.register("S001", "Duplicate", 2.0, 0.8)
    captured = capsys.readouterr()
    assert "S001" in captured.out
    assert "오류" in captured.out


# ---------------------------------------------------------------------------
# list_all
# ---------------------------------------------------------------------------

def test_list_all_returns_all_samples():
    """list_all returns the complete list from the repository."""
    samples = [
        Sample("S001", "Alpha", 1.0, 0.9, 10),
        Sample("S002", "Beta", 2.0, 0.8, 20),
    ]
    ctrl, repo = _make_controller(existing_samples=samples)
    result = ctrl.list_all()
    assert result == samples


def test_list_all_returns_empty_when_no_samples():
    """list_all returns an empty list when the repository is empty."""
    ctrl, repo = _make_controller(existing_samples=[])
    result = ctrl.list_all()
    assert result == []


def test_list_all_calls_repo_load():
    """list_all delegates to repo.load exactly once."""
    ctrl, repo = _make_controller(existing_samples=[])
    ctrl.list_all()
    repo.load.assert_called_once()


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def test_search_returns_matching_samples():
    """search returns samples whose name contains the keyword."""
    samples = [
        Sample("S001", "Silicon Wafer", 1.0, 0.9, 10),
        Sample("S002", "GaAs Chip", 2.0, 0.8, 20),
        Sample("S003", "Silicon Nitride", 3.0, 0.7, 30),
    ]
    ctrl, repo = _make_controller(existing_samples=samples)
    result = ctrl.search("Silicon")
    assert len(result) == 2
    ids = [s.sample_id for s in result]
    assert "S001" in ids
    assert "S003" in ids


def test_search_returns_empty_when_no_match():
    """search returns an empty list when no sample name contains the keyword."""
    samples = [
        Sample("S001", "Silicon Wafer", 1.0, 0.9, 10),
        Sample("S002", "GaAs Chip", 2.0, 0.8, 20),
    ]
    ctrl, repo = _make_controller(existing_samples=samples)
    result = ctrl.search("Nitride")
    assert result == []


def test_search_empty_keyword_returns_all():
    """search with empty keyword matches every sample (substring of all strings)."""
    samples = [
        Sample("S001", "Alpha", 1.0, 0.9, 10),
        Sample("S002", "Beta", 2.0, 0.8, 20),
    ]
    ctrl, repo = _make_controller(existing_samples=samples)
    result = ctrl.search("")
    assert len(result) == 2


def test_search_calls_repo_load():
    """search delegates to repo.load exactly once."""
    ctrl, repo = _make_controller(existing_samples=[])
    ctrl.search("anything")
    repo.load.assert_called_once()


def test_search_returns_empty_when_repository_is_empty():
    """search returns an empty list when the repository has no samples."""
    ctrl, repo = _make_controller(existing_samples=[])
    result = ctrl.search("keyword")
    assert result == []


def test_search_exact_name_match():
    """search returns a sample when keyword exactly equals the name."""
    samples = [Sample("S001", "ExactName", 1.0, 0.9, 0)]
    ctrl, repo = _make_controller(existing_samples=samples)
    result = ctrl.search("ExactName")
    assert len(result) == 1
    assert result[0].sample_id == "S001"
