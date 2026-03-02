import streamlit as st
from itertools import combinations

# 页面基础配置
st.set_page_config(page_title="牛牛计算器", layout="centered")

# --- 终极 CSS：专治手机端自动拉长 ---
st.markdown("""
    <style>
    /* 核心魔法：强制手机端所有列保持并排，绝不换行堆叠 */
    @media screen and (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
        }
        div[data-testid="column"] {
            width: auto !important;
            min-width: 0 !important;
            flex: 1 1 0% !important;
        }
    }
    
    /* 按钮整体样式优化，按键更饱满 */
    .stButton > button {
        width: 100% !important;
        height: 65px !important;
        padding: 0px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
    }

    /* 显示屏样式 */
    .display-screen {
        background-color: #1c1c1e;
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        text-align: right;
        margin-bottom: 20px;
        border: 1px solid #3a3a3c;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 核心算法逻辑 ---
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
st.title("📱 牛牛计算器")

# 显示屏
display_str = " ".join(st.session_state.cards) if st.session_state.cards else "等待选牌"
st.markdown(f'''
    <div class="display-screen">
        <div style="font-size: 14px; color: #8e8e93; margin-bottom: 5px;">已选 {len(st.session_state.cards)} / 5</div>
        <div style="font-size: 38px; font-weight: bold; color: #007aff;">{display_str}</div>
    </div>
''', unsafe_allow_html=True)

# 顶部功能键：AC 和 RE (设为 2 列，所以它们会比较长，各占一半)
c_func1, c_func2 = st.columns(2)
if c_func1.button("AC (清空)", type="primary"):
    st.session_state.cards = []
    st.rerun()
if c_func2.button("RE (退格)"):
    if st.session_state.cards:
        st.session_state.cards.pop()
        st.rerun()

# 键盘矩阵：A-K (设为 4 列，所以它们会变成窄窄的方格)
keys = [
    ['A', '2', '3', '4'],
    ['5', '6', '7', '8'],
    ['9', '10', 'J', 'Q']
]

# 前三排 4x4
for row in keys:
    cols = st.columns(4)
    for i, key in enumerate(row):
        if cols[i].button(key):
            if len(st.session_state.cards) < 5:
                st.session_state.cards.append(key)
                st.rerun()

# 最后一排单独放 K (同样按 4 列分配，保持格子一样小)
cols_last = st.columns(4)
if cols_last[0].button("K"):
    if len(st.session_state.cards) < 5:
        st.session_state.cards.append("K")
        st.rerun()

st.divider()

# 自动结果
if len(st.session_state.cards) == 5:
    res = solve(st.session_state.cards)
    if res["score"] != -1:
        st.success(f"### 🔥 {res['type']}")
        st.info(f"👉 摆法：底 [{' '.join(res['base'])}] | 分 [{' '.join(res['sub'])}]")
    else:
        st.error("### 💀 结果：没牛")
