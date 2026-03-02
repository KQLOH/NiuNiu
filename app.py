import streamlit as st
from itertools import combinations

# 页面基础配置
st.set_page_config(page_title="牛牛计算器 Pro", layout="centered")

# --- 核心 CSS：强制移动端不换行 ---
st.markdown("""
    <style>
    /* 核心：强制所有列在手机上依然并排，不堆叠 */
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }
    
    /* 按钮样式优化 */
    .stButton > button {
        width: 100% !important;
        height: 60px !important;
        padding: 0px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }

    /* 显示屏样式 */
    .display-screen {
        background-color: #1c1c1e;
        color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        text-align: right;
        margin-bottom: 15px;
        border: 1px solid #3a3a3c;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 核心算法逻辑 (已修正 TypeError) ---
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

# --- 状态管理 ---
if 'cards' not in st.session_state:
    st.session_state.cards = []

# --- UI 界面 ---
st.title("🃏 牛牛计算器")

# 显示屏
display_str = " ".join(st.session_state.cards) if st.session_state.cards else "READY"
st.markdown(f'''
    <div class="display-screen">
        <div style="font-size: 12px; color: #8e8e93;">已选 {len(st.session_state.cards)} / 5</div>
        <div style="font-size: 32px; font-weight: bold; color: #007aff;">{display_str}</div>
    </div>
''', unsafe_allow_html=True)

# 功能键：AC 和 Redo (并排)
c_func1, c_func2 = st.columns(2)
if c_func1.button("AC (清空)", type="primary", use_container_width=True):
    st.session_state.cards = []
    st.rerun()
if c_func2.button("RE (退格)", use_container_width=True):
    if st.session_state.cards:
        st.session_state.cards.pop()
        st.rerun()

# 键盘矩阵：每行 4 个按钮
keys = [
    ['A', '2', '3', '4'],
    ['5', '6', '7', '8'],
    ['9', '10', 'J', 'Q'],
    ['K']
]

for row in keys:
    cols = st.columns(len(row))
    for i, key in enumerate(row):
        if cols[i].button(key, use_container_width=True):
            if len(st.session_state.cards) < 5:
                st.session_state.cards.append(key)
                st.rerun()

st.divider()

# 自动结果
if len(st.session_state.cards) == 5:
    res = solve(st.session_state.cards)
    if res["score"] != -1:
        st.success(f"### {res['type']}")
        st.info(f"摆法：底[{' '.join(res['base'])}] 分[{' '.join(res['sub'])}]")
    else:
        st.error("### 结果：没牛")
