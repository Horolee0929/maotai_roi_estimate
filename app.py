import streamlit as st
import akshare as ak
import pandas as pd

st.set_page_config(page_title="贵州茅台投资回报估算器", layout="centered")
st.title("📈 贵州茅台实时估值 + 回报计算器")

# 获取茅台实时财务数据
@st.cache_data(show_spinner=False)
def get_maotai_data():
    try:
        df = ak.stock_financial_analysis_indicator()
        # ✅ 调试
        st.write("AK 返回数据结构预览：", df.head())  
        st.write("列名列表：", df.columns.tolist())    
         # ✅ 调试
        
        if "股票简称" in df.columns:
            df = df[df["股票简称"] == "贵州茅台"]
        elif "股票代码" in df.columns:
            df = df[df["股票代码"] == "600519"]
        else:
            raise ValueError("接口数据中未找到股票代码或简称")

        eps = float(df.iloc[0]["基本每股收益(元)"])
        pe = float(df.iloc[0]["市盈率"])
        dividend_ratio = float(df.iloc[0]["股息率(%)"]) / 100  # 转换为小数
        price = eps * pe
        return eps, pe, price, dividend_ratio
    except Exception as e:
        st.warning(f"⚠️ 实时数据获取失败，使用默认值：{e}")
        return 68.63, 22.0, 1388.0, 0.04  # 默认股息率 4%

# 获取数据
eps, pe, price_now, dividend_ratio = get_maotai_data()

# 显示实时指标
st.subheader("📌 实时财务数据（贵州茅台）")
col1, col2, col3, col4 = st.columns(4)
col1.metric("每股收益 EPS", f"{eps:.2f} 元")
col2.metric("市盈率 PE", f"{pe:.2f}")
col3.metric("当前股价（估算）", f"{price_now:.2f} 元")
col4.metric("股息率", f"{dividend_ratio*100:.2f}%")

st.markdown("---")

# 用户输入参数
st.subheader("🧮 回报率估算参数")
buy_price = st.number_input("你的买入价（元）", value=1388.0)
future_pe = st.slider("未来市盈率 PE（假设）", 5.0, 40.0, 20.0)
leverage = st.slider("杠杆倍数", 1.0, 3.0, 1.0)
holding_years = st.slider("持有年限", 1, 10, 1)
profit_growth_rate = st.slider("利润年增长率 (%)", 0.0, 30.0, 15.0) / 100

# 计算
future_price = eps * (1 + profit_growth_rate)**holding_years * future_pe
total_dividend = sum([eps * (1 + profit_growth_rate)**i * dividend_ratio for i in range(holding_years)])

initial_investment = buy_price / leverage
total_return = (future_price - buy_price) + total_dividend
annualized_return = ((initial_investment + total_return) / initial_investment)**(1/holding_years) - 1

# 结果
st.markdown("---")
st.subheader("📈 回报估算结果")
st.write(f"**未来股价（估算）**：{future_price:.2f} 元")
st.write(f"**持有期间总分红**：{total_dividend:.2f} 元")
st.write(f"**总收益（股价+分红）**：{total_return:.2f} 元")
st.write(f"**年化回报率**：{annualized_return*100:.2f}%")
