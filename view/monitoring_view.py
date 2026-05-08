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
