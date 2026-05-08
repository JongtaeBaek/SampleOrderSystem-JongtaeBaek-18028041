from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from model.order import Order, OrderStatus
from model.production import ProductionJob, ProductionQueue
from controller.sample_controller import SampleController
from controller.order_controller import OrderController
from controller.monitoring_controller import MonitoringController
from controller.production_controller import ProductionController
from controller.release_controller import ReleaseController
from view.menu_view import MenuView
from view.sample_view import SampleView
from view.order_view import OrderView
from view.monitoring_view import MonitoringView


def _restore_queue(orders: list[Order], samples: list) -> ProductionQueue:
    queue = ProductionQueue()
    for order in orders:
        if order.status == OrderStatus.PRODUCING:
            sample = next(s for s in samples if s.sample_id == order.sample_id)
            shortage = order.quantity - sample.stock
            if shortage <= 0:
                shortage = 1
            job = ProductionJob.create(
                order.order_id,
                order.sample_id,
                shortage,
                sample.yield_rate,
                sample.avg_production_time,
            )
            queue.enqueue(job)
    return queue


def _handle_sample_menu(ctrl: SampleController, view: SampleView, menu_view: MenuView) -> None:
    while True:
        menu_view.show_sub_menu("시료 관리", ["시료 등록", "시료 조회", "시료 검색"])
        c = menu_view.prompt_sub_choice()
        if c == "0":
            break
        elif c == "1":
            args = view.prompt_register()
            if ctrl.register(*args):
                view.show_register_success(args[0])
        elif c == "2":
            view.show_sample_list(ctrl.list_all())
        elif c == "3":
            kw = view.prompt_search_keyword()
            view.show_search_result(ctrl.search(kw))
        else:
            menu_view.show_invalid_choice()


def _handle_order_menu(ctrl: OrderController, view: OrderView, menu_view: MenuView) -> None:
    while True:
        menu_view.show_sub_menu("시료 주문", ["시료 예약"])
        c = menu_view.prompt_sub_choice()
        if c == "0":
            break
        elif c == "1":
            args = view.prompt_reserve()
            if ctrl.reserve(*args):
                view.show_reserve_success(args[0])
        else:
            menu_view.show_invalid_choice()


def _handle_approval_menu(
    ctrl: OrderController,
    view: OrderView,
    menu_view: MenuView,
    production_queue: ProductionQueue,
) -> None:
    while True:
        menu_view.show_sub_menu("주문 승인/거절", ["접수된 주문 목록", "주문 승인", "주문 거절"])
        c = menu_view.prompt_sub_choice()
        if c == "0":
            break
        elif c == "1":
            view.show_reserved_list(ctrl.list_reserved())
        elif c == "2":
            order_id = view.prompt_order_id("승인")
            ctrl.approve(order_id, production_queue)
        elif c == "3":
            order_id = view.prompt_order_id("거절")
            ctrl.reject(order_id)
        else:
            menu_view.show_invalid_choice()


def _handle_monitoring_menu(
    ctrl: MonitoringController,
    view: MonitoringView,
    menu_view: MenuView,
) -> None:
    while True:
        menu_view.show_sub_menu("모니터링", ["주문량 확인", "재고량 확인"])
        c = menu_view.prompt_sub_choice()
        if c == "0":
            break
        elif c == "1":
            view.show_order_summary(ctrl.order_summary())
        elif c == "2":
            view.show_stock_summary(ctrl.stock_summary())
        else:
            menu_view.show_invalid_choice()


def _handle_production_menu(
    ctrl: ProductionController,
    view: MonitoringView,
    menu_view: MenuView,
    production_queue: ProductionQueue,
) -> None:
    while True:
        menu_view.show_sub_menu("생산 라인 조회", ["생산 현황", "대기 주문 확인"])
        c = menu_view.prompt_sub_choice()
        if c == "0":
            break
        elif c == "1":
            job = ctrl.show_current(production_queue)
            view.show_production_current(job)
            if job is not None:
                confirm = input("  생산 완료 처리하시겠습니까? (y/n): ").strip()
                if confirm == "y":
                    if ctrl.complete(production_queue):
                        view.show_complete_success(job)
        elif c == "2":
            view.show_production_queue(ctrl.list_queue(production_queue))
        else:
            menu_view.show_invalid_choice()


def _handle_release_menu(
    ctrl: ReleaseController,
    order_view: OrderView,
    menu_view: MenuView,
) -> None:
    while True:
        menu_view.show_sub_menu("출고 처리", ["출고 대기 목록", "출고 처리"])
        c = menu_view.prompt_sub_choice()
        if c == "0":
            break
        elif c == "1":
            order_view.show_confirmed_list(ctrl.list_confirmed())
        elif c == "2":
            order_id = order_view.prompt_order_id("출고")
            if ctrl.release(order_id):
                order_view.show_release_success(order_id)
        else:
            menu_view.show_invalid_choice()


def main() -> None:
    sample_repo = SampleRepository()
    order_repo = OrderRepository()
    samples = sample_repo.load()
    orders = order_repo.load()
    production_queue = _restore_queue(orders, samples)

    sample_ctrl = SampleController(sample_repo)
    order_ctrl = OrderController(order_repo, sample_repo)
    production_ctrl = ProductionController(order_repo, sample_repo)
    monitoring_ctrl = MonitoringController(order_repo, sample_repo)
    release_ctrl = ReleaseController(order_repo, sample_repo)

    menu_view = MenuView()
    sample_view = SampleView()
    order_view = OrderView()
    monitoring_view = MonitoringView()

    while True:
        orders = order_repo.load()
        menu_view.show_main_menu(
            n_samples=len(sample_repo.load()),
            reserved=sum(1 for o in orders if o.status == OrderStatus.RESERVED),
            producing=sum(1 for o in orders if o.status == OrderStatus.PRODUCING),
            confirmed=sum(1 for o in orders if o.status == OrderStatus.CONFIRMED),
        )
        choice = menu_view.prompt_main_choice()

        if choice == "0":
            break
        elif choice == "1":
            _handle_sample_menu(sample_ctrl, sample_view, menu_view)
        elif choice == "2":
            _handle_order_menu(order_ctrl, order_view, menu_view)
        elif choice == "3":
            _handle_approval_menu(order_ctrl, order_view, menu_view, production_queue)
        elif choice == "4":
            _handle_monitoring_menu(monitoring_ctrl, monitoring_view, menu_view)
        elif choice == "5":
            _handle_production_menu(production_ctrl, monitoring_view, menu_view, production_queue)
        elif choice == "6":
            _handle_release_menu(release_ctrl, order_view, menu_view)
        else:
            menu_view.show_invalid_choice()


if __name__ == "__main__":
    main()
