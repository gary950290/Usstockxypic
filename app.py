import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time

# 1. 基礎設定
st.set_page_config(page_title="2026 投資座標定位", layout="wide")

# 請確保在此填入正確的 API Key
FINNHUB_API_KEY = "d6h6jc9r01qnjncnhra0d6h6jc9r01qnjncnhrag"

st.title("🚀 Nvidia 座標圖邏輯：2026 動態估值")

# 2. 定義個股配置
stocks_config = {
    'NVDA': {'name': 'NVIDIA', 'growth': 75.0, 'sector': 'AI半導體'},
    'VST': {'name': 'Vistra', 'growth': 45.0, 'sector': '電力設施'},
    'AMD': {'name': 'AMD', 'growth': 52.0, 'sector': 'AI半導體'},
    'RKLB': {'name': 'Rocket Lab', 'growth': 92.0, 'sector': '商業太空'},
    'TSLA': {'name': 'Tesla', 'growth': 15.0, 'sector': '自動駕駛'}
}

# 3. 抓取數據 (加入錯誤防護)
def get_safe_data():
    data_list = []
    progress_bar = st.progress(0)
    for i, (ticker, info) in enumerate(stocks_config.items()):
        try:
            # 抓取股價
            q_res = requests.get(f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}").json()
            # 抓取預估值
            e_res = requests.get(f"https://finnhub.io/api/v1/stock/earnings-estimate?symbol={ticker}&token={FINNHUB_API_KEY}").json()
            
            price = q_res.get('c', 0)
            fwd_eps = e_res[0].get('epsAvg', 1.0) if (e_res and len(e_res) > 0) else 1.0
            fwd_pe = price / fwd_eps if fwd_eps > 0 else 0
            
            # 限制極端值以防座標軸崩潰
            plot_pe = min(fwd_pe, 200) if fwd_pe > 0 else 0
            
            data_list.append({
                'Ticker': ticker,
                'Name': info['name'],
                'Sales Growth (%)': info['growth'],
                'Forward P/E': plot_pe,
                '真實 P/E': round(fwd_pe, 2),
                'Price': price,
                'Sector': info['sector']
            })
        except Exception as e:
            st.warning(f"⚠️ 無法取得 {ticker} 的即時數據，請檢查 API Key 或額度。")
        progress_bar.progress((i + 1) / len(stocks_config))
    return pd.DataFrame(data_list)

df = get_safe_data()

# 4. 關鍵修復：檢查 DataFrame 是否為空
if not df.empty:
    # 確保欄位名稱完全對應
    fig = px.scatter(
        df, 
        x='Sales Growth (%)', 
        y='Forward P/E',
        text='Ticker',
        size='Price',
        color='Sector',
        hover_name='Name',
        hover_data=['真實 P/E', 'Price'],
        template='plotly_dark'
    )
    
    fig.update_layout(dragmode='pan', height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # 政策評估表
    st.subheader("📋 2026 關鍵政策與估值評估")
    st.dataframe(df[['Ticker', 'Name', 'Sector', 'Sales Growth (%)', '真實 P/E']])
else:
    st.error("❌ 數據載入失敗，目前沒有可顯示的個股。請確認您的 Finnhub API Key 是否正確設定。")
