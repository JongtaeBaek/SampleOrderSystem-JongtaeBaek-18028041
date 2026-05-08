from model.sample import Sample
from repository.sample_repository import SampleRepository


class SampleController:
    def __init__(self, repo: SampleRepository) -> None:
        self._repo = repo

    def register(self, sample_id: str, name: str, avg_time: float, yield_rate: float) -> bool:
        samples = self._repo.load()
        if any(s.sample_id == sample_id for s in samples):
            print(f"오류: 이미 존재하는 시료 ID입니다 — {sample_id}")
            return False
        samples.append(Sample(sample_id=sample_id, name=name, avg_production_time=avg_time, yield_rate=yield_rate))
        self._repo.save(samples)
        return True

    def list_all(self) -> list[Sample]:
        return self._repo.load()

    def search(self, keyword: str) -> list[Sample]:
        return [s for s in self._repo.load() if keyword in s.name]
