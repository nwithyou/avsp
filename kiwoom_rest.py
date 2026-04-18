"""
키움 REST API 래퍼
- Windows/Mac/Linux 모두 동작
- HTS 설치 불필요
- 64비트 Python 사용 가능
"""

import time
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
        # 만료 시간 앞당겨 갱신 (여유 60초)
        self._token_expires_at = time.time() + int(data.get("expires_in", 86400)) - 60
        print("[인증] 액세스 토큰 발급 완료")

    def _headers(self) -> dict:
        self._ensure_token()
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self._access_token}",
            "appkey": config.APP_KEY,
            "secretkey": config.APP_SECRET,
        }

    # ------------------------------------------------------------------
    # 현재가 조회
    # ------------------------------------------------------------------

    def get_stock_price(self, stock_code: str) -> dict:
        """
        주식 현재가 조회 (단건)

        Args:
            stock_code: 종목코드 (예: "005930")

        Returns:
            dict: 현재가, 전일대비, 등락률, 거래량 등
        """
        url = f"{config.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
        params = {
            "fid_cond_mrkt_div_code": "J",   # J: 주식
            "fid_input_iscd": stock_code,
        }
        resp = self._session.get(url, headers=self._headers(), params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("rt_cd") != "0":
            raise RuntimeError(f"API 오류: {data.get('msg1', '알 수 없는 오류')}")

        output = data["output"]
        price = int(output.get("stck_prpr", 0))        # 현재가
        diff = int(output.get("prdy_vrss", 0))         # 전일대비
        rate = float(output.get("prdy_ctrt", 0))       # 등락률
        volume = int(output.get("acml_vol", 0))        # 누적 거래량
        open_ = int(output.get("stck_oprc", 0))        # 시가
        high = int(output.get("stck_hgpr", 0))         # 고가
        low = int(output.get("stck_lwpr", 0))          # 저가

        return {
            "종목코드": stock_code,
            "종목명": output.get("hts_kor_isnm", ""),
            "현재가": price,
            "전일대비": diff,
            "등락률": rate,
            "거래량": volume,
            "시가": open_,
            "고가": high,
            "저가": low,
        }
