"""
삼성전자 / SK하이닉스 현재 시세 조회 예제
실행 방법:
    python main.py

주의사항:
    - Windows 전용 (키움 Open API+는 Windows COM 컴포넌트)
    - 키움증권 HTS(영웅문4) 설치 및 로그인 상태 필요
    - 32비트 Python 환경 권장
    - 장중(09:00~15:30) 또는 시간외 거래 시간에 실행해야 실시간 데이터 수신 가능
"""

import sys
import time
from PyQt5.QtWidgets import QApplication

from kiwoom import Kiwoom

# 조회할 종목 목록
STOCKS = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
}

# TR 요청 사이 대기 시간 (키움 API 조회 제한: 초당 5회)
TR_DELAY_SEC = 0.25


def print_price_info(info: dict) -> None:
    """시세 정보를 보기 좋게 출력"""
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
    app = QApplication(sys.argv)

    kiwoom = Kiwoom()

    print("=" * 50)
    print("  키움 Open API+ 시세 조회")
    print("=" * 50)
    print("[1/2] 로그인 중... (키움 로그인 창이 뜨면 인증하세요)")
    kiwoom.login()

    server = kiwoom.get_login_info("GetServerGubun")
    server_name = "모의투자 서버" if server == "1" else "실거래 서버"
    user_name = kiwoom.get_login_info("USER_NAME")
    print(f"  접속 서버 : {server_name}")
    print(f"  사용자    : {user_name}")
    print()

    print("[2/2] 시세 조회 중...")
    print("-" * 50)

    for code, name in STOCKS.items():
        try:
            info = kiwoom.get_stock_price(code)
            print_price_info(info)
        except Exception as exc:
            print(f"  [{code}] {name} 조회 실패: {exc}")
        time.sleep(TR_DELAY_SEC)

    print("=" * 50)
    print("조회 완료.")


if __name__ == "__main__":
    main()
