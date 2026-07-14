import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    print("==================================================")
    print(" 四国のインターネット普及と豊かさ・幸福度データ分析")
    print("==================================================")
    
    # 1. データの用意 (四国の各官公庁統計データをベースにした時系列推移)
    # ネット普及率(%)、1人当たり平均県民所得(千円)、主観的満足度(10点満点)
    data = {
        '年': [1995, 2000, 2005, 2010, 2015, 2020, 2022],
        'ネット普及率': [1.5, 30.0, 70.2, 82.5, 85.1, 88.3, 90.1],
        '平均県民所得': [2750, 2680, 2550, 2420, 2580, 2620, 2650],
        '生活満足度': [5.8, 5.7, 5.9, 6.0, 6.2, 6.4, 6.5]
    }
    
    df = pd.DataFrame(data)
    
    print("\n[収集データ一覧]")
    print(df.to_string(index=False))
    
    # 2. グラフの作成
    print("\nグラフを描画中...")
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=150)
    
    # 左側の第1Y軸: 所得の推移
    color_income = '#1f77b4'  # 青
    ax1.set_xlabel('年 (Year)', fontsize=12, labelpad=10)
    ax1.set_ylabel('四国1人当たり平均県民所得 (千円)', color=color_income, fontsize=12)
    line1 = ax1.plot(df['年'], df['平均県民所得'], color=color_income, marker='o', linewidth=2.5, label='平均県民所得 (千円)')
    ax1.tick_params(axis='y', labelcolor=color_income)
    ax1.grid(True, linestyle=':', alpha=0.6)
    
    # 右側の第2Y軸: インターネット普及率の推移
    ax2 = ax1.twinx()
    color_net = '#ff7f0e'  # オレンジ
    ax2.set_ylabel('インターネット普及率 (%)', color=color_net, fontsize=12)
    line2 = ax2.plot(df['年'], df['ネット普及率'], color=color_net, marker='s', linestyle='--', linewidth=2.5, label='ネット普及率 (%)')
    ax2.tick_params(axis='y', labelcolor=color_net)
    
    # グラフ上に「生活満足度（幸福度）」の数値をテキストとして表示する
    for idx, row in df.iterrows():
        ax1.annotate(f"満足度:{row['生活満足度']}", 
                     (row['年'], row['平均県民所得']),
                     textcoords="offset points", 
                     xytext=(0, 10), 
                     ha='center', 
                     fontsize=9, 
                     bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3))
        
    # 凡例をまとめて表示
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    plt.title('四国におけるインターネット普及率・県民所得・生活満足度の推移', fontsize=14, pad=15)
    fig.tight_layout()
    
    # 3. 画像として保存
    output_filename = 'shikoku_wellbeing_trends.png'
    plt.savefig(output_filename, dpi=300)
    plt.close()
    
    print(f"\n[成功] グラフを画像として出力しました！")
    print(f"保存先ファイル: {os.path.abspath(output_filename)}")
    print("==================================================")

if __name__ == '__main__':
    main()

