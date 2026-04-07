"""
키움 Open API+ 래퍼 클래스
- Windows 환경 + 키움증권 HTS(영웅문) 설치 필요
- 32비트 Python 환경에서 실행해야 합니다 (API가 32비트 COM 컴포넌트)
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop


# 오류 코드 매핑
ERROR_CODES = {
    0: "정상처리",
    -10: "실패",
    -100: "사용자정보교환실패",
    -101: "서버접속실패",
    -102: "버전처리실패",
}

# 조회 TR 정보
TR_OPT10001 = "opt10001"  # 주식기본정보요청


class Kiwoom(QAxWidget):
    """키움 Open API+ QAxWidget 래퍼"""

    def __init__(self):
        super().__init__()
        self._set_control("KHOPENAPI.KHOpenAPICtrl.1")

        self._login_event_loop = QEventLoop()
        self._tr_event_loop = QEventLoop()
        self._tr_data: dict = {}

        # 이벤트 연결
        self.OnEventConnect.connect(self._on_event_connect)
        self.OnReceiveTrData.connect(self._on_receive_tr_data)

    # ------------------------------------------------------------------
    # 로그인
    # ------------------------------------------------------------------

    def login(self) -> None:
        """로그인 창을 띄우고 완료될 때까지 대기"""
        ret = self.dynamicCall("CommConnect()")
        if ret != 0:
            raise RuntimeError(f"CommConnect 호출 실패: {ret}")
        self._login_event_loop.exec_()  # 로그인 완료 신호까지 블로킹

    def _on_event_connect(self, err_code: int) -> None:
        if err_code == 0:
            print("[로그인] 성공")
        else:
            msg = ERROR_CODES.get(err_code, f"알 수 없는 오류({err_code})")
            print(f"[로그인] 실패 - {msg}")
        self._login_event_loop.exit()

    # ------------------------------------------------------------------
    # TR 요청 (opt10001 - 주식기본정보)
    # ------------------------------------------------------------------

    def get_stock_price(self, stock_code: str) -> dict:
        """
        opt10001 TR로 주식 현재가 정보를 조회합니다.

        Args:
            stock_code: 종목코드 (예: "005930")

        Returns:
            dict: 종목명, 현재가, 전일대비, 등락률 등 기본 시세 정보
        """
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
        ret = self.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            "주식기본정보요청",   # 사용자 구분 이름
            TR_OPT10001,         # TR 이름
            0,                   # 연속조회 여부 (0: 신규)
            "0101",              # 화면번호
        )
        if ret != 0:
            raise RuntimeError(f"CommRqData 실패: {ret}")

        self._tr_event_loop.exec_()  # 수신 완료까지 블로킹
        return self._tr_data.copy()

    def _on_receive_tr_data(
        self,
        screen_no: str,
        rq_name: str,
        tr_code: str,
        record_name: str,
        prev_next: str,
        data_len: int,
        err_code: str,
        msg: str,
        spl_msg: str,
    ) -> None:
        if rq_name != "주식기본정보요청":
            return

        def get(field: str) -> str:
            return self.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                tr_code, rq_name, 0, field,
            ).strip()

        raw_price = get("현재가")
        raw_diff = get("전일대비")
        raw_rate = get("등락률")
        raw_volume = get("거래량")

        # 부호 처리: 상승(+) 시 앞에 '+' 또는 공백, 하락(-) 시 '-'
        price = abs(int(raw_price)) if raw_price else 0
        diff = int(raw_diff) if raw_diff else 0
        rate = float(raw_rate) if raw_rate else 0.0
        volume = int(raw_volume.replace(",", "")) if raw_volume else 0

        self._tr_data = {
            "종목코드": get("종목코드").strip(),
            "종목명": get("종목명"),
            "현재가": price,
            "전일대비": diff,
            "등락률": rate,
            "거래량": volume,
            "시가": abs(int(get("시가") or 0)),
            "고가": abs(int(get("고가") or 0)),
            "저가": abs(int(get("저가") or 0)),
            "기준가": abs(int(get("기준가") or 0)),
        }

        self._tr_event_loop.exit()

    # ------------------------------------------------------------------
    # 계좌 정보 (로그인 후 사용 가능)
    # ------------------------------------------------------------------

    def get_login_info(self, tag: str) -> str:
        """
        로그인 후 사용자 정보를 반환합니다.

        tag 예시:
            "ACCOUNT_CNT"  - 보유 계좌수
            "ACCNO"        - 계좌번호 목록 (';' 구분)
            "USER_ID"      - 사용자 ID
            "USER_NAME"    - 사용자 이름
            "GetServerGubun" - 서버 구분 (1: 모의투자)
        """
        return self.dynamicCall("GetLoginInfo(QString)", tag)
