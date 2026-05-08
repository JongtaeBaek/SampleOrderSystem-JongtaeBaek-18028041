# Phase 5 Design — 생산 라인 조회 (메뉴 5)

## 목표
생산 현황 조회, 생산 완료 처리, 대기 주문 목록 조회 기능을 구현한다.
`ProductionQueue` 를 조작하는 첫 번째 Phase 이다.

## 의존성
- Phase 1 완료 (`model/production.py`, `repository/`)
- Phase 4 완료 (`ProductionJob` 이 큐에 들어오는 경로 완성)

## 산출물 파일

### `controller/production_controller.py`

```python
class ProductionController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository) -> None
    def show_current(self, production_queue: ProductionQueue) -> ProductionJob | None
    def complete(self, production_queue: ProductionQueue) -> bool
    def list_queue(self, production_queue: ProductionQueue) -> list[ProductionJob]
```

#### `__init__(order_repo, sample_repo)`
- `self._order_repo = order_repo`
- `self._sample_repo = sample_repo`

#### `show_current(production_queue) -> ProductionJob | None`
- `return production_queue.peek()`
- 빈 큐이면 `None` 반환

#### `complete(production_queue) -> bool`
1. `production_queue.is_empty()` → `True` 이면 오류 메시지 출력, `False` 반환
   - 메시지: `"생산 중인 작업이 없습니다."`
2. `job = production_queue.dequeue()`
3. `samples = self._sample_repo.load()`
4. `sample = next((s for s in samples if s.sample_id == job.sample_id), None)`
5. `sample.stock += job.actual_production`
6. `self._sample_repo.save(samples)`
7. `orders = self._order_repo.load()`
8. `order = next((o for o in orders if o.order_id == job.order_id), None)`
9. `order.status = OrderStatus.CONFIRMED`
10. `self._order_repo.save(orders)`
11. `True` 반환

#### `list_queue(production_queue) -> list[ProductionJob]`
- `return production_queue.list_all()`

---

### `view/monitoring_view.py` — 생산 현황 부분

```python
class MonitoringView:
    def show_production_current(self, job: ProductionJob | None) -> None
    def show_production_queue(self, jobs: list[ProductionJob]) -> None
    def show_complete_success(self, job: ProductionJob) -> None
```

#### `show_production_current(job)`
- `job` 이 `None` → `"현재 생산 중인 작업이 없습니다."` 출력
- 있으면 주문ID, 시료ID, 필요수량, 실생산량, 총생산시간 출력

#### `show_production_queue(jobs)`
- 빈 리스트 → `"대기 중인 생산 작업이 없습니다."` 출력
- 있으면 순서(#1, #2 …) + 주문ID, 시료ID, 필요수량 출력

#### `show_complete_success(job)`
- `f"생산 완료: 주문 {job.order_id} — {job.actual_production}개 생산"` 출력

## 데이터 흐름 — 생산 완료

```
ProductionController.complete(production_queue)
    → production_queue.dequeue()         # job 꺼냄
    → SampleRepository.load()
    → sample.stock += job.actual_production
    → SampleRepository.save()
    → OrderRepository.load()
    → order.status = CONFIRMED
    → OrderRepository.save()
    → True
```

## 테스트 전략

### `tests/test_controller_production.py`
`OrderRepository`, `SampleRepository` MagicMock, 실제 `ProductionQueue` 인스턴스 사용.

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_show_current_empty_queue` | None 반환 |
| `test_show_current_with_job` | peek 결과 반환 |
| `test_complete_empty_queue` | False, 오류 메시지, dequeue 미호출 |
| `test_complete_success` | dequeue 1회, stock 증가, CONFIRMED, samples+orders 저장, True |
| `test_complete_stock_increases_by_actual_production` | stock += actual_production 정확한 값 검증 |
| `test_list_queue_empty` | [] 반환 |
| `test_list_queue_with_jobs` | list_all() 결과 반환 |

### `tests/test_view_monitoring.py` — 생산 현황 부분

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_show_production_current_none` | "현재 생산 중인 작업이 없습니다." 출력 |
| `test_show_production_current_with_job` | 주문ID, 시료ID 등 필드 출력 |
| `test_show_production_queue_empty` | "대기 중인 생산 작업이 없습니다." 출력 |
| `test_show_production_queue_with_jobs` | 순서 번호 + 각 job 정보 출력 |
| `test_show_complete_success` | "생산 완료: ..." 출력 |

## 주의사항
- `complete` 는 `dequeue` 전에 반드시 `is_empty` 로 선검사한다.
- Phase 6 에서 `MonitoringView` 에 주문량/재고량 메서드가 추가된다. 기존 메서드 보존.
- `view/monitoring_view.py` 는 이 Phase 에서 처음 생성한다.

---

## main.py 업데이트

Phase 5 완료 후 `main.py` 에 아래 내용을 추가한다.

**추가 import**:
```python
from controller.production_controller import ProductionController
from view.monitoring_view import MonitoringView
```

**새 핸들러 함수 추가**:
```python
def _handle_production_menu(ctrl: ProductionController, view: MonitoringView, production_queue: ProductionQueue) -> None:
    while True:
        _show_sub_menu("생산 라인 조회", ["생산 현황", "대기 주문 확인"])
        choice = input("  선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            job = ctrl.show_current(production_queue)
            view.show_production_current(job)
            if job is not None:
                confirm = input("  생산 완료 처리하시겠습니까? (y/n): ").strip()
                if confirm == "y":
                    if ctrl.complete(production_queue):
                        view.show_complete_success(job)
        elif choice == "2":
            view.show_production_queue(ctrl.list_queue(production_queue))
        else:
            print("  잘못된 입력입니다. 다시 선택하세요.")
```

**`main()` 변경**:
- `production_ctrl = ProductionController(order_repo, sample_repo)` 추가
- `monitoring_view = MonitoringView()` 추가
- 메인 메뉴에 `print("5. 생산 라인 조회")` 추가 (메뉴 4 는 Phase 6 에서 추가됨)
- `elif choice == "5": _handle_production_menu(production_ctrl, monitoring_view, production_queue)` 추가

> **참고**: Phase 5 완료 시점에는 메인 메뉴가 1, 2, 3, 5 순서로 표시된다 (4 는 Phase 6 에서 추가).  
> Phase 8 에서 MenuView 로 최종 순서(1~6)로 정렬된다.
