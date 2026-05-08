Phase $ARGUMENTS 의 문서 정합성을 검증한다.

## 역할
SubAgent1 — 문서 정합성 검증 (Doc Validator)

## 수행 절차

1. 아래 3개 문서를 전부 읽는다.
   - `CLAUDE.md`
   - `PLAN.md`
   - `PRD.md`

2. Phase $ARGUMENTS 의 요구사항이 세 문서 간 일관성이 있는지 검사한다.

   **검사 항목**
   - [ ] PLAN.md Phase $ARGUMENTS 의 산출물 목록이 명확히 정의되어 있는가
   - [ ] PLAN.md Phase $ARGUMENTS 의 테스트 범위가 명확히 정의되어 있는가
   - [ ] PLAN.md Phase $ARGUMENTS 의 완료 조건이 명확히 정의되어 있는가
   - [ ] CLAUDE.md 의 아키텍처 설명이 Phase $ARGUMENTS 산출물과 충돌하지 않는가
   - [ ] PRD.md 의 기능 요구사항 중 Phase $ARGUMENTS 에서 구현할 항목이 누락 없이 PLAN.md 에 반영되어 있는가
   - [ ] PLAN.md Phase $ARGUMENTS 의 의존 Phase 가 완료(✅) 상태인지 확인

3. 결과를 아래 형식으로 출력한다.

```
=== Step 1 문서 정합성 검증 — Phase [N] ===

검사 항목:
  [PASS/FAIL] PLAN.md 산출물 목록 명확성
  [PASS/FAIL] PLAN.md 테스트 범위 명확성
  [PASS/FAIL] PLAN.md 완료 조건 명확성
  [PASS/FAIL] CLAUDE.md 아키텍처 충돌 없음
  [PASS/FAIL] PRD.md 요구사항 반영 완전성
  [PASS/FAIL] 의존 Phase 완료 여부

최종 결과: PASS / FAIL

FAIL 항목 상세:
  - (FAIL 항목이 있는 경우 구체적인 문제와 수정 방향 기술)
```

4. FAIL 항목이 있을 경우 해당 문서를 직접 수정하고 재검사를 수행한다.
   - 수정 후 최종 결과가 PASS 가 되면 종료한다.
   - CLAUDE.md 또는 PLAN.md 수정 시 변경 내용을 명시한다.
