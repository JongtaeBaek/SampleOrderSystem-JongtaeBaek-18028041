Phase $ARGUMENTS 의 테스트 코드를 작성한다.

## 역할
SubAgent3 — 테스트 코드 작성 (Test Writer)

## 수행 절차

1. Phase $ARGUMENTS 에서 구현된 소스 파일을 전부 읽는다.
2. `PLAN.md` Phase $ARGUMENTS 의 테스트 범위를 확인한다.
3. `pytest.ini` 가 없으면 아래 내용으로 생성한다.
   ```ini
   [pytest]
   testpaths = tests
   pythonpath = .
   addopts = --cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=100
   ```

4. `tests/` 디렉터리에 테스트 파일을 작성한다.

   **테스트 작성 규칙**
   - 커버리지 100% 달성이 목표 (`# pragma: no cover` 사용 금지)
   - Model 테스트: 필드 초기화, Enum 값, 메서드 직접 호출
   - View 테스트: `patch("builtins.input")` mock, `capsys` 로 출력 검증
   - Controller 테스트: Repository를 `MagicMock` 으로 교체하여 상태 변화 검증
   - Repository 테스트: `tmp_path` fixture 로 실제 파일 I/O 검증
   - main.py 테스트: `monkeypatch.chdir(tmp_path)`, `runpy.run_path` 로 `__main__` 블록 커버
   - 모든 분기(if/else)를 반드시 커버하는 테스트 케이스 작성
   - 경계값(빈 리스트, 없는 ID 입력 등) 케이스 포함

5. 작성 완료 후 아래 형식으로 결과를 보고한다.

```
=== Step 3 테스트 작성 완료 — Phase [N] ===

생성/수정된 테스트 파일:
  - [파일 경로]: [테스트 케이스 수]개

테스트 케이스 목록:
  [파일명]
    - test_xxx: [테스트 내용]
    - ...

커버리지 예상 대상:
  - [소스 파일]: 예상 커버리지 라인 수
```
