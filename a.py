import xml.etree.ElementTree as ET
import pandas as pd
import requests
import urllib3

# SSL検証無効化によるWarningを非表示にする
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 発行したアプリケーションID
APP_ID = "dfc5e48757ca24fbed2df946e1e877222d69ed06"

url = (
    f"https://api.e-stat.go.jp/rest/3.0/app/getStatsData?"
    f"cdTime=1985000101%2C1990000101%2C1995000101%2C2000000101%2C2005000101"
    f"&cdCat01=059&cdCat02=01&cdArea=00054"
    f"&appId={APP_ID}"
    f"&lang=J&statsDataId=0002070001&metaGetFlg=Y&cntGetFlg=N"
    f"&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0"
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("e-StatからXMLデータを取得中...")
response = requests.get(url, headers=headers, verify=False)
response.encoding = "utf-8"

if response.status_code == 200:
    root = ET.fromstring(response.content)
    
    # 1. メタデータ（コードと日本語名の対応表）の辞書を作成
    meta_maps = {}
    class_objects = root.findall(".//CLASS_OBJ")
    for obj in class_objects:
        obj_id = obj.attrib.get("id")  # tab, cat01, area, time など
        meta_maps[obj_id] = {}
        
        # 各コードと名称をマッピング
        classes = obj.findall("CLASS")
        for c in classes:
            code = c.attrib.get("code")
            name = c.attrib.get("name")
            meta_maps[obj_id][code] = name

    # 2. データ本体の抽出
    data_list = []
    values = root.findall(".//VALUE")
    for v in values:
        row_data = v.attrib.copy()
        row_data["value"] = v.text
        data_list.append(row_data)

    if data_list:
        df = pd.DataFrame(data_list)
        
        # 3. 各列のコード値を日本語の名称に置換
        for col in df.columns:
            if col in meta_maps:
                df[col] = df[col].map(meta_maps[col]).fillna(df[col])
        
        # 金額（value）を数値型に変換
        df["value"] = pd.to_numeric(df["value"])
        
        print("\n--- 日本語ラベルに変換したデータ ---")
        print(df[["time", "cat01", "cat02", "area", "value", "unit"]])
