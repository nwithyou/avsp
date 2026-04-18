"""
키움 REST API 설정
키움 Open API 개발자 센터에서 앱키/앱시크릿을 발급받아 입력하세요.
https://apiportal.kiwoom.com
"""

# 키움 REST API 앱키 (개발자 센터에서 발급)
APP_KEY = "여기에_앱키_입력"
APP_SECRET = "여기에_앱시크릿_입력"

# API 서버 주소
BASE_URL = "https://api.kiwoom.com"

# 조회할 종목
STOCKS = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
}
