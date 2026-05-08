# Phase 6 Design — 모니터링 (메뉴 4)

## 목표
상태별 주문 건수와 시료별 재고 현황(여유/부족/고갈)을 조회하는 모니터링 기능을 구현한다.

## 의존성
- Phase 1 완료 (model, repository)
- Phase 5 완료 (`view/monitoring_view.py` 이미 존재)

## 산출물 파일

### `controller/monitoring_controller.py`

```python
class MonitoringController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository) -> None
    def order_summary(self) -> dict[str, int]
    def stock_summary(self) -> list[dict]
```

#### `__init__(order_repo, sample_repo)`
- `self._order_repo = order_repo`
- `self._sample_repo = sample_repo`

#### `order_summary() -> dict[str, int]`
1. `orders = self._order_repo.load()`
2. REJECTED 제외한 4개 상태의 건수 집계
3. 반환 형식:
   ```python
   {
       "RESERVED":  int,
       "PRODUCING": int,
       "CONFIRMED": int,
       "RELEASE":   int,
   }
   ```
4. 해당 상태 주문이 없어도 키는 포함, 값은 `0`

구현 예:
```python
target = [OrderStatus.RESERVED, OrderStatus.PRODUCING, OrderStatus.CONFIRMED, OrderStatus.RELEASE]
return {s.value: sum(1 for o in orders if o.status == s) for s in target}
```

#### `stock_summary() -> list[dict]`
1. `samples = self._sample_repo.load()`
2. `orders = self._order_repo.load()`
3. 각 sample 에 대해:
   - `active_quantity = sum(o.quantity for o in orders if o.sample_id == s.sample_id and o.status in (OrderStatus.RESERVED, OrderStatus.PRODUCING))`
   - 재고 상태 판별:
     - `stock == 0` → `"고갈"`
     - `0 < stock < active_quantity` → `"부족"`
     - 그 외 → `"여유"`
4. 반환: `list[dict]` — 각 dict 는 아래 키 포함
   ```python
   {
       "sample_id": str,
       "name": str,
       "stock": int,
       "active_quantity": int,
       "stock_status": str,   # "여유" | "부족" | "고갈"
   }
   ```

---

### `view/monitoring_view.py` — 메서드 추가

기존 생산 현황 메서드 유지, 아래 추가.

```python
def show_order_summary(self, summary: dict[str, int]) -> None
def show_stock_summary(self, summaries: list[dict]) -> None
```

#### `show_order_summary(summary)`
- 4개 상태(RESERVED, PRODUCING, CONFIRMED, RELEASE) 건수 출력
- 형식 예:
  ```
  === 주문량 현황 ===
  RESERVED  :  N건
  PRODUCING :  N건
  CONFIRMED :  N건
  RELEASE   :  N건
  ```

#### `show_stock_summary(summaries)`
- 빈 리스트 → `"등록된 시료가 없습니다."` 출력
- 있으면 헤더 + 구분선 + 행 출력
  - 컬럼: 시료ID, 이름, 재고, 활성주문량, 상태

## 데이터 흐름 — 재고량 확인

```
MonitoringController.stock_summary()
    → SampleRepository.load()
    → OrderRepository.load()
    → 각 sample 에 대해 RESERVED+PRODUCING 주문량 합산
    → 상태 판별 (고갈/부족/여유)
    → list[dict] 반환
→ MonitoringView.show_stock_summary(summaries)
```

## 테스트 전략

### `tests/test_controller_monitoring.py`
`OrderRepository`, `SampleRepository` MagicMock.

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_order_summary_all_statuses` | 4개 키 존재, 각 건수 정확 |
| `test_order_summary_excludes_rejected` | REJECTED 키 없음 |
| `test_order_summary_empty_orders` | 4개 키 모두 0 |
| `test_stock_summary_surplus` | stock >= active_quantity → "여유" |
| `test_stock_summary_shortage` | 0 < stock < active_quantity → "부족" |
| `test_stock_summary_depleted` | stock == 0 → "고갈" |
| `test_stock_summary_no_active_orders` | active_quantity=0, stock>0 → "여유" |
| `test_stock_summary_empty_samples` | [] 반환 |

### `tests/test_view_monitoring.py` — 메서드 추가

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_show_order_summary` | 4개 상태 건수 출력 검증 |
| `test_show_stock_summary_empty` | "등록된 시료가 없습니다." 출력 |
| `test_show_stock_summary_with_data` | 헤더+행 출력, 상태 문자열 포함 |

## 주의사항
- `stock_summary` 의 `active_quantity` 는 `RESERVED` + `PRODUCING` 만 집계. `CONFIRMED`, `RELEASE` 제외.
- `stock == 0` 이 최우선 판별 조건 ("고갈" 을 먼저 체크). `active_quantity == 0` 이어도 `stock == 0` 이면 "고갈".
- `order_summary` 결과 dict 의 키는 `OrderStatus.value` 문자열 (`"RESERVED"` 등).

---

## main.py 업데이트

Phase 6 완료 후 `main.py` 에 아래 내용을 추가한다.

**추가 import**:
```python
from controller.monitoring_controller import MonitoringController
```

**새 핸들러 함수 추가**:
```python
def _handle_monitoring_menu(ctrl: MonitoringController, view: MonitoringView) -> None:
    while True:
        _show_sub_menu("모니터링", ["주문량 확인", "재고량 확인"])
        choice = input("  선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            view.show_order_summary(ctrl.order_summary())
        elif choice == "2":
            view.show_stock_summary(ctrl.stock_summary())
        else:
            print("  잘못된 입력입니다. 다시 선택하세요.")
```

**`main()` 변경**:
- `monitoring_ctrl = MonitoringController(order_repo, sample_repo)` 추가
- 메인 메뉴에 `print("4. 모니터링")` 추가 (5 앞에 삽입)
- `elif choice == "4": _handle_monitoring_menu(monitoring_ctrl, monitoring_view)` 추가

> **참고**: Phase 6 완료 시점에는 메인 메뉴가 1, 2, 3, 4, 5 순서로 표시된다 (6 은 Phase 7 에서 추가).
