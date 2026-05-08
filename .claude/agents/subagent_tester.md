Phase $ARGUMENTS 의 테스트를 실행하고 결과를 검증한다.

## 역할
SubAgent4 — 테스트 실행 및 커버리지 검증 (Tester)

## 수행 절차

1. `.venv` 가 존재하는지 확인한다. 없으면 생성 후 pytest, pytest-cov 를 설치한다.
   ```
   python -m venv .venv
   .venv\Scripts\pip install pytest pytest-cov
   ```

2. `.venv\Scripts\pytest` 를 실행한다.

3. 실행 결과를 분석한다.

   **PASS 조건**
   - 모든 테스트 케이스 통과 (0 failed)
   - 전체 커버리지 100% (`Required test coverage of 100% reached`)

4. 결과를 아래 형식으로 보고한다.

```
=== Step 4 테스트 검증 — Phase [N] ===

실행 결과:
  총 테스트: N개
  통과: N개 / 실패: N개

커버리지:
  전체: N%
  미달 파일: (있을 경우 파일명과 미커버 라인)

최종 결과: PASS / FAIL
```

5. FAIL 인 경우:
   - 실패한 테스트의 에러 메시지를 분석한다.
   - 소스 코드 버그인 경우 → 소스 코드를 수정한다.
   - 테스트 코드 오류인 경우 → 테스트 코드를 수정한다.
   - 커버리지 미달인 경우 → 누락된 분기를 커버하는 테스트를 추가한다.
   - 수정 후 pytest 를 재실행하여 PASS 가 될 때까지 반복한다.
