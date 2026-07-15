import requests
import pandas as pd

# 1. 設定情報のセット
API_KEY = "dfc5e48757ca24fbed2df946e1e877222d69ed06"
STATS_DATA_ID = "0003001314"

url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
params = {
    "appId": API_KEY,
    "statsDataId": STATS_DATA_ID
}

print("e-Statからデータをダウンロード中...")
response = requests.get(url, params=params)

if response.status_code == 200:
    res_json = response.json()
    
    # エラーチェック
    status = res_json["GET_STATS_DATA"]["RESULT"]["STATUS"]
    if status != 0:
        print(f"e-Statエラー: {res_json['GET_STATS_DATA']['RESULT']['ERROR_MSG']}")
    else:
        print("データを正常に受信しました。四国4県のデータを解析します...\n")
        
        # 統計データのメイン部分を取得
        stat_data = res_json["GET_STATS_DATA"]["STATISTICAL_DATA"]
        
        # 地域コードのマッピング（コードから県名を特定するため）
        area_info = stat_data["CLASS_INF"]["CLASS_OBJ"]
        area_map = {}
        for obj in area_info:
            if obj["@id"] == "area":  # 地域階層を探す
                # 一つだけの場合とリストの場合があるため対応
                classes = obj["CLASS"] if isinstance(obj["CLASS"], list) else [obj["CLASS"]]
                for c in classes:
                    area_map[c["@code"]] = c["@name"]
        
        # 数値データの抽出
        values = stat_data["DATA_INF"]["VALUE"]
        
        # 四国4県のデータを格納するリスト
        shikoku_list = []
        # 四国4県の都道府県コード（頭の2桁など、データ形式に合わせるための判定用）
        shikoku_names = ["徳島県", "香川県", "愛媛県", "高知県"]
        
        for val in values:
            area_code = val.get("@area")
            area_name = area_map.get(area_code, "不明")
            
            # 県名が四国4県にマッチするかチェック
            if any(name in area_name for name in shikoku_names):
                # データの項目名（人口、総人口など）を取得
                cat_code = val.get("@cat01") # 分類コード
                
                shikoku_list.append({
                    "地域": area_name,
                    "数値": val.get("$"),
                    "単位": val.get("@unit")
                })
        
        # 表（DataFrame）にして綺麗に表示
        if shikoku_list:
            df = pd.DataFrame(shikoku_list)
            # 重複などを排除して見やすくソート
            df = df.drop_duplicates().reset_index(drop=True)
            print("=== 四国4県の抽出結果 ===")
            print(df.to_string(index=False))
        else:
            print("四国4県のデータが見つかりませんでした。データ構造を確認します。")
            # デバッグ用に取得できた地域一覧を少し表示
            print("取得できた地域（一部）:", list(area_map.values())[:10])
else:
    print(f"通信エラーが発生しました: {response.status_code}")

