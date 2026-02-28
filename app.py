import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time

# 1. 基礎設定與 API 配置
st.set_page_config(page_title="2026 投資戰略座標", layout="wide")
FINNHUB_API_KEY = "d1f12n9r01qsg7d9nf50d1f12n9r01qsg7d9nf5g" # ⬅️ 填入你的 KEY

st.title("🚀 Nvidia 座標圖邏輯：2026 動態估值分析")
st.caption(f"數據更新時間: {time.strftime('%Y-%m-%d %H:%M:%S')} (Finnhub Real-time)")

# 2. 定義個股清單與 2026 預期營收成長率 (根據研究報告設定)
# 這裡的 Growth 是我們對 2026 年的預測值，P/E 則由 API 股價動態計算
stocks_config = {
    'NVDA': {'name': 'NVIDIA', 'growth': 75.0, 'sector': '半導體/AI', 'color': '#76b900'},
    'VST': {'name': 'Vistra', 'growth': 45.0, 'sector': '核能/電力', 'color': '#ff4b4b'},
    'AMD': {'name': 'AMD', 'growth': 52.0, 'sector': '半導體/AI', 'color': '#fe2850'},
    'RKLB': {'name': 'Rocket Lab', 'growth': 92.0, 'sector': '商業太空', 'color': '#00a3e0'},
    'MSFT': {'name': 'Microsoft', 'growth': 18.5, 'sector': '科技巨頭', 'color': '#f25022'},
    'TSLA': {'name': 'Tesla', 'growth': 15.0, 'sector': '自動駕駛', 'color': '#cc0000'},
    'SMR': {'name': 'NuScale', 'growth': 115.0, 'sector': '小型核能', 'color': '#ff9900'}
}

# 3. 定義獲取 Finnhub 數據的函式
def get_finnhub_data(symbol):
    # 獲取即時股價 (Quote)
    quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    # 獲取預估盈餘 (Earnings Estimates) 用於計算 Forward P/E
    est_url = f"https://finnhub.io/api/v1/stock/earnings-estimate?symbol={symbol}&token={FINNHUB_API_KEY}"
    
    try:
        q_res = requests.get(quote_url).json()
        e_res = requests.get(est_url).json()
        
        current_price = q_res.get('c', 0)
        # 取未來一年的平均 EPS 預估值
        fwd_eps = e_res[0].get('epsAvg', 1.0) if e_res else 1.0 
        fwd_pe = current_price / fwd_eps if fwd_eps > 0 else 0
        
        return current_price, round(fwd_pe, 2)
    except:
        return 0, 0

# 4. 建立數據集
data_list = []
with st.spinner('正在同步 Finnhub 最新市場數據...'):
    for ticker, info in stocks_config.items():
        price, pe = get_finnhub_data(ticker)
        data_list.append({
            'Ticker': ticker,
            'Name': info['name'],
            'Sales Growth (%)': info['growth'],
            'Forward P/E': pe,
            'Price': price,
            'Sector': info['sector'],
            'Color': info['color']
        })

df = pd.DataFrame(data_list)

# 5. 繪製互動式座標圖
fig = px.scatter(
    df, x='Sales Growth (%)', y='Forward P/E',
    text='Ticker', size='Price', color='Sector',
    hover_name='Name',
    hover_data={'Ticker':True, 'Price':':$.2f', 'Sales Growth (%)':':.1f%', 'Forward P/E':':.2f'},
    template='plotly_dark',
    height=600
)

# 優化圖表外觀與縮放
fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
fig.update_layout(
    xaxis=dict(title="2026 預期營收成長率 (%)", gridcolor='#333'),
    yaxis=dict(title="動態預估本益比 (Forward P/E)", gridcolor='#333'),
    dragmode='pan' # 預設為平移，方便手機操作
)

st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

# 6. 詳細政策評估表 (自動化與表格化)
st.divider()
st.subheader("📋 2026 關鍵政策與個股估值評估")

policy_df = pd.DataFrame([
    ["核能/電力 (VST, SMR)", "2026 電力優先分配法案", "顯著右移 (成長加速)", "強烈看好"],
    ["半導體 (NVDA, AMD)", "先進封裝補貼實施", "下移 (估值修復)", "價值區"],
    ["商業太空 (RKLB)", "太空軍商業採購撥款", "氣泡變大 (營收噴發)", "高風險高回報"],
    ["自動駕駛 (TSLA)", "Robotaxi 監管拉鋸", "停留在左上方", "觀望"],
], columns=["板塊", "進行中政策", "座標位移方向", "詳細評估"])

st.table(policy_df)
