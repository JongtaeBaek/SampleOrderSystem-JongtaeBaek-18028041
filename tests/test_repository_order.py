"""Tests for repository/order_repository.py — 100% coverage.

Covers OrderStatus serialisation / deserialisation and all I/O branches.
"""
import json
from pathlib import Path

from model.order import Order, OrderStatus
from repository.order_repository import OrderRepository


class TestOrderRepositoryLoad:
    """Tests for OrderRepository.load()."""

    def test_load_returns_empty_list_when_file_does_not_exist(self, tmp_path):
        """load() returns [] when the JSON file does not exist."""
        repo = OrderRepository(tmp_path / "orders.json")
        result = repo.load()
        assert result == []

    def test_load_deserialises_order_status_from_string(self, tmp_path):
        """load() reconstructs OrderStatus enum from stored string value."""
        path = tmp_path / "orders.json"
        data = [
            {
                "order_id": "abc12345",
                "sample_id": "S001",
                "customer_name": "ACME",
                "quantity": 10,
                "status": "RESERVED",
            }
        ]
        path.write_text(json.dumps(data), encoding="utf-8")

        repo = OrderRepository(path)
        result = repo.load()

        assert len(result) == 1
        o = result[0]
        assert isinstance(o, Order)
        assert o.order_id == "abc12345"
        assert o.status is OrderStatus.RESERVED

    def test_load_all_order_statuses(self, tmp_path):
        """load() correctly deserialises every possible OrderStatus value."""
        path = tmp_path / "orders.json"
        statuses = ["RESERVED", "CONFIRMED", "PRODUCING", "RELEASE", "REJECTED"]
        data = [
            {
                "order_id": f"id{i:04d}",
                "sample_id": "S001",
                "customer_name": "Cust",
                "quantity": 1,
                "status": s,
            }
            for i, s in enumerate(statuses)
        ]
        path.write_text(json.dumps(data), encoding="utf-8")

        repo = OrderRepository(path)
        result = repo.load()

        assert len(result) == 5
        loaded_statuses = [o.status for o in result]
        assert OrderStatus.RESERVED in loaded_statuses
        assert OrderStatus.CONFIRMED in loaded_statuses
        assert OrderStatus.PRODUCING in loaded_statuses
        assert OrderStatus.RELEASE in loaded_statuses
        assert OrderStatus.REJECTED in loaded_statuses

    def test_load_returns_multiple_orders(self, tmp_path):
        """load() parses all records when multiple orders exist in the file."""
        path = tmp_path / "orders.json"
        data = [
            {"order_id": "id0001", "sample_id": "S001", "customer_name": "A", "quantity": 5, "status": "RESERVED"},
            {"order_id": "id0002", "sample_id": "S002", "customer_name": "B", "quantity": 15, "status": "CONFIRMED"},
        ]
        path.write_text(json.dumps(data), encoding="utf-8")

        repo = OrderRepository(path)
        result = repo.load()

        assert len(result) == 2
        assert result[0].order_id == "id0001"
        assert result[1].order_id == "id0002"

    def test_load_empty_json_array(self, tmp_path):
        """load() returns an empty list when the JSON file contains []."""
        path = tmp_path / "orders.json"
        path.write_text("[]", encoding="utf-8")

        repo = OrderRepository(path)
        result = repo.load()
        assert result == []


class TestOrderRepositorySave:
    """Tests for OrderRepository.save()."""

    def test_save_creates_file(self, tmp_path):
        """save() creates the JSON file if it does not exist."""
        path = tmp_path / "orders.json"
        repo = OrderRepository(path)
        orders = [Order("id0001", "S001", "ACME", 10, OrderStatus.RESERVED)]

        repo.save(orders)

        assert path.exists()

    def test_save_creates_parent_directories(self, tmp_path):
        """save() creates any missing intermediate directories."""
        path = tmp_path / "nested" / "data" / "orders.json"
        repo = OrderRepository(path)
        repo.save([])
        assert path.parent.exists()

    def test_save_serialises_status_as_string(self, tmp_path):
        """save() writes the status field as a plain string (not an Enum repr)."""
        path = tmp_path / "orders.json"
        repo = OrderRepository(path)
        order = Order("id0001", "S001", "ACME", 10, OrderStatus.CONFIRMED)

        repo.save([order])

        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw[0]["status"] == "CONFIRMED"
        assert isinstance(raw[0]["status"], str)

    def test_save_all_status_values_serialised_correctly(self, tmp_path):
        """save() serialises every OrderStatus variant as its string value."""
        path = tmp_path / "orders.json"
        repo = OrderRepository(path)
        orders = [
            Order(f"id{i:04d}", "S001", "C", 1, status)
            for i, status in enumerate(OrderStatus)
        ]

        repo.save(orders)

        raw = json.loads(path.read_text(encoding="utf-8"))
        serialised_statuses = {r["status"] for r in raw}
        assert serialised_statuses == {"RESERVED", "CONFIRMED", "PRODUCING", "RELEASE", "REJECTED"}

    def test_save_and_load_roundtrip(self, tmp_path):
        """save() then load() reproduces the original list of Order objects."""
        path = tmp_path / "orders.json"
        repo = OrderRepository(path)
        original = [
            Order("id0001", "S001", "Alpha", 10, OrderStatus.RESERVED),
            Order("id0002", "S002", "Beta", 5, OrderStatus.PRODUCING),
            Order("id0003", "S001", "Gamma", 20, OrderStatus.CONFIRMED),
        ]

        repo.save(original)
        loaded = repo.load()

        assert loaded == original

    def test_save_empty_list(self, tmp_path):
        """save() correctly writes an empty JSON array."""
        path = tmp_path / "orders.json"
        repo = OrderRepository(path)

        repo.save([])

        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw == []

    def test_save_overwrites_existing_file(self, tmp_path):
        """save() replaces previous content when called a second time."""
        path = tmp_path / "orders.json"
        repo = OrderRepository(path)

        repo.save([Order("old001", "S001", "Old", 1, OrderStatus.RESERVED)])
        repo.save([Order("new001", "S002", "New", 2, OrderStatus.CONFIRMED)])

        loaded = repo.load()
        assert len(loaded) == 1
        assert loaded[0].order_id == "new001"

    def test_save_non_ascii_customer_name(self, tmp_path):
        """save() preserves non-ASCII characters in customer_name."""
        path = tmp_path / "orders.json"
        repo = OrderRepository(path)
        orders = [Order("id0001", "S001", "고객사A", 5, OrderStatus.RESERVED)]

        repo.save(orders)
        loaded = repo.load()

        assert loaded[0].customer_name == "고객사A"


class TestOrderRepositoryDefaultPath:
    """Tests for default path configuration."""

    def test_default_path_is_data_orders_json(self):
        """The default path points to data/orders.json."""
        repo = OrderRepository()
        assert repo._path == Path("data/orders.json")
