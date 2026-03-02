import streamlit as st
from itertools import combinations

# =========================
# 页面基础配置
# =========================
st.set_page_config(page_title="牛牛计算器", layout="centered")

# 只保留最基础的按键加高 CSS，方便手指点击 (User Friendly)
st.markdown("""
    <style>
    .stButton > button {
        height: 60px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    /* 让结果提示框更大更醒目 */
    .stAlert {
        font-size: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# 核心算法逻辑
# =========================
def get_val(c):
    if c in ['J', 'Q', 'K', '10']: return 10
    if c == 'A': return 1
    return int(c)

def solve(cards):
    cards = tuple(c.upper() for c in cards)
    hands = {cards}
    for i, c in enumerate(cards):
        tmp = set()
        for h in hands:
            lst = list(h)
            if c == '3': lst[i] = '6'; tmp.add(tuple(lst))
            elif c == '6': lst[i] = '3'; tmp.add(tuple(lst))
        hands.update(tmp)

    best = {"type": "没牛", "score": -1, "base": None, "sub": None}
    for h in hands:
        for b_idx in combinations(range(5), 3):
            s_idx = [i for i in range(5) if i not in b_idx]
            base, sub = [h[i] for i in b_idx], [h[i] for i in s_idx]
            if sum(get_val(x) for x in base) % 10 == 0:
                is_bb = (get_val(sub[0]) == get_val(sub[1]))
                pts = sum(get_val(x) for x in sub)
                score = 10 if pts % 10 == 0 else pts % 10
                cur_v = 20 if is_bb else score
                if cur_v > best["score"]:
                    best = {"type": f"宝宝({sub[0]})" if is_bb else (f"牛{score}" if score < 10 else "牛牛"),
                            "score": cur_v, "base": base, "sub": sub}
    return best

# =========================
# 状态管理
# =========================
if 'cards' not in st.session_state:
    st.session_state.cards = []

# =========================
# UI 界面 - User Friendly 版
# =========================
st.title("🃏 牛牛智能计算器")
st.caption("支持 3/6 互变与宝宝对子规则")

# 1. 顶部状态与显示屏 (使用原生组件，干净清爽)
st.markdown(f"**已选牌数： {len(st.session_state.cards)} / 5**")

# 用一个好看的代码块来展示当前手牌
display_str = "  ".join(st.session_state.cards) if st.session_state.cards else "请在下方点击选牌..."
st.info(f"### {display_str}")

# 2. 独立的操作区 (防误触)
col_del, col_clear = st.columns(2)
with col_del:
    if st.button("🔙 退格", use_container_width=True):
        if st.session_state.cards:
            st.session_state.cards.pop()
            st.rerun()
with col_clear:
    if st.button("🗑️ 清空重选", type="primary", use_container_width=True):
        st.session_state.cards = []
        st.rerun()

st.divider()

# 3. 选牌区 (自然排版)
keys = [
    ['A', '2', '3', '4'],
    ['5', '6', '7', '8'],
    ['9', '10', 'J', 'Q']
]

for row in keys:
    cols = st.columns(4)
    for i, key in enumerate(row):
        if cols[i].button(key, use_container_width=True):
            if len(st.session_state.cards) < 5:
                st.session_state.cards.append(key)
                st.rerun()

# K 单独放中间，或者按常规对齐
cols_last = st.columns(4)
if cols_last[0].button("K", use_container_width=True):
    if len(st.session_state.cards) < 5:
        st.session_state.cards.append("K")
        st.rerun()

st.divider()

# =========================
# 结果展示区
# =========================
if len(st.session_state.cards) == 5:
    res = solve(st.session_state.cards)
    if res["score"] != -1:
        st.success(f"## 🎉 结果：{res['type']}")
        
        # 用两列清晰展示底牌和分牌
        res_col1, res_col2 = st.columns(2)
        res_col1.metric("底牌 (凑10的倍数)", " ".join(res['base']))
        res_col2.metric("分牌 (决定点数)", " ".join(res['sub']))
    else:
        st.error("## 💀 没牛（乌龙）")
        st.write("这把运气一般，点击上方 **清空重选** 继续吧！")
