from model.sample import Sample

_TABLE_WIDTH = 64
_TABLE_HEADER = f"{'ID':<12} {'이름':<20} {'평균생산시간':>12} {'수율':>8} {'재고':>6}"


class SampleView:
    def prompt_register(self) -> tuple[str, str, float, float]:
        sample_id = input("시료 ID: ").strip()
        name = input("이름: ").strip()
        avg_time = float(input("평균 생산시간(시간): ").strip())
        yield_rate = float(input("수율(0.0~1.0): ").strip())
        return sample_id, name, avg_time, yield_rate

    def prompt_search_keyword(self) -> str:
        return input("검색 키워드(이름 부분 일치): ").strip()

    def show_sample_list(self, samples: list[Sample]) -> None:
        if not samples:
            print("등록된 시료가 없습니다.")
            return
        print(_TABLE_HEADER)
        print("-" * _TABLE_WIDTH)
        for s in samples:
            print(f"{s.sample_id:<12} {s.name:<20} {s.avg_production_time:>12.1f} {s.yield_rate:>8.2f} {s.stock:>6}")

    def show_search_result(self, samples: list[Sample]) -> None:
        if not samples:
            print("검색 결과가 없습니다.")
            return
        self.show_sample_list(samples)

    def show_register_success(self, sample_id: str) -> None:
        print(f"시료 등록 완료: {sample_id}")
