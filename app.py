import streamlit as st
from itertools import combinations

st.set_page_config(page_title="牛牛计算器 Pro", layout="wide")

# =========================
# 手机优化 CSS：无缝拼接版
# =========================
st.markdown("""
<style>

/* 页面边距缩小 */
.block-container {
    padding: 10px !important;
}

/* 强制一行4列，不换行，且【消除所有缝隙】 */
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 0px !important; /* 关键：间距为0 */
}

/* 每列平均分，且【消除内边距】 */
[data-testid="column"] {
    flex: 1 1 0% !important;
    min-width: 0px !important;
    padding: 0px !important; /* 关键：内边距为0 */
}

/* 按钮样式：变成直角方块，完全贴合 */
.stButton > button {
    width: 100% !important;
    height: 60px !important;
    font-size: 20px !important;
    font-weight: bold;
    border-radius: 0px !important; /* 关键：去掉圆角才能无缝拼接 */
    border: 1px solid #3a3a3c !important; /* 加上暗色细边框，防止按键糊成一团 */
    margin: 0px !important;
}

/* 按下去的颜色反馈 */
.stButton > button:active {
    background-color: #636366 !important;
}

.display-screen {
    box-sizing: border-box;
    width: 100%;
    background-color: #1c1c1e;
    color: white;
    padding: 12px;
    border-radius: 15px;
    text-align: right;
    margin-bottom: 15px;
    border: 1px solid #3a3a3c;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 算法
# =========================
def get_val(c):
    if c in ['J', 'Q', 'K', '10']:
        return 10
    if c == 'A':
        return 1
    return int(c)

def solve(cards):
    cards = tuple(c.upper() for c in cards)
    hands = {cards}

    for i, c in enumerate(cards):
        tmp = set()
        for h in hands:
            lst = list(h)
            if c == '3':
                lst[i] = '6'
                tmp.add(tuple(lst))
            elif c == '6':
                lst[i] = '3'
                tmp.add(tuple(lst))
        hands.update(tmp)

    best = {"type": "没牛", "score": -1, "base": None, "sub": None}

    for h in hands:
        for b_idx in combinations(range(5), 3):
            s_idx = [i for i in range(5) if i not in b_idx]
            base = [h[i] for i in b_idx]
            sub = [h[i] for i in s_idx]

            if sum(get_val(x) for x in base) % 10 == 0:
                is_bb = (get_val(sub[0]) == get_val(sub[1]))
                pts = sum(get_val(x) for x in sub)
                score = 10 if pts % 10 == 0 else pts % 10
                cur_v = 20 if is_bb else score

                if cur_v > best["score"]:
                    best = {
                        "type": f"宝宝({sub[0]})" if is_bb else (f"牛{score}" if score < 10 else "牛牛"),
                        "score": cur_v,
                        "base": base,
                        "sub": sub
                    }

    return best

# =========================
# 状态
# =========================
if "cards" not in st.session_state:
    st.session_state.cards = []

# =========================
# UI
# =========================
st.title("🃏 牛牛计算器")

display = " ".join(st.session_state.cards) if st.session_state.cards else "READY"

st.markdown(f"""
<div class="display-screen">
    <div style="font-size:12px;color:#8e8e93;">
        已选 {len(st.session_state.cards)} / 5
    </div>
    <div style="font-size:28px;font-weight:bold;color:#007aff;">
        {display}
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 真正固定 4x4
# =========================
keys = [
    ['A','2','3','4'],
    ['5','6','7','8'],
    ['9','10','J','Q'],
    ['K','RE','AC','']
]

for row in keys:
    cols = st.columns(4)
    for i, key in enumerate(row):

        if key == "":
            cols[i].empty()

        elif key == "AC":
            if cols[i].button("AC"):
                st.session_state.cards = []
                st.rerun()

        elif key == "RE":
            if cols[i].button("RE"):
                if st.session_state.cards:
                    st.session_state.cards.pop()
                    st.rerun()

        else:
            if cols[i].button(key):
                if len(st.session_state.cards) < 5:
                    st.session_state.cards.append(key)
                    st.rerun()

st.divider()

# =========================
# 自动计算
# =========================
if len(st.session_state.cards) == 5:
    res = solve(st.session_state.cards)

    if res["score"] != -1:
        st.success(f"### {res['type']}")
        st.info(f"摆法：底[{' '.join(res['base'])}] 分[{' '.join(res['sub'])}]")
    else:
        st.error("### 结果：没牛")
