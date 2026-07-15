https://api.e-stat.go.jp/rest/3.0/app/getStatsData?cdTime=1985000101%2C1990000101%2C1995000101%2C2000000101%2C2005000101&cdCat01=059&cdCat02=01&cdArea=00054&appId=&lang=J&statsDataId=0002070001&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0


import requests
import pandas as pd

# 1. 設定情報のセット
API_KEY = "dfc5e48757ca24fbed2df946e1e877222d69ed06"
STATS_DATA_ID = "0004023602"  # 家計調査（貯蓄・負債）

url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
params = {
    "appId": API_KEY,
    "statsDataId": STATS_DATA_ID
}

print("e-Statからデータをダウンロード中...")
response = requests.get(url, params=params)

if response.status_code == 200:
    res_json = response.json()
    status = res_json["GET_STATS_DATA"]["RESULT"]["STATUS"]
    
    if status != 0:
        print(f"e-Statエラー: {res_json['GET_STATS_DATA']['RESULT']['ERROR_MSG']}")
    else:
        print("データを正常に受信しました。四国4市の経済データを抽出します...\n")
        
        stat_data = res_json["GET_STATS_DATA"]["STATISTICAL_DATA"]
        
        # 1. 地域コードの辞書作成（コード -> 市名）
        area_map = {}
        for obj in stat_data["CLASS_INF"]["CLASS_OBJ"]:
            if obj["@id"] == "area":
                classes = obj["CLASS"] if isinstance(obj["CLASS"], list) else [obj["CLASS"]]
                for c in classes:
                    area_map[c["@code"]] = c["@name"]
                    
        # 2. 調査項目の辞書作成（コード -> 項目名：年間収入や貯蓄高など）
        item_map = {}
        for obj in stat_data["CLASS_INF"]["CLASS_OBJ"]:
            if obj["@id"] == "cat01":
                classes = obj["CLASS"] if isinstance(obj["CLASS"], list) else [obj["CLASS"]]
                for c in classes:
                    item_map[c["@code"]] = c["@name"]

        # 3. 数値データの抽出
        values = stat_data["DATA_INF"]["VALUE"]
        
        # 四国4市のターゲット名
        shikoku_cities = ["徳島市", "高松市", "松山市", "高知市"]
        # 抽出したい項目（年間収入、貯蓄現在高）
        target_items = ["年間収入", "貯蓄現在高"]
        
        extracted_data = []
        
        for val in values:
            area_code = val.get("@area")
            city_name = area_map.get(area_code, "")
            
            # 市名に四国4市が含まれているか
            if any(target in city_name for target in shikoku_cities):
                item_code = val.get("@cat01")
                item_name = item_map.get(item_code, "")
                
                # 年間収入か貯蓄現在高のデータ、かつ「二人以上の世帯（全体平均）」のデータ（階級コードが全体を示すもの）を狙う
                # ※階級コード @cat02 が "000010" もしくは存在しない、あるいは名前に「平均」が含まれるものを抽出
                cat02_name = val.get("@cat02", "")
                
                if item_name in target_items:
                    # e-Statの家計調査の基本平均データ（五分位に含まれない総数）をフィルタリング
                    if val.get("@cat02") == "001000" or "平均" in item_name or val.get("@cat02") is None:
                        # 市名から余計なコード（03201など）を消して綺麗にする
                        clean_city = city_name.split()[-1] if " " in city_name else city_name
                        
                        extracted_data.append({
                            "都市": clean_city,
                            "項目": item_name,
                            "金額": int(val.get("$", 0)),
                            "単位": val.get("@unit", "円")
                        })
        
        # 4. 綺麗に表に整える
        if extracted_data:
            df = pd.DataFrame(extracted_data)
            # 重複を排除
            df = df.drop_duplicates()
            # 見やすくピボット（横並び）にする
            df_pivot = df.pivot(index="都市", columns="項目", values="金額")
            
            # 単位を「万円」に変換して見やすくする（家計調査は基本「円」単位で入っているため）
            if "年間収入" in df_pivot.columns:
                df_pivot["年間収入（万円）"] = (df_pivot["年間収入"] / 10000).round(1)
            if "貯蓄現在高" in df_pivot.columns:
                df_pivot["貯蓄現在高（万円）"] = (df_pivot["貯蓄現在高"] / 10000).round(1)
                
            # 必要な列だけ表示して、貯蓄高が多い順に並び替え
            display_cols = [c for c in ["年間収入（万円）", "貯蓄現在高（万円）"] if c in df_pivot.columns]
            df_pivot = df_pivot.sort_values(by=display_cols[-1], ascending=False)
            
            print("=== 四国4市 経済的豊かさ（家計調査）ランキング ===")
            print(df_pivot[display_cols])
        else:
            print("条件に合うデータが抽出できませんでした。")
else:
    print(f"通信エラーが発生しました: {response.status_code}")
