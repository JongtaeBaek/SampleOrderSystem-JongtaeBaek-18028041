# Phase 1 Design — Model + Repository

## 목표
도메인 모델 데이터클래스와 JSON 영속성 레이어를 완성한다.
이후 모든 Phase의 기반이 되는 계층이므로 필드명·타입·직렬화 규칙이 정확해야 한다.

## 의존성
없음 (첫 번째 Phase)

## 산출물 파일

### `model/__init__.py`
빈 패키지 마커.

---

### `model/sample.py`

```python
from dataclasses import dataclass, field

@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float   # 단위: 시간
    yield_rate: float            # 범위: 0.0 ~ 1.0
    stock: int = field(default=0)
```

- `dataclasses.asdict(sample)` 로 직렬화 가능해야 한다.
- `stock` 기본값은 `0`.

---

### `model/order.py`

```python
from dataclasses import dataclass
from enum import Enum

class OrderStatus(Enum):
    RESERVED  = "RESERVED"
    CONFIRMED = "CONFIRMED"
    PRODUCING = "PRODUCING"
    RELEASE   = "RELEASE"
    REJECTED  = "REJECTED"

@dataclass
class Order:
    order_id: str        # uuid4 앞 8자리
    sample_id: str
    customer_name: str
    quantity: int
    status: OrderStatus
```

- `OrderStatus(value)` 로 문자열에서 복원 가능해야 한다.
- `OrderStatus.value` 로 문자열 직렬화.

---

### `model/production.py`

```python
_YIELD_SAFETY_FACTOR = 0.9   # 수율 안전 계수 (도메인 상수)

@dataclass
class ProductionJob:
    order_id: str
    sample_id: str
    required_quantity: int    # 부족분 = quantity - stock
    actual_production: int    # ceil(required / (yield_rate * 0.9))
    total_time: float         # avg_production_time * actual_production

    @staticmethod
    def create(order_id, sample_id, required_quantity, yield_rate, avg_production_time) -> "ProductionJob":
        actual_production = math.ceil(required_quantity / (yield_rate * _YIELD_SAFETY_FACTOR))
        total_time = avg_production_time * actual_production
        return ProductionJob(order_id, sample_id, required_quantity, actual_production, total_time)

class ProductionQueue:
    def __init__(self) -> None          # deque 초기화
    def enqueue(self, job) -> None      # 큐 끝에 추가
    def dequeue(self) -> ProductionJob  # 큐 앞에서 제거 후 반환
    def peek(self) -> ProductionJob | None   # 제거 없이 첫 번째 반환 (빈 큐 → None)
    def is_empty(self) -> bool
    def list_all(self) -> list[ProductionJob]   # 순서 유지, 비파괴
```

- `dequeue` 는 빈 큐에서 호출하지 않는 것이 호출자 책임 (Controller 가 `is_empty` 로 선검사).
- `_YIELD_SAFETY_FACTOR` 는 모듈 상수로 외부에서 변경 불가.

---

### `repository/__init__.py`
빈 패키지 마커.

---

### `repository/sample_repository.py`

```python
class SampleRepository:
    def __init__(self, path: Path = Path("data/samples.json")) -> None
    def load(self) -> list[Sample]   # 파일 없으면 [] 반환
    def save(self, samples: list[Sample]) -> None  # parent 디렉터리 자동 생성
```

- `load`: `json.load` → `[Sample(**r) for r in records]`
- `save`: `dataclasses.asdict` → `json.dump(ensure_ascii=False, indent=2)`
- 파일이 없으면 `[]` 반환 (최초 실행 대응).

---

### `repository/order_repository.py`

```python
class OrderRepository:
    def __init__(self, path: Path = Path("data/orders.json")) -> None
    def load(self) -> list[Order]
    def save(self, orders: list[Order]) -> None
```

- `load`: `status` 필드 → `OrderStatus(r["status"])` 로 복원.
- `save`: `{**dataclasses.asdict(order), "status": order.status.value}` 로 직렬화.

---

### `pytest.ini`

```ini
[pytest]
testpaths = tests
pythonpath = .
addopts = --cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=100
```

## 테스트 전략

| 파일 | 핵심 케이스 |
|------|------------|
| `test_model_sample.py` | 기본 생성, stock 기본값 0, asdict 직렬화 |
| `test_model_order.py` | OrderStatus 5종 값 존재, 문자열→Enum 복원, Order 생성 |
| `test_model_production.py` | `create()` 공식 검증, FIFO 순서, peek 비제거, 빈 큐 None |
| `test_repository_sample.py` | 파일 없음→[], 저장→로드 왕복, 디렉터리 자동 생성, 한글 보존 |
| `test_repository_order.py` | status 직렬화/역직렬화 5종, 왕복, 파일 없음→[] |

## 주의사항
- `ProductionJob.create()` 의 `math.ceil` 은 표준 라이브러리 `math` 모듈 사용.
- Model 에 if/else 비즈니스 판단 로직 없음. `create()` 는 순수 계산 팩토리.
- `OrderStatus` 는 `Enum` 이므로 `OrderStatus("RESERVED")` 로 복원 가능.
