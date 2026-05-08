# PRD.md — 반도체 시료 생산 주문 관리 시스템

## 1. 배경 및 목적

가상의 반도체 회사 "S-Semi"는 다양한 반도체 시료(Sample)를 생산하여 연구소, 팹리스 업체, 대학 연구실 등에 납품한다. 주문량 급증 이후 엑셀/메모장 기반 관리의 한계가 드러나 체계적인 시료 생산 주문 관리 시스템이 필요해졌다.

**핵심 문제**
- 주문 처리 여부를 파악하기 어려움
- 공정 완료 시점을 예측할 수 없음
- 재고가 충분함에도 불필요한 생산이 발생

## 2. 사용자 역할

| 역할 | 책임 |
|------|------|
| 주문 담당자 | 주문서 작성, 주문 상태 관리 |
| 생산 담당자 | 시료 등록, 주문 승인/거절, 생산 지시 및 출고 처리 |

> 이 시스템은 단일 콘솔 인터페이스로 두 역할을 모두 지원한다.

## 3. 도메인 모델

### Sample (시료)
| 필드 | 타입 | 설명 |
|------|------|------|
| sample_id | str | 고유 ID (수동 입력) |
| name | str | 시료 이름 |
| avg_production_time | float | 평균 생산시간 (단위: 시간) |
| yield_rate | float | 수율 (0.0 ~ 1.0) |
| stock | int | 현재 재고 수량 (기본값 0) |

### Order (주문)
| 필드 | 타입 | 설명 |
|------|------|------|
| order_id | str | uuid4 앞 8자리 자동 생성 |
| sample_id | str | 주문 대상 시료 ID |
| customer_name | str | 고객명 |
| quantity | int | 주문 수량 |
| status | OrderStatus | 주문 상태 |

### OrderStatus (주문 상태 흐름)
```
[접수]
RESERVED
    │
    ├── (재고 충분: stock >= quantity) ──────────→ CONFIRMED ──→ RELEASE
    │                                                               (출고)
    ├── (재고 부족: stock < quantity)  ──→ PRODUCING ──→ CONFIRMED ──→ RELEASE
    │                                      (생산 완료)
    └── (거절) ──→ REJECTED
```
- `REJECTED`는 모니터링 집계에서 제외

### ProductionJob (생산 작업)
| 필드 | 설명 |
|------|------|
| order_id | 연결된 주문 ID |
| sample_id | 생산할 시료 ID |
| required_quantity | 부족분 (= quantity - stock) |
| actual_production | 실 생산량 = `ceil(부족분 / (yield_rate × 0.9))` |
| total_time | 총 생산 시간 = `avg_production_time × actual_production` |

### ProductionQueue
- FIFO 방식 (`collections.deque`)
- 하나의 생산 라인이 시료를 하나씩 순차 처리
- 앱 재시작 시 `PRODUCING` 상태 주문으로 자동 복원

## 4. 기능 요구사항

### 메뉴 1 — 시료 관리

#### 1-1. 시료 등록
- 입력: sample_id, 이름, 평균 생산시간, 수율
- 중복 ID 입력 시 오류 메시지 출력 후 취소
- 등록 즉시 `samples.json` 저장

#### 1-2. 시료 조회
- 등록된 전체 시료 목록 출력 (재고 수량 포함)
- 시료 없을 경우 안내 메시지 출력

#### 1-3. 시료 검색
- 이름(부분 일치)으로 검색
- 검색 결과 없을 경우 안내 메시지 출력

---

### 메뉴 2 — 시료 주문

#### 2-1. 시료 예약
- 입력: sample_id, 고객명, 주문 수량
- 존재하지 않는 sample_id 입력 시 오류 메시지 출력 후 취소
- 생성된 주문 상태: `RESERVED`
- 등록 즉시 `orders.json` 저장

---

### 메뉴 3 — 주문 승인/거절

#### 3-1. 접수된 주문 목록
- `RESERVED` 상태 주문 목록 출력

#### 3-2. 주문 승인
- 입력: order_id
- `RESERVED` 아닌 주문 ID 입력 시 오류 메시지 출력 후 취소
- 재고 분기 처리:
  - `stock >= quantity`: 상태 → `CONFIRMED`, `stock -= quantity`
  - `stock < quantity`: `ProductionJob` 생성 → 큐 enqueue, 상태 → `PRODUCING`
- samples + orders 즉시 저장

#### 3-3. 주문 거절
- 입력: order_id
- `RESERVED` 아닌 주문 ID 입력 시 오류 메시지 출력 후 취소
- 상태 → `REJECTED`, 즉시 저장

---

### 메뉴 4 — 모니터링

#### 4-1. 주문량 확인
- 상태별 주문 건수 출력: `RESERVED` / `PRODUCING` / `CONFIRMED` / `RELEASE`
- `REJECTED` 제외

#### 4-2. 재고량 확인
- 시료별 재고 수량 및 상태 출력
  - **여유**: stock > 0 이고 stock ≥ 활성 주문 수량 합계 (RESERVED + PRODUCING)
  - **부족**: stock > 0 이고 stock < 활성 주문 수량 합계
  - **고갈**: stock == 0

---

### 메뉴 5 — 생산 라인 조회

#### 5-1. 생산 현황
- 큐의 첫 번째 작업(현재 생산 중) 정보 출력
- 생산 완료(complete) 실행 시: `stock += actual_production`, 상태 `PRODUCING → CONFIRMED`
- 큐가 비어 있을 경우 안내 메시지

#### 5-2. 대기 주문 확인
- 큐 전체 목록 출력 (FIFO 순서)
- 큐가 비어 있을 경우 안내 메시지

---

### 메뉴 6 — 출고 처리

- `CONFIRMED` 상태 주문 목록 출력
- 입력: order_id
- `CONFIRMED` 아닌 주문 ID 입력 시 오류 메시지 출력 후 취소
- `stock -= quantity`, 상태 → `RELEASE`
- samples + orders 즉시 저장

## 5. 비기능 요구사항

| 항목 | 내용 |
|------|------|
| 플랫폼 | 콘솔 기반 (Python 3.14) |
| 의존성 | 표준 라이브러리만 사용 (외부 패키지 금지) |
| 영속성 | JSON 파일 (`data/samples.json`, `data/orders.json`) |
| 테스트 | pytest + pytest-cov, 커버리지 100% |
| 인코딩 | UTF-8 |
