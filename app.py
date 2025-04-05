import streamlit as st

# ✅ 自定义蓝色滑动条样式
st.markdown(
    """
    <style>
    /* 滑动条轨道背景（整条线条） */
    input[type="range"] {
        accent-color: #1f77b4; /* 通用的蓝色滑条样式 */
    }

    /* WebKit浏览器专用：轨道背景（未选中区域） */
    input[type="range"]::-webkit-slider-runnable-track {
        background: #cce5ff;
        height: 6px;
        border-radius: 4px;
    }

    /* WebKit：滑块（thumb）颜色 */
    input[type="range"]::-webkit-slider-thumb {
        background: #1f77b4;
        border: none;
    }

    /* Firefox专用：轨道高亮部分 */
    input[type="range"]::-moz-range-progress {
        background-color: #1f77b4;
    }

    input[type="range"]::-moz-range-track {
        background-color: #cce5ff;
    }

    input[type="range"]::-moz-range-thumb {
        background-color: #1f77b4;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ✅ 回报率计算逻辑
def estimate_annual_return(
    buy_price,
    current_eps,
    profit_growth_rate,
    dividend_payout_ratio,
    leverage_rate,
    current_pe,
    future_pe_assumption,
    holding_years=1
):
    future_eps = current_eps * ((1 + profit_growth_rate) ** holding_years)
    future_price = future_eps * future_pe_assumption

    total_dividend = sum([
        current_eps * ((1 + profit_growth_rate) ** year) * dividend_payout_ratio
        for year in range(holding_years)
    ])

    total_return = (future_price - buy_price) + total_dividend
    capital_invested = buy_price / leverage_rate
    annualized_return = ((capital_invested + total_return) / capital_invested) ** (1 / holding_years) - 1

    return {
        '未来股价': round(future_price, 2),
        '总分红': round(total_dividend, 2),
        '总收益': round(total_return, 2),
        '年化回报率 (%)': round(annualized_return * 100, 2)
    }

# ✅ 页面布局
st.title("贵州茅台投资回报率估算器")

st.sidebar.header("输入参数")
buy_price = st.sidebar.number_input("买入价（元）", value=1388.0)
current_eps = st.sidebar.number_input("当前每股收益 EPS（元）", value=68.63)
profit_growth_rate = st.sidebar.slider("利润年增长率 (%)", 0.0, 30.0, 15.38) / 100
dividend_payout_ratio = st.sidebar.slider("分红率 (%)", 0.0, 100.0, 40.0) / 100
leverage_rate = st.sidebar.slider("杠杆倍数", 1.0, 3.0, 1.0)
current_pe = st.sidebar.number_input("当前市盈率 PE", value=22.0)
future_pe_assumption = st.sidebar.number_input("未来市盈率 PE 假设", value=20.0)
holding_years = st.sidebar.slider("持有年限", 1, 10, 1)

# ✅ 计算
result = estimate_annual_return(
    buy_price,
    current_eps,
    profit_growth_rate,
    dividend_payout_ratio,
    leverage_rate,
    current_pe,
    future_pe_assumption,
    holding_years
)

# ✅ 显示结果
st.subheader("估算结果")
for k, v in result.items():
    st.write(f"**{k}**：{v}")
