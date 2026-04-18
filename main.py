"""
삼성전자 / SK하이닉스 현재 시세 조회 (키움 REST API)

실행 전 준비:
  1. https://apiportal.kiwoom.com 에서 앱키/앱시크릿 발급
  2. config.py 에 APP_KEY, APP_SECRET 입력

실행 방법:
  pip install -r requirements.txt
  python main.py
"""

from kiwoom_rest import KiwoomREST
import config


def print_price_info(info: dict) -> None:
    sign = "▲" if info["전일대비"] >= 0 else "▼"
    rate_sign = "+" if info["등락률"] >= 0 else ""
    print(
        f"  [{info['종목코드']}] {info['종목명']}\n"
        f"    현재가  : {info['현재가']:>10,} 원\n"
        f"    전일대비: {sign} {abs(info['전일대비']):>8,} 원  ({rate_sign}{info['등락률']:.2f}%)\n"
        f"    시 / 고 / 저: {info['시가']:,} / {info['고가']:,} / {info['저가']:,}\n"
        f"    거래량  : {info['거래량']:>10,} 주\n"
    )


def main() -> None:
    print("=" * 50)
    print("  키움 REST API - 현재 시세 조회")
    print("=" * 50)

    api = KiwoomREST()

    for code, name in config.STOCKS.items():
        print(f"[조회 중] {name} ({code})")
        try:
            info = api.get_stock_price(code)
            print_price_info(info)
        except Exception as exc:
            print(f"  오류: {exc}\n")

    print("=" * 50)
    print("조회 완료.")


if __name__ == "__main__":
    main()
