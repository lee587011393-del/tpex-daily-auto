import requests
import pandas as pd
from datetime import datetime
import io
import sys

today = datetime.today()
date_str = today.strftime('%Y/%m/%d')
date_file = today.strftime('%Y%m%d')

url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
params = {
    "l": "zh-tw",
    "d": date_str,
    "o": "csv",
    "s": "0"
}

res = requests.get(url, params=params, timeout=20)
res.encoding = "utf-8"

# 🧯 防呆 1：不是 CSV 就直接結束（不算失敗）
if "證券代號" not in res.text:
    print("⚠️ 今日無有效 CSV（可能是假日或資料尚未更新）")
    sys.exit(0)

try:
    df = pd.read_csv(io.StringIO(res.text))
except Exception as e:
    print("⚠️ CSV 解析失敗，但不中斷流程")
    print(e)
    sys.exit(0)

# 🧯 防呆 2：資料為空
if df.empty:
    print("⚠️ 今日資料為空")
    sys.exit(0)

csv_name = f"tpex_daily_close_{date_file}.csv"
df.to_csv(csv_name, index=False, encoding="utf-8-sig")

# === 簡易摘要 ===
def to_num(col):
    return pd.to_numeric(df[col], errors="coerce") if col in df.columns else None

if "漲跌幅" in df.columns and "成交股數" in df.columns:
    df["漲跌幅"] = to_num("漲跌幅")
    df["成交量"] = to_num("成交股數")

    top_up = df.sort_values("漲跌幅", ascending=False).head(5)
    top_vol = df.sort_values("成交量", ascending=False).head(5)

    summary = []
    summary.append(f"📅 {date_str} 上櫃市場摘要\n")

    summary.append("📈 漲幅前五名")
    for _, r in top_up.iterrows():
        summary.append(f"- {r['代號']} {r['名稱']}：{r['漲跌幅']}%")

    summary.append("\n🔥 成交量前五名")
    for _, r in top_vol.iterrows():
        summary.append(f"- {r['代號']} {r['名稱']}：{int(r['成交量']):,}")

    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(summary))

print("✅ 程式完成（安全結束）")
