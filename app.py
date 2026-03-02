import streamlit as st
from itertools import combinations

# 页面基础配置：隐藏默认侧边栏，居中
st.set_page_config(page_title="牛牛计算器", layout="centered", initial_sidebar_state="collapsed")

# --- 终极核弹级 CSS：彻底干掉移动端自动换行 ---
st.markdown("""
    <style>
    /* 隐藏顶部白边、菜单和页脚，让它看起来像个原生 App */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 1. 强制所有水平区块在手机上【绝对不换行】 */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        margin-bottom: 8px !important;
    }
    
    /* 2. 强制每一列平分宽度 */
    div[data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
        width: auto !important;
        padding: 0 !important;
    }

    /* 3. 按钮整体样式：仿 iOS 计算器暗黑风 */
    .stButton > button {
        width: 100% !important;
        height: 70px !important;
        font-size: 26px !important;
        font-weight: 600 !important;
        border-radius: 16px !important;
        background-color: #333333 !important; /* 深灰色键 */
        color: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    
    /* 按下去的反馈感 */
    .stButton > button:active {
        background-color: #737373 !important;
    }

    /* AC 清空键：设置为苹果红/橙色 */
    .stButton > button[kind="primary"] {
        background-color: #ff3b30 !important; 
        color: white !important;
    }

    /* 显示屏样式优化 */
    .calc-screen {
        background-color: #000000;
        padding: 20px;
        border-radius: 20px;
        text-align: right;
        margin-bottom: 25px;
        margin-top: -30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 核心算牌逻辑 (保持之前的 3/6 互通与宝宝逻辑) ---
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

# --- 界面 ---

# 1. 纯黑显示屏
display_str = " ".join(st.session_state.cards) if st.session_state.cards else "0"
st.markdown(f'''
    <div class="calc-screen">
        <div style="font-size: 14px; color: #8e8e93; margin-bottom: 5px;">已选 {len(st.session_state.cards)} / 5</div>
        <div style="font-size: 42px; font-weight: bold; color: #ffffff; min-height: 50px;">{display_str}</div>
    </div>
''', unsafe_allow_html=True)

# 2. 顶部控制键 (2列)
c_top1, c_top2 = st.columns(2)
with c_top1:
    if st.button("AC", type="primary"):
        st.session_state.cards = []
        st.rerun()
with c_top2:
    if st.button("退格 (Del)"):
        if st.session_state.cards:
            st.session_state.cards.pop()
            st.rerun()

# 3. 键盘矩阵 (强制 4 列)
rows = [
    ['A', '2', '3', '4'],
    ['5', '6', '7', '8'],
    ['9', '10', 'J', 'Q']
]

for row in rows:
    cols = st.columns(4)
    for i, key in enumerate(row):
        if cols[i].button(key):
            if len(st.session_state.cards) < 5:
                st.session_state.cards.append(key)
                st.rerun()

# 最后一行单独处理 K (占据最左边1格，其余留空保持对齐)
cols = st.columns(4)
if cols[0].button("K"):
    if len(st.session_state.cards) < 5:
        st.session_state.cards.append("K")
        st.rerun()

# 4. 自动计算结果
if len(st.session_state.cards) == 5:
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    res = solve(st.session_state.cards)
    if res["score"] != -1:
        st.success(f"🔥 {res['type']}")
        st.info(f"👉 底牌: [{' '.join(res['base'])}] | 分牌: [{' '.join(res['sub'])}]")
    else:
        st.error("💀 没牛")
