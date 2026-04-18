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


def main() -> None:
    import json
    print("=" * 50)
    print("  키움 REST API - 현재 시세 조회")
    print("=" * 50)

    api = KiwoomREST()

    for code, name in config.STOCKS.items():
        print(f"[조회 중] {name} ({code})")
        try:
            info = api.get_stock_price(code)
            # 응답 필드 확인을 위해 원본 출력
            print(json.dumps(info, indent=2, ensure_ascii=False))
        except Exception as exc:
            print(f"  오류: {exc}\n")

    print("=" * 50)
    print("조회 완료.")


if __name__ == "__main__":
    main()
