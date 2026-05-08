_W = 60


class MenuView:
    def show_main_menu(self, n_samples: int, reserved: int, producing: int, confirmed: int) -> None:
        print("\n" + "=" * _W)
        print("  반도체 시료 생산 주문 관리 시스템")
        print("=" * _W)
        print(
            f"  시료: {n_samples}종"
            f"  |  접수: {reserved}건"
            f"  |  생산중: {producing}건"
            f"  |  출고대기: {confirmed}건"
        )
        print("-" * _W)
        print("  1. 시료 관리")
        print("  2. 시료 주문")
        print("  3. 주문 승인/거절")
        print("  4. 모니터링")
        print("  5. 생산 라인 조회")
        print("  6. 출고 처리")
        print("  0. 종료")
        print("=" * _W)

    def prompt_main_choice(self) -> str:
        return input("  메뉴 선택: ").strip()

    def show_sub_menu(self, title: str, options: list[str]) -> None:
        print("\n" + "=" * _W)
        print(f"  [ {title} ]")
        print("-" * _W)
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        print("  0. 돌아가기")
        print("=" * _W)

    def prompt_sub_choice(self) -> str:
        return input("  선택: ").strip()

    def show_invalid_choice(self) -> None:
        print("  잘못된 입력입니다. 다시 선택하세요.")
