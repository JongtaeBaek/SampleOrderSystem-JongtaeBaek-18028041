from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from model.order import OrderStatus
from model.production import ProductionQueue
from controller.sample_controller import SampleController
from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from view.sample_view import SampleView
from view.order_view import OrderView
from view.monitoring_view import MonitoringView

_W = 60


def _show_sub_menu(title: str, options: list[str]) -> None:
    print("\n" + "=" * _W)
    print(f"  [ {title} ]")
    print("-" * _W)
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print("  0. 돌아가기")
    print("=" * _W)


def _show_main_header(sample_repo: SampleRepository, order_repo: OrderRepository) -> None:
    samples = sample_repo.load()
    orders = order_repo.load()
    reserved  = sum(1 for o in orders if o.status == OrderStatus.RESERVED)
    producing = sum(1 for o in orders if o.status == OrderStatus.PRODUCING)
    confirmed = sum(1 for o in orders if o.status == OrderStatus.CONFIRMED)
    print("\n" + "=" * _W)
    print("  반도체 시료 생산 주문 관리 시스템")
    print("=" * _W)
    print(
        f"  시료: {len(samples)}종"
        f"  |  접수: {reserved}건"
        f"  |  생산중: {producing}건"
        f"  |  출고대기: {confirmed}건"
    )
    print("-" * _W)


def _handle_production_menu(ctrl: ProductionController, view: MonitoringView, production_queue: ProductionQueue) -> None:
    while True:
        _show_sub_menu("생산 라인 조회", ["생산 현황", "대기 주문 확인"])
        choice = input("  선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            job = ctrl.show_current(production_queue)
            view.show_production_current(job)
            if job is not None:
                confirm = input("  생산 완료 처리하시겠습니까? (y/n): ").strip()
                if confirm == "y":
                    if ctrl.complete(production_queue):
                        view.show_complete_success(job)
        elif choice == "2":
            view.show_production_queue(ctrl.list_queue(production_queue))
        else:
            print("  잘못된 입력입니다. 다시 선택하세요.")


def _handle_approval_menu(ctrl: OrderController, view: OrderView, production_queue: ProductionQueue) -> None:
    while True:
        _show_sub_menu("주문 승인/거절", ["접수된 주문 목록", "주문 승인", "주문 거절"])
        choice = input("  선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            view.show_reserved_list(ctrl.list_reserved())
        elif choice == "2":
            order_id = view.prompt_order_id("승인")
            ctrl.approve(order_id, production_queue)
        elif choice == "3":
            order_id = view.prompt_order_id("거절")
            ctrl.reject(order_id)
        else:
            print("  잘못된 입력입니다. 다시 선택하세요.")


def _handle_order_menu(ctrl: OrderController, view: OrderView) -> None:
    while True:
        _show_sub_menu("시료 주문", ["시료 예약"])
        choice = input("  선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            args = view.prompt_reserve()
            if ctrl.reserve(*args):
                view.show_reserve_success(args[0])
        else:
            print("  잘못된 입력입니다. 다시 선택하세요.")


def _handle_sample_menu(ctrl: SampleController, view: SampleView) -> None:
    while True:
        _show_sub_menu("시료 관리", ["시료 등록", "시료 조회", "시료 검색"])
        choice = input("  선택: ").strip()
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
            print("  잘못된 입력입니다. 다시 선택하세요.")


def main() -> None:
    sample_repo = SampleRepository()
    order_repo = OrderRepository()
    sample_ctrl = SampleController(sample_repo)
    sample_view = SampleView()
    order_ctrl = OrderController(order_repo, sample_repo)
    order_view = OrderView()
    production_queue = ProductionQueue()
    production_ctrl = ProductionController(order_repo, sample_repo)
    monitoring_view = MonitoringView()

    while True:
        _show_main_header(sample_repo, order_repo)
        print("  1. 시료 관리")
        print("  2. 시료 주문")
        print("  3. 주문 승인/거절")
        print("  5. 생산 라인 조회")
        print("  0. 종료")
        print("=" * _W)
        choice = input("  메뉴 선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            _handle_sample_menu(sample_ctrl, sample_view)
        elif choice == "2":
            _handle_order_menu(order_ctrl, order_view)
        elif choice == "3":
            _handle_approval_menu(order_ctrl, order_view, production_queue)
        elif choice == "5":
            _handle_production_menu(production_ctrl, monitoring_view, production_queue)
        else:
            print("  잘못된 입력입니다. 다시 선택하세요.")


if __name__ == "__main__":
    main()
