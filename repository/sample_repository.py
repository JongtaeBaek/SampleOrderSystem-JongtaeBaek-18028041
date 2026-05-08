import json
import dataclasses
from pathlib import Path

from model.sample import Sample

_DEFAULT_PATH = Path("data/samples.json")


class SampleRepository:
    def __init__(self, path: Path = _DEFAULT_PATH) -> None:
        self._path = path

    def load(self) -> list[Sample]:
        if not self._path.exists():
            return []
        with self._path.open(encoding="utf-8") as f:
            records = json.load(f)
        return [Sample(**r) for r in records]

    def save(self, samples: list[Sample]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            json.dump([dataclasses.asdict(s) for s in samples], f, ensure_ascii=False, indent=2)
