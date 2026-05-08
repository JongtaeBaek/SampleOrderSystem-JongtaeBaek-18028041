1. 개발 과정
   1. PoC 개발
      1. MVC 스켈레톤 코드: Model/Controller/View 패키지 구조와 역할 분리 완성 ✅
         - git repository: https://github.com/JongtaeBaek/ConsoleMVC-JongtaeBaek-18028041.git
         - 완료 내용
           - model/: Sample, Order(OrderStatus), ProductionJob/ProductionQueue
           - view/: menu_view, sample_view, order_view, monitoring_view
           - controller/: sample, order, monitoring, production, release
           - main.py: 메뉴 라우팅 루프
           - 단위 테스트: 63개, 커버리지 100%
           - 개발 의존성: pytest, pytest-cov
      2. 데이터 영속성 처리: JSON(데이터 형식) 데이터를 저장/불러오는 구조 구현, 콘솔 시스템 포함 ✅
         - git repository: https://github.com/JongtaeBaek/DataPersistence-JongtaeBaek-18028041.git
         - 완료 내용
           - repository/: SampleRepository, OrderRepository (JSON load/save, pathlib 사용)
           - OrderStatus enum 직렬화/역직렬화 (저장: value 문자열, 로드: OrderStatus(value))
           - controller 업데이트: repo 주입 + 변경 후 save() 호출
           - main.py: 앱 시작 시 JSON 로드, PRODUCING 주문으로 ProductionQueue 재구성
           - 단위 테스트: 78개, 커버리지 100%
           - pytest.ini addopts: --cov-report=html 로 htmlcov/ 자동 산출
      3. 데이터 모니터링 Tool: 현재 저장된 데이터 상태를 콘솔에서 실시간 조회할 수 있는 관리자 도구 ✅
         - git repository: https://github.com/JongtaeBaek/DataMonitor-JongtaeBaek-18028041.git
         - 완료 내용
           - monitor/data_monitor.py: DataMonitor 클래스 (시료 현황/주문 현황/재고 현황/전체 조회)
           - model/, repository/: 1.1.2와 동일한 코드 이식 (read-only 운용)
           - main.py: 메뉴 루프 진입점 (standalone 툴)
           - 재고 상태 분류: 여유(stock >= 활성 주문량) / 부족(0 < stock < 활성 주문량) / 고갈(stock == 0)
           - 단위 테스트: 24개, 커버리지 100%
           - pytest.ini addopts: --cov-report=html 로 htmlcov/ 자동 산출
      4. Dummy 데이터 생성 Tool: Test를 위한 Dummy Data를 생성하는 도구, Dummy Data는 연결된 DB에 추가 ✅
         - git repository: https://github.com/JongtaeBaek/DummyDataGenerator-JongtaeBaek-18028041.git
         - 완료 내용
           - generator/dummy_generator.py: DummyGenerator 클래스 (generate_samples / generate_orders / reset)
           - 랜덤 시드(seed) 파라미터로 결정론적 생성 지원 (테스트 용이)
           - 시료/주문 기존 데이터에 추가(append) 방식, reset()으로 전체 초기화 후 재생성
           - model/, repository/: 1.1.2와 동일한 코드 이식
           - main.py: 메뉴 루프 진입점 (standalone 툴)
           - 단위 테스트: 24개, 커버리지 100%
           - pytest.ini addopts: --cov-report=html 로 htmlcov/ 자동 산출
   2. 프로젝트 개발
      - git repository: https://github.com/JongtaeBaek/SampleOrderSystem-JongtaeBaek-18028041.git
2. 개발 배경
여기가상의반도체회사"S-Semi" 가 있습니다.
이회사는다양한종류의반도체시료(Sample)를 생산하여연구소, 팹리스(Fabless) 업체, 대학 연구실 등의 고객에게
납품하고있습니다. 시료는주문이들어오면웨이퍼공정설비를통해제작되고, 검수를거쳐고객에게출고됩니다. 그런데최근들어주문량이급증하면서문제가생겼습니다.
"어, 이 주문 처리됐나요?"
"공정 예약을했는데, 언제완성되는지모르겠어요."
"이미 충분한시료재고가있는데, 왜추가공정이돌아가고있나요?“
엑셀과메모장으로주문을관리하다보니, 실수가잦고재고와공정현황을한눈에파악하기어려웠습1니다. 이러한이유로S-Semi에서는 더체계적인시료관리를위한"반도체시료생산주문관리시스템"을개발하기로결정
했습니다. 
3. 역할별 흐름도 
   - 고객(시료 요청자): 필요한 시료를 이메일로 주문 담당자에게 요청 
   - 주문 담당자(주문서 관리): 요청에 맞게 주문서 작성, 주문서를 생산 담당자에게 전달, 생산 담당자의 주문서에 대한 승인/거절에 따라 주문 관리 
   - 생산 담당자(시료 생산/승인): 개발 시료등록, 주문 수신 후 승인 또는 거절, 주문 담당자의 주문서를 바탕으로 시료 재고를 확인하고 재고가 부족하면 생산라인에 생산 요청, 재고가 있다면 승인 
