Phase $ARGUMENTS 의 소스 코드를 구현한다.

## 역할
SubAgent2 — 소스 코드 구현 (Code Implementer)

## 수행 절차

1. 아래 문서를 읽어 구현 범위를 파악한다.
   - `PLAN.md` — Phase $ARGUMENTS 산출물 목록 및 구현 상세
   - `PRD.md` — 해당 기능의 요구사항 상세
   - `CLAUDE.md` — 아키텍처 규칙 및 도메인 모델

2. 이미 구현된 이전 Phase 코드를 읽어 패턴과 스타일을 파악한다.

3. Phase $ARGUMENTS 의 산출물 파일을 모두 구현한다.

   **구현 규칙**
   - Model: 데이터 구조 정의만 (비즈니스 로직 없음)
   - View: 출력 및 입력 수집만 (데이터 가공 없음, print/input 직접 사용)
   - Controller: 비즈니스 로직 담당, Repository를 통해 데이터 접근
   - Repository: JSON 파일 읽기/쓰기만 담당
   - 의존 방향: View → Controller → Repository (역방향 금지)
   - 외부 라이브러리 사용 금지 (표준 라이브러리만)
   - `# pragma: no cover` 사용 금지
   - 코멘트는 WHY가 비명확한 경우에만 최소한으로 작성

4. 구현 완료 후 아래 형식으로 결과를 보고한다.

```
=== Step 2 코드 구현 완료 — Phase [N] ===

생성/수정된 파일:
  - [파일 경로]: [한 줄 설명]
  - ...

주요 구현 내용:
  - [클래스/함수명]: [역할 및 로직 요약]
  - ...

특이사항:
  - (설계 결정 사항이나 주의가 필요한 부분)
```
