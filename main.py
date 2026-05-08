from repository.sample_repository import SampleRepository
from controller.sample_controller import SampleController
from view.sample_view import SampleView


def _handle_sample_menu(ctrl: SampleController, view: SampleView) -> None:
    while True:
        print("\n=== 시료 관리 ===")
        print("1. 시료 등록")
        print("2. 시료 조회")
        print("3. 시료 검색")
        print("0. 돌아가기")
        choice = input("선택: ").strip()
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
            print("잘못된 입력입니다. 다시 선택하세요.")


def main() -> None:
    sample_ctrl = SampleController(SampleRepository())
    sample_view = SampleView()

    while True:
        print("\n=== 반도체 시료 생산 주문 관리 시스템 ===")
        print("1. 시료 관리")
        print("0. 종료")
        choice = input("메뉴 선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            _handle_sample_menu(sample_ctrl, sample_view)
        else:
            print("잘못된 입력입니다. 다시 선택하세요.")


if __name__ == "__main__":
    main()
