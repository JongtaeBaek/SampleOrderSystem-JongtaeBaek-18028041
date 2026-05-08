# Phase 2 Design — 시료 관리 (메뉴 1)

## 목표
시료 등록 / 조회 / 검색 기능을 구현한다. View 와 Controller 계층을 처음 도입하는 Phase 이다.

## 의존성
- Phase 1 완료 (`model/sample.py`, `repository/sample_repository.py`)

## 산출물 파일

### `view/sample_view.py`

```python
class SampleView:
    def prompt_register(self) -> tuple[str, str, float, float]
    def prompt_search_keyword(self) -> str
    def show_sample_list(self, samples: list[Sample]) -> None
    def show_search_result(self, samples: list[Sample]) -> None
    def show_register_success(self, sample_id: str) -> None
```

#### `prompt_register() -> tuple[str, str, float, float]`
- 순서대로 `input()` 호출: `시료 ID`, `이름`, `평균 생산시간(시간)`, `수율(0.0~1.0)`
- 반환: `(sample_id, name, avg_time, yield_rate)` — avg_time, yield_rate 는 `float` 변환

#### `prompt_search_keyword() -> str`
- `input("검색 키워드(이름 부분 일치): ")` 반환

#### `show_sample_list(samples)`
- `samples` 가 빈 리스트 → `"등록된 시료가 없습니다."` 출력 후 반환
- 비어 있지 않으면 헤더 + 구분선 + 행 테이블 출력
  - 컬럼: ID, 이름, 평균생산시간, 수율, 재고

#### `show_search_result(samples)`
- `samples` 가 빈 리스트 → `"검색 결과가 없습니다."` 출력 후 반환
- 비어 있지 않으면 `show_sample_list(samples)` 위임

#### `show_register_success(sample_id)`
- `f"시료 등록 완료: {sample_id}"` 출력

---

### `controller/sample_controller.py`

```python
class SampleController:
    def __init__(self, repo: SampleRepository) -> None
    def register(self, sample_id: str, name: str, avg_time: float, yield_rate: float) -> bool
    def list_all(self) -> list[Sample]
    def search(self, keyword: str) -> list[Sample]
```

#### `__init__(repo)`
- `self._repo = repo` — SampleRepository 주입

#### `register(sample_id, name, avg_time, yield_rate) -> bool`
1. `self._repo.load()` 로 기존 시료 목록 조회
2. `sample_id` 중복 검사: `any(s.sample_id == sample_id for s in samples)`
3. 중복 시: `f"오류: 이미 존재하는 시료 ID입니다 — {sample_id}"` 출력, `False` 반환
4. 정상: `Sample(...)` 생성 후 목록에 추가 → `self._repo.save(samples)` → `True` 반환

#### `list_all() -> list[Sample]`
- `return self._repo.load()`

#### `search(keyword) -> list[Sample]`
- `return [s for s in self._repo.load() if keyword in s.name]`

## 데이터 흐름

```
SampleView.prompt_register()
    → (sample_id, name, avg_time, yield_rate)
    → SampleController.register(...)
        → SampleRepository.load()
        → 중복 검사
        → SampleRepository.save()
    → SampleView.show_register_success() or 오류 메시지
```

## 테스트 전략

### `tests/test_view_sample.py`
`builtins.input` mock + `capsys` 사용.

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_prompt_register_returns_tuple` | input 4회 호출, 반환값 타입 검증 |
| `test_prompt_search_keyword` | input 1회 호출, 반환값 검증 |
| `test_show_sample_list_empty` | "등록된 시료가 없습니다." 출력 |
| `test_show_sample_list_with_samples` | 헤더+구분선+데이터 행 출력 |
| `test_show_search_result_empty` | "검색 결과가 없습니다." 출력 |
| `test_show_search_result_with_results` | show_sample_list 위임 → 헤더 포함 출력 |
| `test_show_register_success` | "시료 등록 완료: ..." 출력 |

### `tests/test_controller_sample.py`
`SampleRepository` 를 `MagicMock` 으로 교체.

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_register_success` | load→append→save 호출 순서, True 반환 |
| `test_register_duplicate_id` | 중복 시 save 미호출, False 반환, 오류 메시지 출력 |
| `test_list_all` | repo.load() 결과 그대로 반환 |
| `test_search_found` | keyword 포함 항목만 반환 |
| `test_search_not_found` | 일치 없을 때 빈 리스트 반환 |

## 주의사항
- Controller 는 View 를 import 하지 않는다 (단방향 의존성).
- `register` 의 오류 메시지 출력은 Controller 에서 직접 `print` — View 의존 없이.
- `search` 는 대소문자 구분 있음 (PRD 에 별도 명시 없으므로 단순 `in` 연산).

---

## main.py 연동

`main.py` 는 Phase 2 부터 실행 가능한 파일로 유지된다. Phase 2~7 은 MenuView 없이 직접  
`print()` / `input()` 으로 메뉴를 출력하고, Phase 8 에서 MenuView 로 리팩토링된다.

**Phase 2 이후 main.py 전체 내용**:

```python
from repository.sample_repository import SampleRepository
from controller.sample_controller import SampleController
from view.sample_view import SampleView


def _handle_sample_menu(ctrl: SampleController, view: SampleView) -> None:
    while True:
        print("\n=== 시료 관리 ===")
        print("1. 시료 등록")
        print("2. 시료 조회")
        print("3. 시료 검색")
        print("0. 돌아가기")
        choice = input("선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            args = view.prompt_register()
            if ctrl.register(*args):
                view.show_register_success(args[0])
        elif choice == "2":
            view.show_sample_list(ctrl.list_all())
        elif choice == "3":
            kw = view.prompt_search_keyword()
            view.show_search_result(ctrl.search(kw))
        else:
            print("잘못된 입력입니다. 다시 선택하세요.")


def main() -> None:
    sample_ctrl = SampleController(SampleRepository())
    sample_view = SampleView()

    while True:
        print("\n=== 반도체 시료 생산 주문 관리 시스템 ===")
        print("1. 시료 관리")
        print("0. 종료")
        choice = input("메뉴 선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            _handle_sample_menu(sample_ctrl, sample_view)
        else:
            print("잘못된 입력입니다. 다시 선택하세요.")


if __name__ == "__main__":
    main()
```

**커버리지 주의**: Phase 2~7 에서 `main.py` 는 pytest 커버리지 측정 대상에서 제외한다.  
루트 디렉터리의 `.coveragerc` 에 `[run] omit = main.py` 가 설정된다.  
Phase 8 에서 이 omit 설정을 제거하고 `test_main.py` 로 커버리지 100% 를 달성한다.
