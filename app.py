import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time

# 1. 網頁基礎與主題設定 (黑底深藍專業風格)
st.set_page_config(
    page_title="2026 戰鬥定位圖",
    layout="wide",
    initial_sidebar_state="collapsed" # 手機預設折疊側邊欄
)

# 嵌入 CSS 以進一步調整樣式 (手機端全螢幕化)
st.markdown("""
<style>
    /* 讓圖表更貼近螢幕邊緣 */
    .block-container {
        padding: 1rem 1rem 1rem 1rem;
    }
    /* 在手機上自動隱藏多餘空白 */
    iframe {
        height: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# API 金鑰與配置 (⬅️ 填入您的 Key)
FINNHUB_API_KEY = "d1f12n9r01qsg7d9nf50d1f12n9r01qsg7d9nf5g"

st.markdown("# 2026 投資座標定位")
st.caption(f"數據最後更新: {time.strftime('%Y-%m-%d %H:%M:%S')} (Finnhub Real-time)")

# 2. 定義個股配置與對 2026 的成長預期 (可自由修改 Growth 值)
stocks_config = {
    'NVDA': {'name': 'NVIDIA', 'growth': 75.0, 'sector': 'AI半導體', 'color': '#76b900'},
    'VST': {'name': 'Vistra', 'growth': 45.0, 'sector': '電力設施', 'color': '#ff4b4b'},
    'AMD': {'name': 'AMD', 'growth': 52.0, 'sector': 'AI半導體', 'color': '#fe2850'},
    'CRWD': {'name': 'CrowdStrike', 'growth': 65.0, 'sector': '軟體資安', 'color': '#2962ff'},
    'MELI': {'name': 'MercadoLibre', 'growth': 38.0, 'sector': '電子商務', 'color': '#ffd700'},
    'NU': {'name': 'Nu Holdings', 'growth': 62.0, 'sector': '金融科技', 'color': '#ab47bc'},
    'RKLB': {'name': 'Rocket Lab', 'growth': 92.0, 'sector': '商業太空', 'color': '#00a3e0'},
    'HIMS': {'name': 'Hims & Hers', 'growth': 88.0, 'sector': '遠端醫療', 'color': '#e1bda4'},
    'SMR': {'name': 'NuScale', 'growth': 115.0, 'sector': '小型核能', 'color': '#ff9900'},
    'RDW': {'name': 'Redwire', 'growth': 70.0, 'sector': '商業太空', 'color': '#42a5f5'},
    'TSLA': {'name': 'Tesla', 'growth': 15.0, 'sector': '自動駕駛', 'color': '#cc0000'}
}

# 3. 定義獲取 Finnhub 數據的函式 (計算 PE 與即時數據)
@st.cache_data(ttl=300) # 免費 Key 有頻率限制，緩存 5 分鐘
def get_stock_data():
    data_list = []
    with st.spinner('同步最新數據中...'):
        for ticker, info in stocks_config.items():
            try:
                # 獲取即時股價 (Quote)
                q_res = requests.get(f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}").json()
                # 獲取預估 EPS (Earnings Estimates) 用於計算 Forward P/E
                e_res = requests.get(f"https://finnhub.io/api/v1/stock/earnings-estimate?symbol={ticker}&token={FINNHUB_API_KEY}").json()
                
                price = q_res.get('c', 0)
                # 取華爾街分析師預估未來一年 EPS (如果有的話)
                fwd_eps = e_res[0].get('epsAvg', 1.0) if e_res else 1.0 
                fwd_pe = price / fwd_eps if fwd_eps > 0 else 0
                
                # 計算 PEG
                peg = fwd_pe / info['growth'] if info['growth'] > 0 else 0
                
                data_list.append({
                    'Ticker': ticker,
                    'Name': info['name'],
                    'X: Sales Growth (%)': info['growth'],
                    'Y: Forward P/E': pe if pe < 200 else 200, # 限制極端值以便繪圖
                    '真實 P/E': pe, # 用於顯示真實數據
                    'Price': price,
                    'Sector': info['sector'],
                    'Color': info['color'],
                    'PEG Ratio': round(peg, 2)
                })
            except Exception as e:
                # 若抓取失敗，顯示錯誤或賦予模擬值
                print(f"Error fetching {ticker}: {e}")
                
    return pd.DataFrame(data_list)

# 獲取 DataFrame
df = get_stock_data()

# 4. 針對手機優化的 plotly 互動圖表
# 增加文字選取控制
show_text = st.toggle("顯示個股名稱", value=True)

fig = px.scatter(
    df, x='X: Sales Growth (%)', y='Y: Forward P/E',
    text='Ticker' if show_text else None, # 控制文字顯示
    size='Price', # 氣泡大小反映股價
    color='Sector',
    hover_name='Name',
    hover_data={'Ticker':True, 'Price':':$.2f', 'X: Sales Growth (%)':':.1f%', 'Y: Forward P/E':':.2f', 'PEG Ratio':True, '真實 P/E':False},
    template='plotly_dark'
)

# 優化手機互動功能與視角調整
fig.update_traces(
    textposition='top center',
    marker=dict(line=dict(width=1, color='white'))
)
fig.update_layout(
    xaxis=dict(title="成長性 (2026 預期)", gridcolor='#333', nticks=5), # 限制 nticks 讓手機看更乾淨
    yaxis=dict(title="估值 (Forward P/E)", gridcolor='#333', range=[0, 205]), # 限制極端 P/E 壓縮座標軸
    dragmode='pan', # 預設平移
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), # 傳奇改下方水平顯示，不佔用空間
    margin=dict(l=10, r=10, t=10, b=10) # 徹底極小化邊框
)

# 呈現圖表，啟用橫向縮放與手勢
st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'modeBarButtonsToRemove': ['lasso2d']})

# 5. 分析面板與篩選功能 (收納式，不佔用空間)
with st.expander("📌 2026 數據與 PEG 篩選表", expanded=True):
    # 自動計算 PEG 並表格化
    show_cols = ['Ticker', 'Name', 'Sector', '真實 P/E', 'Sales Growth (%)', 'PEG Ratio']
    df_sorted = df.sort_values(by='PEG Ratio')
    st.table(df_sorted.drop(columns=['X: Sales Growth (%)', 'Y: Forward P/E', 'Price', 'Color']))
