import requests
import pandas as pd
from datetime import datetime
import io

# === 日期 ===
today = datetime.today()
date_str = today.strftime('%Y/%m/%d')
date_file = today.strftime('%Y%m%d')

# === 櫃買中心官方資料（不含定價）===
url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
params = {
    "l": "zh-tw",
    "d": date_str,
    "o": "csv",
    "s": "0"   # 0 = 不含定價交易
}

res = requests.get(url, params=params)
res.encoding = "utf-8"

df = pd.read_csv(io.StringIO(res.text))

# === 儲存完整行情 ===
csv_name = f"tpex_daily_close_{date_file}.csv"
df.to_csv(csv_name, index=False, encoding="utf-8-sig")

# === 簡易整理（你手機會看的）===
df["漲跌幅"] = pd.to_numeric(df["漲跌幅"], errors="coerce")
df["成交量"] = pd.to_numeric(df["成交股數"], errors="coerce")

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

summary_text = "\n".join(summary)

with open("daily_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary_text)

print("✅ 櫃買資料抓取完成")