4. 시스템 개요
   - 공장에서 시료 하나를 생산하는 설비 흐름
   - 하나의 생산 라인은 시료를 하나씩 생산
   - 주문이 들어온 시료에 대해서만 생산
   - 시스템은 콘솔 기반으로 동작
   - 담당자가 직접 명령을 입력, 시료를 등록하고 주문을 처리 
5. 주문 상태 흐름
   - 모든 주문은 아래 상태를 보유, REJECTED는 거절된 주문으로 정상 흐름 외의 상태이며 모니터링에서 제외
     - RESERVED: 주문 접수
     - REJECTED: 주문 거절
     - PRODUCING: 주문 승인 완료 및 재고 부족으로 생산 중
     - CONFIRMED: 주문 승인 완료 및 출고 대기 중
     - RELEASE: 출고 완료 
6. 메인 메뉴(콘솔 시스템)
   1. 시료 관리: 새로운 시료 등록, 목록 조회, 이름 검색 기능 시료(Sample는 이 시스템의 가장 기본이 되는 단위 
      - JSON파일로 관리 
      - 각 시료는 고유한 이름과 속성을 가지며, 시스템에 등록된 시료만 주문 가능 
      - 아래 메뉴를 가지게 됨 
        - 시료 등록: 새로운 시료를 시스템에 추가, 속성 값: 시료 ID, 이름, 평균 생산시간, 수율 
        - 시료 조회: 등록된 모든 시료 목록을 확인, 현재 재고 수량도 함께 표시 
        - 시료 검색: 이름 등 속성으로 특정 시료를 검색 
   2. 시료 주문 
      - 고객이 시료를 요청하면 주문 담당자가 주문을 생성
      - 아래 메뉴를 가지게 됨
        - 시료 예약 
          - 고객이 원하는 시료와 수량을 주문 
          - 이 시점에서 주문 상태는 RESERVED 
        - 예약시 입력 값 
          - 시료 ID 
          - 고객 명 
          - 주문 수량 
   3. 주문 승인/거절 
      - 점수된 주문(RESERVED 상태) 목록을 확인, 특정 주문에 대하여 승인 혹은 거절 
      - 아래 메뉴를 가지게 됨
        - 접수된 주문 목록 
          - RESERVED 상태의 주문 목록 Display
        - 주문 승인
          - 접수된 특정 주문에 대해 승인
            - 승인시 재고 생황에 따라 2가지 방식으로 자동처리
              - 재고가 충분한 경우: 주문을 즉시 CONFIRMED 상태로 전환
              - 재고가 부족한 경우: 생산 라인에 자동으로 등록, 주문 상태를 PRODUCING으로 전환
        - 주문 거절
          - 접수된 특정 주문에 대해 거절
          - 즉시 REJECTED 상태로 전환 
   4. 모니터링: 상태별 주문 수 및 시료별 재고 현황 확인
      - 주문에 따른 시료 재고에 대한 정보 모니터링 기능
      - 담당자가 현재 시스템 상태를 한눈에 파악할 수 있도록 구성
      - 아래 메뉴를 가지게 됨
        - 주문량 확인
          - 현재 상태별 (RESERVED/CONFIRMED/PRODUCING/RELEASE) 목록을 확인
          - REJECTED는 유효한 주문이 아니므로 무시
        - 재고량 확인
          - 각 시료별 현재 재고 수량을 확인
          - 주문대비 재고 수량에 따라 상태도 표기
            - 여유: 주문대비 재고 충분 상태
            - 부족: 주문대비 재고 수량 부족 상태
            - 고갈: 수량이 0인 상태
   5. 생산 라인 조회: 현재 생산 중인 시료 및 대기 중인 생산 큐 확인
      - 생산라인에 대한 정보를 display
      - 주문량에 대한 부족분을 생산하되, 수율 및 오차를 고려하여 시료를 생산
        - 실 생산량: ceil (부족분/(수율 *0.9))
        - 총 생산 시간: 평균 생산시간 * 실 생산량
        - 생산 완료시 주문상태 PRODUCING -> CONFIRMED로 변경
      - 아래 메뉴를 가지게 됨
        - 생산 현황 표기
          - 현재 생산중인 시료에 대한 정보 표기
          - 표기할 정보 수준은 주문 정보, 현재까지의 생산 량 등
        - 대기 주문 확인
          - 생산라인의 대기열인 생산 큐를 이용
          - 생산 작업을 대기하고 있는 목록을 출력
            - 스케쥴링 전략: FIFO(First In First Out)
   6. 출고처리
      - 재고가 충분해진 CONFIRMED 주문에 대하여 출고를 처리
      - 특정 주문에 대해 출고를 실행
      - 주문 상태가 RELEASE로 전환
