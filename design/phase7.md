# Phase 7 Design — 출고 처리 (메뉴 6)

## 목표
CONFIRMED 상태 주문을 출고 처리(RELEASE)하고 재고를 차감하는 기능을 구현한다.

## 의존성
- Phase 1 완료 (model, repository)
- Phase 4 완료 (CONFIRMED 상태가 생성되는 경로)

## 산출물 파일

### `controller/release_controller.py`

```python
class ReleaseController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository) -> None
    def list_confirmed(self) -> list[Order]
    def release(self, order_id: str) -> bool
```

#### `__init__(order_repo, sample_repo)`
- `self._order_repo = order_repo`
- `self._sample_repo = sample_repo`

#### `list_confirmed() -> list[Order]`
- `orders = self._order_repo.load()`
- `return [o for o in orders if o.status == OrderStatus.CONFIRMED]`

#### `release(order_id) -> bool`
1. `orders = self._order_repo.load()`
2. `order = next((o for o in orders if o.order_id == order_id), None)`
3. `order` 없거나 `order.status != CONFIRMED`:
   - `f"오류: 출고 가능한 주문이 아닙니다 — {order_id}"` 출력
   - `False` 반환
4. `samples = self._sample_repo.load()`
5. `sample = next((s for s in samples if s.sample_id == order.sample_id), None)`
6. `sample.stock -= order.quantity`
7. `order.status = OrderStatus.RELEASE`
8. `self._sample_repo.save(samples)`
9. `self._order_repo.save(orders)`
10. `True` 반환

---

### `view/order_view.py` — 메서드 추가

기존 메서드 유지, 아래 추가.

```python
def show_confirmed_list(self, orders: list[Order]) -> None
def show_release_success(self, order_id: str) -> None
```

#### `show_confirmed_list(orders)`
- 빈 리스트 → `"출고 대기 중인 주문이 없습니다."` 출력
- 있으면 `show_order_list(orders)` 위임

#### `show_release_success(order_id)`
- `f"출고 완료: {order_id} → RELEASE"` 출력

## 데이터 흐름

```
OrderView.show_confirmed_list(release_controller.list_confirmed())
OrderView.prompt_order_id("출고")
    → order_id
    → ReleaseController.release(order_id)
        → OrderRepository.load()
        → CONFIRMED 검사
        → SampleRepository.load()
        → sample.stock -= order.quantity
        → order.status = RELEASE
        → SampleRepository.save()
        → OrderRepository.save()
    → True
→ OrderView.show_release_success(order_id)
```

## 테스트 전략

### `tests/test_controller_release.py`
`OrderRepository`, `SampleRepository` MagicMock.

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_list_confirmed` | CONFIRMED 만 반환 |
| `test_list_confirmed_empty` | CONFIRMED 없으면 [] |
| `test_release_success` | stock 차감, RELEASE 전환, samples+orders 저장, True |
| `test_release_stock_decreases_by_quantity` | stock -= quantity 정확한 값 |
| `test_release_not_found` | 없는 order_id, False, save 미호출 |
| `test_release_wrong_status_reserved` | RESERVED 주문, False |
| `test_release_wrong_status_producing` | PRODUCING 주문, False |

### `tests/test_view_order.py` — 메서드 추가

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_show_confirmed_list_empty` | "출고 대기 중인 주문이 없습니다." 출력 |
| `test_show_confirmed_list_with_orders` | show_order_list 위임 |
| `test_show_release_success` | "출고 완료: ... → RELEASE" 출력 |

## 주의사항
- `release` 에서 `sample.stock -= order.quantity` 는 재고가 충분하다는 전제 하에 실행 (CONFIRMED 는 이미 재고 확보된 상태 또는 생산 완료 상태).
- 재고 검증 로직 불필요 — PRD 에서 CONFIRMED 상태 주문은 이미 재고 확보가 보장됨.
- `release_controller.py` 는 이 Phase 에서 처음 생성.

---

## main.py 업데이트

Phase 7 완료 후 `main.py` 에 아래 내용을 추가한다.

**추가 import**:
```python
from controller.release_controller import ReleaseController
```

**새 핸들러 함수 추가**:
```python
def _handle_release_menu(ctrl: ReleaseController, view: OrderView) -> None:
    while True:
        print("\n=== 출고 처리 ===")
        print("1. 출고 대기 목록")
        print("2. 출고 처리")
        print("0. 돌아가기")
        choice = input("선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            view.show_confirmed_list(ctrl.list_confirmed())
        elif choice == "2":
            order_id = view.prompt_order_id("출고")
            if ctrl.release(order_id):
                view.show_release_success(order_id)
        else:
            print("잘못된 입력입니다. 다시 선택하세요.")
```

**`main()` 변경**:
- `release_ctrl = ReleaseController(order_repo, sample_repo)` 추가
- 메인 메뉴에 `print("6. 출고 처리")` 추가
- `elif choice == "6": _handle_release_menu(release_ctrl, order_view)` 추가

> **참고**: Phase 7 완료 시점에는 전체 메뉴(1~6, 0)가 모두 동작한다.  
> Phase 8 에서 MenuView 로 리팩토링하고, `_restore_queue` 로 ProductionQueue 복원 로직이 추가된다.
