# Phase 3 Design — 시료 주문 (메뉴 2)

## 목표
주문 예약(RESERVED) 기능을 구현한다. OrderController 와 OrderView 를 처음 도입한다.

## 의존성
- Phase 1 완료 (`model/order.py`, `repository/order_repository.py`, `repository/sample_repository.py`)
- Phase 2 완료 (패턴 참조)

## 산출물 파일

### `view/order_view.py`

```python
class OrderView:
    def prompt_reserve(self) -> tuple[str, str, int]
    def show_order_list(self, orders: list[Order]) -> None
    def show_reserve_success(self, order_id: str) -> None
```

#### `prompt_reserve() -> tuple[str, str, int]`
- `input()` 순서: `시료 ID`, `고객명`, `주문 수량`
- 수량은 `int` 변환
- 반환: `(sample_id, customer_name, quantity)`

#### `show_order_list(orders)`
- 빈 리스트 → `"주문이 없습니다."` 출력 후 반환
- 비어 있지 않으면 헤더 + 구분선 + 행 출력
  - 컬럼: 주문ID, 시료ID, 고객명, 수량, 상태

#### `show_reserve_success(order_id)`
- `f"주문 예약 완료: {order_id}"` 출력

---

### `controller/order_controller.py`

```python
class OrderController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository) -> None
    def reserve(self, sample_id: str, customer_name: str, quantity: int) -> bool
```

#### `__init__(order_repo, sample_repo)`
- `self._order_repo = order_repo`
- `self._sample_repo = sample_repo`

#### `reserve(sample_id, customer_name, quantity) -> bool`
1. `self._sample_repo.load()` 로 시료 목록 조회
2. `sample_id` 존재 여부 검사: `any(s.sample_id == sample_id for s in samples)`
3. 없으면: `f"오류: 존재하지 않는 시료 ID입니다 — {sample_id}"` 출력, `False` 반환
4. 존재하면:
   - `order_id = str(uuid.uuid4())[:8]`
   - `Order(order_id, sample_id, customer_name, quantity, OrderStatus.RESERVED)` 생성
   - 기존 주문 목록에 추가 → `self._order_repo.save(orders)` → `True` 반환

## 데이터 흐름

```
OrderView.prompt_reserve()
    → (sample_id, customer_name, quantity)
    → OrderController.reserve(...)
        → SampleRepository.load()       # sample_id 존재 검사
        → OrderRepository.load()        # 기존 주문 로드
        → Order(status=RESERVED) 생성
        → OrderRepository.save()
    → OrderView.show_reserve_success() or 오류 메시지
```

## 테스트 전략

### `tests/test_view_order.py`
`builtins.input` mock + `capsys`.

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_prompt_reserve_returns_tuple` | input 3회, (str, str, int) 반환 |
| `test_show_order_list_empty` | "주문이 없습니다." 출력 |
| `test_show_order_list_with_orders` | 헤더+구분선+행 출력 |
| `test_show_reserve_success` | "주문 예약 완료: ..." 출력 |

### `tests/test_controller_order.py`
`OrderRepository`, `SampleRepository` 모두 `MagicMock`.

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_reserve_success` | sample 존재, order 저장, True 반환, status=RESERVED |
| `test_reserve_sample_not_found` | sample 없음, order_repo.save 미호출, False 반환, 오류 메시지 |
| `test_reserve_order_id_is_8_chars` | order_id 길이 8 검증 |

## 주의사항
- `uuid.uuid4()` 는 표준 라이브러리 `uuid` 모듈.
- `order_id = str(uuid.uuid4())[:8]` — 앞 8자리 슬라이싱.
- Controller 는 View 를 import 하지 않는다.
- Phase 4 에서 `list_reserved`, `approve`, `reject` 가 이 파일에 추가된다. 기존 `reserve` 로직 보존.

---

## main.py 업데이트

Phase 3 완료 후 `main.py` 에 아래 내용을 추가한다.

**추가 import**:
```python
from repository.order_repository import OrderRepository
from controller.order_controller import OrderController
from view.order_view import OrderView
```

**새 핸들러 함수 추가**:
```python
def _handle_order_menu(ctrl: OrderController, view: OrderView) -> None:
    while True:
        print("\n=== 시료 주문 ===")
        print("1. 시료 예약")
        print("0. 돌아가기")
        choice = input("선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            args = view.prompt_reserve()
            if ctrl.reserve(*args):
                view.show_reserve_success(args[0])
        else:
            print("잘못된 입력입니다. 다시 선택하세요.")
```

**`main()` 변경**:
- `SampleRepository()` 를 `sample_repo = SampleRepository()` 로 분리 (이후 Phase 에서 공유)
- `order_repo = OrderRepository()` 추가
- `order_ctrl = OrderController(order_repo, sample_repo)` 추가
- `order_view = OrderView()` 추가
- `SampleController(sample_repo)` 로 변경
- 메인 메뉴에 `print("2. 시료 주문")` 추가
- `elif choice == "2": _handle_order_menu(order_ctrl, order_view)` 추가
