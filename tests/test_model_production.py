"""Tests for model/production.py — 100% coverage."""
import math

from model.production import ProductionJob, ProductionQueue


class TestProductionJob:
    """Tests for ProductionJob dataclass and its factory method."""

    def test_create_computes_actual_production(self):
        """ProductionJob.create computes actual_production via ceil formula."""
        job = ProductionJob.create(
            order_id="order001",
            sample_id="S001",
            required_quantity=10,
            yield_rate=0.9,
            avg_production_time=2.0,
        )
        expected_actual = math.ceil(10 / (0.9 * 0.9))  # ceil(10 / 0.81) = 13
        assert job.actual_production == expected_actual

    def test_create_computes_total_time(self):
        """ProductionJob.create computes total_time = avg_production_time * actual_production."""
        job = ProductionJob.create(
            order_id="order001",
            sample_id="S001",
            required_quantity=10,
            yield_rate=0.9,
            avg_production_time=2.0,
        )
        expected_actual = math.ceil(10 / (0.9 * 0.9))
        assert job.total_time == 2.0 * expected_actual

    def test_create_sets_all_fields(self):
        """ProductionJob.create sets order_id, sample_id and required_quantity correctly."""
        job = ProductionJob.create(
            order_id="abc",
            sample_id="S999",
            required_quantity=5,
            yield_rate=0.8,
            avg_production_time=1.5,
        )
        assert job.order_id == "abc"
        assert job.sample_id == "S999"
        assert job.required_quantity == 5

    def test_create_with_exact_divisible_quantity(self):
        """create handles quantities where division produces a whole number."""
        # required=9, yield_rate=1.0 -> 9/(1.0*0.9)=10.0 -> ceil=10
        job = ProductionJob.create(
            order_id="o2",
            sample_id="S1",
            required_quantity=9,
            yield_rate=1.0,
            avg_production_time=1.0,
        )
        assert job.actual_production == math.ceil(9 / (1.0 * 0.9))
        assert job.total_time == float(job.actual_production)

    def test_create_with_low_yield_rate(self):
        """create with a low yield rate produces a higher actual_production."""
        job = ProductionJob.create(
            order_id="o3",
            sample_id="S2",
            required_quantity=100,
            yield_rate=0.5,
            avg_production_time=3.0,
        )
        expected = math.ceil(100 / (0.5 * 0.9))
        assert job.actual_production == expected

    def test_direct_instantiation(self):
        """ProductionJob can be instantiated directly with explicit field values."""
        job = ProductionJob(
            order_id="direct",
            sample_id="SD",
            required_quantity=20,
            actual_production=25,
            total_time=50.0,
        )
        assert job.order_id == "direct"
        assert job.sample_id == "SD"
        assert job.required_quantity == 20
        assert job.actual_production == 25
        assert job.total_time == 50.0

    def test_job_equality(self):
        """Two ProductionJob instances with identical fields are equal."""
        j1 = ProductionJob("o1", "S1", 10, 12, 24.0)
        j2 = ProductionJob("o1", "S1", 10, 12, 24.0)
        assert j1 == j2


class TestProductionQueue:
    """Tests for ProductionQueue FIFO operations."""

    def test_new_queue_is_empty(self):
        """A newly created ProductionQueue is empty."""
        q = ProductionQueue()
        assert q.is_empty() is True

    def test_enqueue_makes_queue_non_empty(self):
        """After enqueue, is_empty returns False."""
        q = ProductionQueue()
        job = ProductionJob("o1", "S1", 10, 12, 24.0)
        q.enqueue(job)
        assert q.is_empty() is False

    def test_dequeue_returns_first_in_first_out(self):
        """dequeue returns jobs in the order they were enqueued (FIFO)."""
        q = ProductionQueue()
        j1 = ProductionJob("o1", "S1", 10, 12, 24.0)
        j2 = ProductionJob("o2", "S2", 20, 23, 46.0)
        q.enqueue(j1)
        q.enqueue(j2)
        assert q.dequeue() is j1
        assert q.dequeue() is j2

    def test_dequeue_empties_queue(self):
        """After dequeuing the only element, queue is empty again."""
        q = ProductionQueue()
        job = ProductionJob("o1", "S1", 10, 12, 24.0)
        q.enqueue(job)
        q.dequeue()
        assert q.is_empty() is True

    def test_peek_returns_first_element_without_removing(self):
        """peek returns the front job without removing it from the queue."""
        q = ProductionQueue()
        j1 = ProductionJob("o1", "S1", 10, 12, 24.0)
        j2 = ProductionJob("o2", "S2", 5, 6, 12.0)
        q.enqueue(j1)
        q.enqueue(j2)
        assert q.peek() is j1
        # Confirm the queue still has both elements
        assert q.dequeue() is j1
        assert q.dequeue() is j2

    def test_peek_returns_none_when_empty(self):
        """peek returns None when the queue is empty."""
        q = ProductionQueue()
        assert q.peek() is None

    def test_list_all_returns_all_jobs_in_order(self):
        """list_all returns a list of all jobs in enqueue order."""
        q = ProductionQueue()
        j1 = ProductionJob("o1", "S1", 10, 12, 24.0)
        j2 = ProductionJob("o2", "S2", 5, 6, 12.0)
        j3 = ProductionJob("o3", "S3", 15, 18, 36.0)
        q.enqueue(j1)
        q.enqueue(j2)
        q.enqueue(j3)
        result = q.list_all()
        assert result == [j1, j2, j3]

    def test_list_all_returns_empty_list_when_queue_empty(self):
        """list_all returns an empty list when the queue has no jobs."""
        q = ProductionQueue()
        assert q.list_all() == []

    def test_list_all_does_not_modify_queue(self):
        """list_all does not remove items from the queue."""
        q = ProductionQueue()
        job = ProductionJob("o1", "S1", 10, 12, 24.0)
        q.enqueue(job)
        q.list_all()
        assert q.is_empty() is False

    def test_multiple_enqueue_dequeue_cycle(self):
        """Queue handles multiple enqueue/dequeue cycles correctly."""
        q = ProductionQueue()
        j1 = ProductionJob("o1", "S1", 10, 12, 24.0)
        j2 = ProductionJob("o2", "S2", 5, 6, 12.0)
        q.enqueue(j1)
        first = q.dequeue()
        assert first is j1
        assert q.is_empty() is True
        q.enqueue(j2)
        assert q.is_empty() is False
        assert q.dequeue() is j2
