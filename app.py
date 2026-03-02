import streamlit as st
from itertools import combinations

# 页面基础配置：默认折叠侧边栏，居中
st.set_page_config(page_title="牛牛计算器", layout="centered", initial_sidebar_state="collapsed")

# --- 终极核弹 CSS：绝对锁死屏幕，禁止任何滑动 ---
st.markdown("""
    <style>
    /* 1. 彻底禁用 HTML 和 Body 的滚动、回弹和默认外边距 */
    html, body, [class*="css"] {
        overflow: hidden !important;
        touch-action: none !important; /* 禁止手势滑动 */
        overscroll-behavior: none !important; /* 禁止橡皮筋回弹 */
        margin: 0 !important;
        padding: 0 !important;
        height: 100vh !important;
    }
    
    /* 2. 隐藏 Streamlit 所有的顶部装饰、菜单和底部水印 */
    header {display: none !important;}
    footer {display: none !important;}
    
    /* 3. 清除主容器的所有留白，让内容100%贴合屏幕 */
    .block-container {
        padding: 1rem 0.5rem 0rem 0.5rem !important;
        max-width: 100% !important;
        overflow: hidden !important;
    }

    /* 4. 强制键盘行不换行，缩进间距 */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 6px !important;
        margin-bottom: 6px !important;
    }
    
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }
    
    /* 5. 动态按键高度：根据屏幕高度自动伸缩 (vh)，保证刚好塞满一屏 */
    .stButton > button {
        width: 100% !important; 
        height: 10vh !important; /* 屏幕高度的 10% */
        min-height: 55px !important;
        padding: 0px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        background-color: #2c2c2e !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton > button:active {
        background-color: #636366 !important;
    }

    /* AC和退格键特殊颜色 */
    div[data-testid="column"]:nth-child(2) button:contains("RE"),
    div[data-testid="column"]:nth-child(3) button:contains("AC") {
        background-color: #ff3b30 !important;
    }

    /* 6. 显示屏样式：动态高度 */
    .display-screen {
        box-sizing: border-box !important;
        width: 100% !important;
        height: 14vh !important;
        background-color: #000000;
        color: #ffffff;
        padding: 15px;
        border-radius: 16px;
        text-align: right;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* 自定义结果框，替代原本会撑开屏幕的 st.success */
    .result-box {
        margin-top: 10px;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
    }
    .res-win { background-color: #34c759; color: white; }
    .res-lose { background-color: #ff3b30; color: white; }
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

# 1. 顶部纯黑显示屏
display_str = " ".join(st.session_state.cards) if st.session_state.cards else "0"
st.markdown(f'''
    <div class="display-screen">
        <div style="font-size: 14px; color: #8e8e93; margin-bottom: 5px;">COUNT: {len(st.session_state.cards)} / 5</div>
        <div style="font-size: 40px; font-weight: bold; color: #ffffff;">{display_str}</div>
    </div>
''', unsafe_allow_html=True)

# 2. 键盘矩阵：4x4 布局
keys = [
    ['A', '2', '3', '4'],
    ['5', '6', '7', '8'],
    ['9', '10', 'J', 'Q'],
    ['K', 'RE', 'AC', '']  
]

for row in keys:
    cols = st.columns(4) 
    for i, key in enumerate(row):
        if key == 'AC':
            if cols[i].button("AC"):
                st.session_state.cards = []
                st.rerun()
        elif key == 'RE':
            if cols[i].button("RE"):
                if st.session_state.cards:
                    st.session_state.cards.pop()
                    st.rerun()
        elif key != '':
            if cols[i].button(key):
                if len(st.session_state.cards) < 5:
                    st.session_state.cards.append(key)
                    st.rerun()

# 3. 自定义结果展示（固定大小，不会撑开页面）
if len(st.session_state.cards) == 5:
    res = solve(st.session_state.cards)
    if res["score"] != -1:
        st.markdown(f'''
            <div class="result-box res-win">
                🔥 {res['type']} <br>
                <span style="font-size:14px; font-weight:normal;">底: {' '.join(res['base'])} | 分: {' '.join(res['sub'])}</span>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('<div class="result-box res-lose">💀 没牛</div>', unsafe_allow_html=True)
else:
    # 占位符，防止高度塌陷
    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
