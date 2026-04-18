"""
키움 REST API 래퍼
- Windows/Mac/Linux 모두 동작
- HTS 설치 불필요
- 64비트 Python 사용 가능
"""

import time
from datetime import datetime
import requests

import config


class KiwoomREST:
    """키움 REST API 클라이언트"""

    def __init__(self):
        self._access_token: str = ""
        self._token_expires_at: float = 0.0
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # 인증
    # ------------------------------------------------------------------

    def _ensure_token(self) -> None:
        """토큰이 없거나 만료됐으면 새로 발급"""
        if self._access_token and time.time() < self._token_expires_at:
            return

        url = f"{config.BASE_URL}/oauth2/token"
        body = {
            "grant_type": "client_credentials",
            "appkey": config.APP_KEY,
            "secretkey": config.APP_SECRET,
        }
        resp = self._session.post(url, json=body, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        self._access_token = data["token"]
        # expires_dt 형식: "20241107083713" (YYYYMMDDHHmmss)
        expires_dt = data.get("expires_dt", "")
        if expires_dt:
            self._token_expires_at = datetime.strptime(expires_dt, "%Y%m%d%H%M%S").timestamp() - 60
        else:
            self._token_expires_at = time.time() + 86400 - 60
        print("[인증] 액세스 토큰 발급 완료")

    def _headers(self, api_id: str) -> dict:
        self._ensure_token()
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self._access_token}",
            "api-id": api_id,
        }

    # ------------------------------------------------------------------
    # 현재가 조회
    # ------------------------------------------------------------------

    def get_stock_price(self, stock_code: str) -> dict:
        """
        주식 현재가 조회 (ka10007 - 시세표성정보요청)

        Args:
            stock_code: 종목코드 (예: "005930")

        Returns:
            dict: 서버 응답 원본 (응답 필드 확인용)
        """
        url = f"{config.BASE_URL}/api/dostk/mrkcond"
        body = {
            "stk_cd": f"KRX:{stock_code}",
        }
        resp = self._session.post(url, headers=self._headers("ka10007"), json=body, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("return_code") not in (0, "0", None):
            raise RuntimeError(f"API 오류: {data.get('return_msg', '알 수 없는 오류')}")

        def to_int(v):
            try:
                return int(str(v).replace(",", ""))
            except (ValueError, TypeError):
                return 0

        def to_float(v):
            try:
                return float(str(v).replace(",", ""))
            except (ValueError, TypeError):
                return 0.0

        return {
            "종목코드": stock_code,
            "종목명": data.get("stk_nm", ""),
            "현재가": to_int(data.get("cur_prc")),
            "전일종가": to_int(data.get("pred_close_pric")),
            "등락률": to_float(data.get("flu_rt")),
            "시가": to_int(data.get("open_pric")),
            "고가": to_int(data.get("high_pric")),
            "저가": to_int(data.get("low_pric")),
            "거래량": to_int(data.get("trde_qty")),
            "부호": data.get("smbol", ""),  # +: 상승, -: 하락
        }
