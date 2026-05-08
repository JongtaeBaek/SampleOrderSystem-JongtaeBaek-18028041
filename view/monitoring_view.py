from model.production import ProductionJob


class MonitoringView:
    def show_production_current(self, job: ProductionJob | None) -> None:
        if job is None:
            print("현재 생산 중인 작업이 없습니다.")
            return
        print(f"  주문 ID      : {job.order_id}")
        print(f"  시료 ID      : {job.sample_id}")
        print(f"  필요 수량    : {job.required_quantity}")
        print(f"  실생산량     : {job.actual_production}")
        print(f"  총 생산시간  : {job.total_time:.1f}시간")

    def show_production_queue(self, jobs: list[ProductionJob]) -> None:
        if not jobs:
            print("대기 중인 생산 작업이 없습니다.")
            return
        for i, job in enumerate(jobs, 1):
            print(f"  #{i}  주문ID: {job.order_id}  시료ID: {job.sample_id}  필요수량: {job.required_quantity}")

    def show_complete_success(self, job: ProductionJob) -> None:
        print(f"생산 완료: 주문 {job.order_id} — {job.actual_production}개 생산")

    def show_order_summary(self, summary: dict[str, int]) -> None:
        print("=== 주문량 현황 ===")
        print(f"RESERVED  : {summary.get('RESERVED', 0):3d}건")
        print(f"PRODUCING : {summary.get('PRODUCING', 0):3d}건")
        print(f"CONFIRMED : {summary.get('CONFIRMED', 0):3d}건")
        print(f"RELEASE   : {summary.get('RELEASE', 0):3d}건")

    def show_stock_summary(self, summaries: list[dict]) -> None:
        if not summaries:
            print("등록된 시료가 없습니다.")
            return
        header = f"{'시료ID':<12}{'이름':<16}{'재고':>6}{'활성주문량':>10}{'상태':>6}"
        print(header)
        print("-" * len(header))
        for s in summaries:
            print(
                f"{s['sample_id']:<12}{s['name']:<16}{s['stock']:>6}{s['active_quantity']:>10}{s['stock_status']:>6}"
            )
