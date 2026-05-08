# Phase 8 Design — 통합 완성 (main.py + MenuView)

## 목표
전체 메뉴 루프를 통합하고 앱 시작 시 ProductionQueue 를 자동 복원한다.
모든 Controller, View 를 연결하는 최종 Phase 이다.

## 의존성
- Phase 1~7 전체 완료

## 산출물 파일

### `view/menu_view.py`

```python
class MenuView:
    def show_main_menu(self, n_samples: int, reserved: int, producing: int, confirmed: int) -> None
    def prompt_main_choice(self) -> str
    def show_sub_menu(self, title: str, options: list[str]) -> None
    def prompt_sub_choice(self) -> str
    def show_invalid_choice(self) -> None
```

#### `show_main_menu(n_samples, reserved, producing, confirmed)`
Phase 2~7 의 `_show_main_header` + 메인 메뉴 항목 출력을 하나로 통합.  
대시보드(현황 요약) + 메뉴 항목(1~6, 0) 을 아래 형식으로 출력:
```
============================================================
  반도체 시료 생산 주문 관리 시스템
============================================================
  시료: N종  |  접수: N건  |  생산중: N건  |  출고대기: N건
------------------------------------------------------------
  1. 시료 관리
  2. 시료 주문
  3. 주문 승인/거절
  4. 모니터링
  5. 생산 라인 조회
  6. 출고 처리
  0. 종료
============================================================
```
- `_W = 60` 상수 사용 (`"=" * 60`, `"-" * 60`)

#### `prompt_main_choice() -> str`
- `input("  메뉴 선택: ").strip()` 반환

#### `show_sub_menu(title, options)`
Phase 2~7 의 `_show_sub_menu(title, options)` 와 동일한 출력 형식:
```
============================================================
  [ title ]
------------------------------------------------------------
  1. option1
  2. option2
  0. 돌아가기
============================================================
```
- `_W = 60` 사용

#### `prompt_sub_choice() -> str`
- `input("  선택: ").strip()` 반환

#### `show_invalid_choice()`
- `"  잘못된 입력입니다. 다시 선택하세요."` 출력

---

### `main.py`

```python
def _restore_queue(orders: list[Order], samples: list[Sample]) -> ProductionQueue
def main() -> None

if __name__ == "__main__":
    main()
```

#### `_restore_queue(orders, samples) -> ProductionQueue`
앱 재시작 시 PRODUCING 상태 주문으로 ProductionQueue 재구성.

```
queue = ProductionQueue()
for order in orders where order.status == PRODUCING:
    sample = next(s for s in samples if s.sample_id == order.sample_id)
    shortage = order.quantity - sample.stock
    if shortage <= 0:
        shortage = 1   # 안전값 (정상 흐름에서 발생하지 않음)
    job = ProductionJob.create(order.order_id, order.sample_id, shortage,
                               sample.yield_rate, sample.avg_production_time)
    queue.enqueue(job)
return queue
```

**주의**: `shortage` 는 항상 양수여야 한다. 정상 흐름에서 PRODUCING 상태는 재고 부족이 보장되므로 `order.quantity > sample.stock` 이다.

#### `main() -> None`
전체 흐름:

```python
def main():
    sample_repo = SampleRepository()
    order_repo = OrderRepository()

    samples = sample_repo.load()
    orders = order_repo.load()
    production_queue = _restore_queue(orders, samples)

    sample_ctrl = SampleController(sample_repo)
    order_ctrl = OrderController(order_repo, sample_repo)
    production_ctrl = ProductionController(order_repo, sample_repo)
    monitoring_ctrl = MonitoringController(order_repo, sample_repo)
    release_ctrl = ReleaseController(order_repo, sample_repo)

    menu_view = MenuView()
    sample_view = SampleView()
    order_view = OrderView()
    monitoring_view = MonitoringView()

    while True:
        orders = order_repo.load()
        menu_view.show_main_menu(
            n_samples=len(sample_repo.load()),
            reserved=sum(1 for o in orders if o.status == OrderStatus.RESERVED),
            producing=sum(1 for o in orders if o.status == OrderStatus.PRODUCING),
            confirmed=sum(1 for o in orders if o.status == OrderStatus.CONFIRMED),
        )
        choice = menu_view.prompt_main_choice()

        if choice == "0":
            break
        elif choice == "1":
            _handle_sample_menu(sample_ctrl, sample_view, menu_view)
        elif choice == "2":
            _handle_order_menu(order_ctrl, order_view, menu_view)
        elif choice == "3":
            _handle_approval_menu(order_ctrl, order_view, menu_view, production_queue)
        elif choice == "4":
            _handle_monitoring_menu(monitoring_ctrl, monitoring_view, menu_view)
        elif choice == "5":
            _handle_production_menu(production_ctrl, monitoring_view, menu_view, production_queue)
        elif choice == "6":
            _handle_release_menu(release_ctrl, order_view, menu_view)
        else:
            menu_view.show_invalid_choice()
```

#### 서브메뉴 핸들러 함수

