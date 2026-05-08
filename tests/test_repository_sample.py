"""Tests for repository/sample_repository.py — 100% coverage (tmp_path I/O)."""
import json
from pathlib import Path

from model.sample import Sample
from repository.sample_repository import SampleRepository


class TestSampleRepositoryLoad:
    """Tests for SampleRepository.load()."""

    def test_load_returns_empty_list_when_file_does_not_exist(self, tmp_path):
        """load() returns [] when the JSON file does not exist (first run)."""
        repo = SampleRepository(tmp_path / "samples.json")
        result = repo.load()
        assert result == []

    def test_load_returns_samples_from_file(self, tmp_path):
        """load() deserialises records from an existing JSON file into Sample objects."""
        path = tmp_path / "samples.json"
        data = [
            {
                "sample_id": "S001",
                "name": "Silicon Wafer",
                "avg_production_time": 2.5,
                "yield_rate": 0.85,
                "stock": 100,
            }
        ]
        path.write_text(json.dumps(data), encoding="utf-8")

        repo = SampleRepository(path)
        result = repo.load()

        assert len(result) == 1
        s = result[0]
        assert isinstance(s, Sample)
        assert s.sample_id == "S001"
        assert s.name == "Silicon Wafer"
        assert s.avg_production_time == 2.5
        assert s.yield_rate == 0.85
        assert s.stock == 100

    def test_load_returns_multiple_samples(self, tmp_path):
        """load() correctly parses a file with multiple sample records."""
        path = tmp_path / "samples.json"
        data = [
            {"sample_id": "S001", "name": "Wafer A", "avg_production_time": 1.0, "yield_rate": 0.9, "stock": 50},
            {"sample_id": "S002", "name": "Wafer B", "avg_production_time": 2.0, "yield_rate": 0.8, "stock": 0},
        ]
        path.write_text(json.dumps(data), encoding="utf-8")

        repo = SampleRepository(path)
        result = repo.load()

        assert len(result) == 2
        assert result[0].sample_id == "S001"
        assert result[1].sample_id == "S002"

    def test_load_empty_json_array(self, tmp_path):
        """load() returns an empty list when the JSON file contains an empty array."""
        path = tmp_path / "samples.json"
        path.write_text("[]", encoding="utf-8")

        repo = SampleRepository(path)
        result = repo.load()
        assert result == []


class TestSampleRepositorySave:
    """Tests for SampleRepository.save()."""

    def test_save_creates_file(self, tmp_path):
        """save() creates the JSON file when it does not yet exist."""
        path = tmp_path / "data" / "samples.json"
        repo = SampleRepository(path)
        samples = [Sample("S001", "Wafer A", 1.0, 0.9, 10)]

        repo.save(samples)

        assert path.exists()

    def test_save_creates_parent_directories(self, tmp_path):
        """save() creates intermediate directories if they do not exist."""
        path = tmp_path / "nested" / "dir" / "samples.json"
        repo = SampleRepository(path)
        repo.save([])
        assert path.parent.exists()

    def test_save_writes_valid_json(self, tmp_path):
        """save() writes well-formed JSON that can be read back."""
        path = tmp_path / "samples.json"
        repo = SampleRepository(path)
        samples = [Sample("S001", "Silicon Wafer", 2.5, 0.85, 100)]

        repo.save(samples)

        raw = json.loads(path.read_text(encoding="utf-8"))
        assert len(raw) == 1
        assert raw[0]["sample_id"] == "S001"
        assert raw[0]["name"] == "Silicon Wafer"
        assert raw[0]["avg_production_time"] == 2.5
        assert raw[0]["yield_rate"] == 0.85
        assert raw[0]["stock"] == 100

    def test_save_and_load_roundtrip(self, tmp_path):
        """save() then load() produces an equivalent list of Sample objects."""
        path = tmp_path / "samples.json"
        repo = SampleRepository(path)
        original = [
            Sample("S001", "Wafer A", 1.0, 0.9, 10),
            Sample("S002", "Wafer B", 3.0, 0.7, 0),
        ]

        repo.save(original)
        loaded = repo.load()

        assert loaded == original

    def test_save_empty_list(self, tmp_path):
        """save() correctly writes an empty JSON array."""
        path = tmp_path / "samples.json"
        repo = SampleRepository(path)

        repo.save([])

        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw == []

    def test_save_overwrites_existing_file(self, tmp_path):
        """save() overwrites previous content when called a second time."""
        path = tmp_path / "samples.json"
        repo = SampleRepository(path)

        repo.save([Sample("S001", "Old", 1.0, 0.9, 5)])
        repo.save([Sample("S002", "New", 2.0, 0.8, 20)])

        loaded = repo.load()
        assert len(loaded) == 1
        assert loaded[0].sample_id == "S002"

    def test_save_non_ascii_name(self, tmp_path):
        """save() preserves non-ASCII characters (ensure_ascii=False)."""
        path = tmp_path / "samples.json"
        repo = SampleRepository(path)
        samples = [Sample("S001", "실리콘 웨이퍼", 1.0, 0.9, 0)]

        repo.save(samples)
        loaded = repo.load()

        assert loaded[0].name == "실리콘 웨이퍼"


class TestSampleRepositoryDefaultPath:
    """Tests for default path behaviour."""

    def test_default_path_is_data_samples_json(self):
        """The default path points to data/samples.json."""
        repo = SampleRepository()
        assert repo._path == Path("data/samples.json")
