Phase $ARGUMENTS 의 구현 코드가 PRD 요구사항과 MVC 아키텍처 원칙을 준수하는지 검증한다.

## 역할
SubAgent5 — 준수성 검증 (Compliance Verifier)

## 수행 절차

1. 아래 문서를 읽는다.
   - `PRD.md` — 기능 요구사항
   - `CLAUDE.md` — 아키텍처 원칙 및 도메인 모델
   - `PLAN.md` Phase $ARGUMENTS — 완료 조건

2. Phase $ARGUMENTS 에서 구현된 소스 파일을 전부 읽는다.

3. 아래 항목을 검사한다.

   **PRD 요구사항 준수**
   - [ ] Phase $ARGUMENTS 범위의 모든 기능 요구사항이 구현되었는가
   - [ ] 입력값 유효성 검사 (존재하지 않는 ID, 잘못된 상태 등) 가 구현되었는가
   - [ ] 오류 시 예외를 발생시키지 않고 메시지 출력 후 취소 처리를 하는가
   - [ ] 데이터 변경 직후 즉시 save() 가 호출되는가

   **MVC 아키텍처 준수**
   - [ ] Model 파일에 비즈니스 로직(if/else 판단)이 없는가
   - [ ] View 파일에 데이터 가공 로직이 없는가 (print/input 만 담당하는가)
   - [ ] Controller 가 View 를 import 하지 않는가 (단방향 의존성)
   - [ ] Repository 가 JSON 읽기/쓰기만 담당하는가

   **코드 품질**
   - [ ] `# pragma: no cover` 가 사용되지 않았는가
   - [ ] 외부 라이브러리 import 가 없는가 (표준 라이브러리만)
   - [ ] 도메인 모델 필드명이 CLAUDE.md 와 일치하는가
   - [ ] OrderStatus 직렬화 규칙이 준수되었는가 (저장: .value, 로드: OrderStatus(value))

4. 결과를 아래 형식으로 보고한다.

```
=== Step 5 준수성 검증 — Phase [N] ===

PRD 요구사항 준수:
  [PASS/FAIL] 기능 요구사항 완전 구현
  [PASS/FAIL] 입력값 유효성 검사
  [PASS/FAIL] 오류 처리 방식 (예외 없이 메시지 출력)
  [PASS/FAIL] 즉시 save() 호출

MVC 아키텍처 준수:
  [PASS/FAIL] Model 에 비즈니스 로직 없음
  [PASS/FAIL] View 에 데이터 가공 없음
  [PASS/FAIL] Controller → View 역방향 의존 없음
  [PASS/FAIL] Repository 단일 책임

코드 품질:
  [PASS/FAIL] pragma: no cover 미사용
  [PASS/FAIL] 표준 라이브러리만 사용
  [PASS/FAIL] 도메인 모델 필드명 일치
  [PASS/FAIL] OrderStatus 직렬화 규칙 준수

최종 결과: PASS / FAIL

FAIL 항목 상세:
  - (FAIL 항목이 있는 경우 파일명, 라인 번호, 구체적인 문제 기술)
```

5. FAIL 항목이 있을 경우 직접 코드를 수정하고 재검사한다.
   - 수정 후 최종 결과가 PASS 가 되면 종료한다.
