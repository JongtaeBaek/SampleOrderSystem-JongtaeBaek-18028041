# Phase 4 Design — 주문 승인/거절 (메뉴 3)

## 목표
RESERVED 주문에 대한 재고 분기 승인 로직과 거절 기능을 구현한다.
재고가 충분하면 즉시 CONFIRMED, 부족하면 ProductionJob 을 생성해 큐에 등록하고 PRODUCING 으로 전환한다.

## 의존성
- Phase 1 완료 (model, repository 전체)
- Phase 3 완료 (`controller/order_controller.py` — `reserve` 메서드 이미 존재)

## 산출물 파일

### `controller/order_controller.py` — 메서드 추가

기존 `reserve` 메서드를 유지하고 아래 3개 메서드를 추가한다.

```python
def list_reserved(self) -> list[Order]
def approve(self, order_id: str, production_queue: ProductionQueue) -> bool
def reject(self, order_id: str) -> bool
```

#### `list_reserved() -> list[Order]`
- `self._order_repo.load()` 후 `status == OrderStatus.RESERVED` 필터링하여 반환

#### `approve(order_id, production_queue) -> bool`
1. `self._order_repo.load()` 로 주문 목록 조회
2. `order_id` 로 주문 탐색: `next((o for o in orders if o.order_id == order_id), None)`
3. 주문이 없거나 `status != RESERVED` 이면: 오류 메시지 출력, `False` 반환
   - 메시지: `f"오류: 승인 가능한 주문이 아닙니다 — {order_id}"`
4. `self._sample_repo.load()` 로 시료 조회
5. `sample = next((s for s in samples if s.sample_id == order.sample_id), None)`
6. **재고 충분** (`sample.stock >= order.quantity`):
   - `sample.stock -= order.quantity`
   - `order.status = OrderStatus.CONFIRMED`
   - `self._sample_repo.save(samples)`, `self._order_repo.save(orders)`
   - `True` 반환
7. **재고 부족** (`sample.stock < order.quantity`):
   - `shortage = order.quantity - sample.stock`
   - `job = ProductionJob.create(order.order_id, order.sample_id, shortage, sample.yield_rate, sample.avg_production_time)`
   - `production_queue.enqueue(job)`
   - `order.status = OrderStatus.PRODUCING`
   - `self._order_repo.save(orders)`
   - `True` 반환
   - **주의**: 재고 부족 시 stock 차감 없음, samples 저장 없음

#### `reject(order_id) -> bool`
1. `self._order_repo.load()` 로 주문 목록 조회
2. `order_id` 로 주문 탐색
3. 없거나 `status != RESERVED` → 오류 메시지 출력, `False` 반환
   - 메시지: `f"오류: 거절 가능한 주문이 아닙니다 — {order_id}"`
4. `order.status = OrderStatus.REJECTED`
5. `self._order_repo.save(orders)`, `True` 반환

---

### `view/order_view.py` — 메서드 추가

기존 메서드 유지, 아래 추가.

```python
def prompt_order_id(self, action: str) -> str
def show_reserved_list(self, orders: list[Order]) -> None
def show_approve_success(self, order_id: str, status: OrderStatus) -> None
def show_reject_success(self, order_id: str) -> None
```

#### `prompt_order_id(action) -> str`
- `input(f"{action}할 주문 ID: ").strip()` 반환
- `action` 예: `"승인"`, `"거절"`

#### `show_reserved_list(orders)`
- 빈 리스트 → `"접수된 주문이 없습니다."` 출력 후 반환
- 비어 있지 않으면 `show_order_list(orders)` 위임

#### `show_approve_success(order_id, status)`
- `f"승인 완료: {order_id} → {status.value}"` 출력
- `status` 는 승인 후의 상태 (CONFIRMED 또는 PRODUCING)

#### `show_reject_success(order_id)`
- `f"거절 완료: {order_id} → REJECTED"` 출력

## 데이터 흐름 — 승인 (재고 충분)

```
OrderView.prompt_order_id("승인")
    → order_id
    → OrderController.approve(order_id, production_queue)
        → OrderRepository.load()
        → RESERVED 검사
        → SampleRepository.load()
        → stock >= quantity 분기
        → sample.stock -= quantity
        → order.status = CONFIRMED
        → SampleRepository.save()
        → OrderRepository.save()
    → True
```

## 데이터 흐름 — 승인 (재고 부족)

```
OrderController.approve(order_id, production_queue)
    → stock < quantity 분기
    → shortage = quantity - stock
    → ProductionJob.create(...)
    → production_queue.enqueue(job)
    → order.status = PRODUCING
    → OrderRepository.save()   ← samples 저장 없음
    → True
```

## 테스트 전략

### `tests/test_controller_order.py` — 메서드 추가

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_list_reserved` | RESERVED 만 필터링 반환 |
| `test_approve_sufficient_stock` | stock 차감, CONFIRMED, samples+orders 저장 |
| `test_approve_insufficient_stock` | shortage 계산, job enqueue, PRODUCING, orders 저장, samples 저장 없음 |
| `test_approve_not_found` | 없는 order_id, False, save 미호출 |
| `test_approve_wrong_status` | CONFIRMED 주문에 approve, False, save 미호출 |
| `test_reject_success` | REJECTED 전환, orders 저장, True |
| `test_reject_not_found` | 없는 order_id, False |
| `test_reject_wrong_status` | PRODUCING 주문에 reject, False |

### `tests/test_view_order.py` — 메서드 추가

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_prompt_order_id` | input 1회, 반환값 검증 |
| `test_show_reserved_list_empty` | "접수된 주문이 없습니다." 출력 |
| `test_show_reserved_list_with_orders` | show_order_list 위임 |
| `test_show_approve_success_confirmed` | "... → CONFIRMED" 출력 |
| `test_show_approve_success_producing` | "... → PRODUCING" 출력 |
| `test_show_reject_success` | "... → REJECTED" 출력 |

## 주의사항
- 재고 부족 승인 시 `sample.stock` 은 변경하지 않는다. 생산 완료 후 Phase 5 에서 처리.
- `ProductionJob.create()` import: `from model.production import ProductionJob, ProductionQueue`
- Phase 3 테스트(`test_controller_order.py`)의 기존 `reserve` 테스트가 깨지지 않아야 한다.

---

## main.py 업데이트

Phase 4 완료 후 `main.py` 에 아래 내용을 추가한다.

**추가 import**:
```python
from model.production import ProductionQueue
```

**새 핸들러 함수 추가**:
```python
def _handle_approval_menu(ctrl: OrderController, view: OrderView, production_queue: ProductionQueue) -> None:
    while True:
        _show_sub_menu("주문 승인/거절", ["접수된 주문 목록", "주문 승인", "주문 거절"])
        choice = input("  선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            view.show_reserved_list(ctrl.list_reserved())
        elif choice == "2":
            order_id = view.prompt_order_id("승인")
            ctrl.approve(order_id, production_queue)
        elif choice == "3":
            order_id = view.prompt_order_id("거절")
            ctrl.reject(order_id)
        else:
            print("  잘못된 입력입니다. 다시 선택하세요.")
```

**`main()` 변경**:
- `production_queue = ProductionQueue()` 추가 (앱 재시작 시 복원은 Phase 8 에서 `_restore_queue` 로 처리)
- 메인 메뉴에 `print("3. 주문 승인/거절")` 추가
- `elif choice == "3": _handle_approval_menu(order_ctrl, order_view, production_queue)` 추가