```python
def _handle_sample_menu(ctrl, view, menu_view):
    # 서브메뉴: 1.시료등록 / 2.시료조회 / 3.시료검색 / 0.돌아가기
    while True:
        menu_view.show_sub_menu("시료 관리", ["시료 등록", "시료 조회", "시료 검색"])
        c = menu_view.prompt_sub_choice()
        if c == "0": break
        elif c == "1":
            args = view.prompt_register()
            if ctrl.register(*args):
                view.show_register_success(args[0])
        elif c == "2":
            view.show_sample_list(ctrl.list_all())
        elif c == "3":
            kw = view.prompt_search_keyword()
            view.show_search_result(ctrl.search(kw))
        else:
            menu_view.show_invalid_choice()

def _handle_order_menu(ctrl, view, menu_view):
    # 서브메뉴: 1.시료예약 / 0.돌아가기
    while True:
        menu_view.show_sub_menu("시료 주문", ["시료 예약"])
        c = menu_view.prompt_sub_choice()
        if c == "0": break
        elif c == "1":
            args = view.prompt_reserve()
            if ctrl.reserve(*args):
                view.show_reserve_success(args[0])  # order_id 는 ctrl 내부 생성, 메시지 단순화
        else:
            menu_view.show_invalid_choice()

def _handle_approval_menu(ctrl, view, menu_view, production_queue):
    # 서브메뉴: 1.접수된주문목록 / 2.주문승인 / 3.주문거절 / 0.돌아가기
    while True:
        menu_view.show_sub_menu("주문 승인/거절", ["접수된 주문 목록", "주문 승인", "주문 거절"])
        c = menu_view.prompt_sub_choice()
        if c == "0": break
        elif c == "1":
            view.show_reserved_list(ctrl.list_reserved())
        elif c == "2":
            order_id = view.prompt_order_id("승인")
            ctrl.approve(order_id, production_queue)
        elif c == "3":
            order_id = view.prompt_order_id("거절")
            ctrl.reject(order_id)
        else:
            menu_view.show_invalid_choice()

def _handle_monitoring_menu(ctrl, view, menu_view):
    # 서브메뉴: 1.주문량확인 / 2.재고량확인 / 0.돌아가기
    ...

def _handle_production_menu(ctrl, view, menu_view, production_queue):
    # 서브메뉴: 1.생산현황 / 2.대기주문확인 / 0.돌아가기
    # 생산현황: job 보여주고 "생산 완료 처리?" 입력 받아 complete() 호출
    ...

def _handle_release_menu(ctrl, order_view, menu_view):
    # 서브메뉴: 1.출고대기목록 / 2.출고처리 / 0.돌아가기
    ...
```

## 테스트 전략

### `tests/test_view_menu.py`

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_show_main_menu` | 메뉴 항목 0~6 + 대시보드(시료/접수/생산중/출고대기 수) 출력 |
| `test_prompt_main_choice` | input 1회, 반환값 검증 |
| `test_show_sub_menu` | title, options, "0. 돌아가기" 출력 |
| `test_prompt_sub_choice` | input 1회, 반환값 검증 |
| `test_show_invalid_choice` | 오류 메시지 출력 |

### `tests/test_main.py`
`monkeypatch.chdir(tmp_path)` + `runpy.run_module("__main__")` 또는 `runpy.run_path("main.py")`.

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_restore_queue_empty` | PRODUCING 주문 없음 → 빈 큐 |
| `test_restore_queue_with_producing` | PRODUCING 주문 1개 → 큐에 job 1개 |
| `test_main_menu_0_exits` | input side_effect=["0"] → 정상 종료 |
| `test_main_menu_1_sample` | "1","0","0" → 시료관리 진입 후 돌아오기 |
| `test_main_menu_2_order` | "2","0","0" → 주문 진입 후 돌아오기 |
| `test_main_menu_3_approval` | "3","0","0" → 승인 진입 후 돌아오기 |
| `test_main_menu_4_monitoring` | "4","0","0" → 모니터링 진입 후 돌아오기 |
| `test_main_menu_5_production` | "5","0","0" → 생산 진입 후 돌아오기 |
| `test_main_menu_6_release` | "6","0","0" → 출고 진입 후 돌아오기 |
| `test_main_menu_invalid` | "9","0" → show_invalid_choice 호출 |
| `test_main_restores_queue_on_start` | tmp_path 에 PRODUCING 주문 JSON 사전 생성 → 큐 복원 확인 |

## 주의사항
- `main.py` 의 `if __name__ == "__main__":` 블록은 `runpy` 로만 커버 가능.
- `_restore_queue` 는 `main.py` 내 private 함수 — 테스트에서 직접 import 가능 (`from main import _restore_queue`).
- 서브메뉴 핸들러는 `main.py` 내 private 함수로 정의 (`_handle_*`). 테스트는 `main()` 전체 흐름으로 커버.
- 모든 서브메뉴 핸들러는 `"0"` 입력 시 루프 탈출 → 메인 메뉴로 복귀.
- `tmp_path` fixture 와 `monkeypatch.chdir` 으로 `data/` 디렉터리가 tmp_path 아래에 생성되도록 격리.
- **`.coveragerc` 수정 필수**: Phase 2~7 에서 루트의 `.coveragerc` 에 `[run] omit = main.py` 가 설정되어 있다.  
  Phase 8 Step 2(코드 구현) 에서 반드시 이 omit 설정을 `.coveragerc` 에서 제거해야 한다.  
  제거 후 `test_main.py` 가 `main.py` 전체 커버리지를 달성해야 한다.
- Phase 8 의 `main()` 은 Phase 2~7 에서 점진적으로 추가된 `_handle_*` 핸들러를 MenuView 를 사용하도록 리팩토링한다.  
  각 핸들러의 직접 `print`/`input` 호출을 `menu_view.show_sub_menu()` / `menu_view.prompt_sub_choice()` 로 교체한다.
