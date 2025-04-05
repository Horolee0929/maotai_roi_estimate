import streamlit as st
import akshare as ak
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="全球股票投资回报估算器", layout="centered")
st.title("📈 全球股票估值 + 回报率计算器")

# 股票代码输入
st.sidebar.header("📌 股票选择")
market = st.sidebar.selectbox("选择市场", ["A股", "美股"])
stock_code = st.sidebar.text_input("输入股票代码 (A股如600519，美股如AAPL)", value="600519" if market == "A股" else "AAPL")

# 数据获取函数
def get_stock_data(market, stock_code):
    try:
        if market == "A股":
            stock_code_full = stock_code if stock_code.startswith("6") else f"sz{stock_code}"
            df = ak.stock_individual_info_em(symbol=stock_code_full)
            eps_row = df[df["item"] == "每股收益"]
            pe_row = df[df["item"] == "市盈率"]
            price_row = df[df["item"] == "最新价"]
            eps = float(eps_row["value"].values[0]) if not eps_row.empty else None
            pe = float(pe_row["value"].values[0]) if not pe_row.empty else None
            price = float(price_row["value"].values[0]) if not price_row.empty else eps * pe if eps and pe else None
            dividend_ratio = 0.04
        else:
            stock = yf.Ticker(stock_code)
            info = stock.info
            eps = float(info.get("trailingEps", 0))
            pe = float(info.get("trailingPE", 0))
            price = float(info.get("currentPrice", 0))
            dividend_ratio = float(info.get("dividendYield", 0) or 0)
        if eps and pe and price:
            return eps, pe, price, dividend_ratio, True
        else:
            raise ValueError("缺失美股关键数据")
    except Exception as e:
        st.warning(f"⚠️ 实时数据获取失败，请手动输入参数。错误信息：{e}")
        return None, None, None, None, False

# 获取数据
eps, pe, price_now, dividend_ratio, data_success = get_stock_data(market, stock_code)

# 显示数据或手动输入
st.subheader("📌 财务指标")

if data_success:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("每股收益 EPS", f"{eps:.2f}")
    col2.metric("市盈率 PE", f"{pe:.2f}")
    col3.metric("当前股价", f"{price_now:.2f}")
    col4.metric("股息率", f"{dividend_ratio*100:.2f}%")
else:
    eps = st.number_input("每股收益 EPS（手动输入）", min_value=0.0, step=0.1, format="%.2f")
    pe = st.number_input("市盈率 PE（手动输入）", min_value=0.0, step=0.1, format="%.2f")
    price_now = st.number_input("当前股价（手动输入）", min_value=0.0, step=0.1, format="%.2f")
    dividend_ratio_input = st.number_input("股息率（%）（手动输入）", min_value=0.0, step=0.1, format="%.2f")
    dividend_ratio = dividend_ratio_input / 100

st.markdown("---")

# 用户输入参数
st.subheader("🧮 回报率估算参数")
buy_price = st.number_input("你的买入价（元/美元）", value=price_now if price_now else 100.0)
future_pe = st.slider("未来市盈率 PE（假设）", 5.0, 60.0, 20.0)
leverage = st.slider("杠杆倍数", 1.0, 3.0, 1.0)
holding_years = st.slider("持有年限", 1, 10, 1)
profit_growth_rate = st.slider("利润年增长率 (%)", 0.0, 30.0, 15.0) / 100

# 回报计算
future_price = eps * (1 + profit_growth_rate)**holding_years * future_pe
total_dividend = sum([eps * (1 + profit_growth_rate)**i * dividend_ratio for i in range(holding_years)])

initial_investment = buy_price / leverage
total_return = (future_price - buy_price) + total_dividend
annualized_return = ((initial_investment + total_return) / initial_investment)**(1/holding_years) - 1

# 结果
st.markdown("---")
st.subheader("📈 回报估算结果")
st.write(f"**未来股价（估算）**：{future_price:.2f}")
st.write(f"**持有期间总分红**：{total_dividend:.2f}")
st.write(f"**总收益（股价+分红）**：{total_return:.2f}")
st.write(f"**年化回报率**：{annualized_return*100:.2f}%")
