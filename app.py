import streamlit as st
from itertools import combinations

# 页面配置：移动端优化
st.set_page_config(page_title="牛牛 Pro", layout="centered")

# 自定义 CSS：仿 iPhone 计算器样式
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        height: 70px;
        font-size: 24px !important;
        font-weight: bold;
        border-radius: 50px;
        border: none;
        color: white;
    }
    /* 数字键：深灰色 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(n) button {
        background-color: #333333;
    }
    /* 字母/特殊键：浅灰色 */
    div[data-testid="stHorizontalBlock"] button[aria-label="J"], 
    div[data-testid="stHorizontalBlock"] button[aria-label="Q"],
    div[data-testid="stHorizontalBlock"] button[aria-label="K"],
    div[data-testid="stHorizontalBlock"] button[aria-label="A"] {
        background-color: #A5A5A5;
        color: black;
    }
    /* 清空按钮：红色/橙色 */
    .clear-btn button {
        background-color: #FF9500 !important;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 核心算牌逻辑 ---
def get_val(c):
    if c in ['J', 'Q', 'K', '10']: return 10
    if c == 'A': return 1
    return int(c)

def solve(cards):
    # 修复 TypeError: 统一转为元组处理
    cards = tuple(c.upper() for c in cards)
    hands = {cards}
    # 3/6 互换逻辑
    for i, c in enumerate(cards):
        tmp = set()
        for h in hands:
            lst = list(h)
            if c == '3': lst[i] = '6'; tmp.add(tuple(lst))
            elif c == '6': lst[i] = '3'; tmp.add(tuple(lst))
        hands.update(tmp)

    best = {"type": "没牛", "score": -1, "base": [], "sub": []}
    for h in hands:
        for b_idx in combinations(range(5), 3):
            s_idx = [i for i in range(5) if i not in b_idx]
            base, sub = [h[i] for i in b_idx], [h[i] for i in s_idx]
            if sum(get_val(x) for x in base) % 10 == 0:
                is_bb = (get_val(sub[0]) == get_val(sub[1]))
                pts = sum(get_val(x) for x in sub)
                score = 10 if pts % 10 == 0 else pts % 10
                cur_val = 20 if is_bb else score
                if cur_val > best["score"]:
                    name = f"宝宝({sub[0]})" if is_bb else (f"牛{score}" if score < 10 else "牛牛")
                    best = {"type": name, "score": cur_val, "base": base, "sub": sub}
    return best

# --- UI 逻辑 ---
if 'cards' not in st.session_state:
    st.session_state.cards = []

# 显示屏
st.markdown(f"""
    <div style="background-color: black; padding: 20px; border-radius: 15px; text-align: right; margin-bottom: 20px;">
        <p style="color: white; font-size: 14px; margin: 0;">当前选择 ({len(st.session_state.cards)}/5)</p>
        <h1 style="color: white; font-size: 40px; margin: 0;">{' '.join(st.session_state.cards) if st.session_state.cards else '0'}</h1>
    </div>
    """, unsafe_allow_html=True)

# 按钮矩阵
keys = [
    ['A', 'J', 'Q', 'K'],
    ['7', '8', '9'],
    ['4', '5', '6'],
    ['1', '2', '3'],
    ['10']
]

for row in keys:
    cols = st.columns(len(row))
    for i, key in enumerate(row):
        if cols[i].button(key):
            if len(st.session_state.cards) < 5:
                st.session_state.cards.append(key)
                st.rerun()

st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
if st.button("AC / 清空重选"):
    st.session_state.cards = []
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 结果弹窗
if len(st.session_state.cards) == 5:
    res = solve(st.session_state.cards)
    if res["score"] != -1:
        st.balloons()
        st.info(f"结果：{res['type']}")
        st.write(f"底：{res['base']} | 分：{res['sub']}")
    else:
        st.error("结果：没牛")
