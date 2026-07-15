import requests
import pandas as pd

API_KEY = "dfc5e48757ca24fbed2df946e1e877222d69ed06"  # ここに実際のキーを貼る
STATS_DATA_ID = "0003000000"  # 取得したい統計ID

# ベースとなるURL（パラメータを含めない）
url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

# パラメータを辞書型で安全に渡す
params = {
    "appId": "dfc5e48757ca24fbed2df946e1e877222d69ed06",
    "statsDataId": "0003001314" 
}

# リクエスト送信
response = requests.get(url, params=params)

# データの「ステータス」や「中身の一部」を画面に出力する命令
print("--- 取得ステータス ---")
print(response.status_code)  # 200と出れば正常成功

print("\n--- 取得したデータ（最初の500文字） ---")
print(response.text[:500])  # 取得した生データを少しだけ表示
