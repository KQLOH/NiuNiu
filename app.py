import streamlit as st
from itertools import combinations

# 页面设置
st.set_page_config(page_title="牛牛计算器 Pro", layout="wide")

# ==========================
# 🎯 真正 4x4 Grid 布局 CSS
# ==========================
st.markdown("""
<style>

/* 页面整体缩小 */
.block-container {
    padding: 10px !important;
}

/* 显示屏 */
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

/* 4x4 Grid 容器 */
.keyboard {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}

/* 按钮 */
.keyboard button {
    width: 100%;
    height: 55px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 14px;
    border: none;
}

/* 手机优化 */
@media (max-width: 480px) {
    .keyboard button {
        height: 48px;
        font-size: 16px;
    }
}

</style>
""", unsafe_allow_html=True)

# ==========================
# 🧠 算法
# ==========================
def get_val(c):
    if c in ['J', 'Q', 'K', '10']:
        return 10
    if c == 'A':
        return 1
    return int(c)

def solve(cards):
    cards = tuple(c.upper() for c in cards)
    hands = {cards}

    # 3 和 6 互换
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

# ==========================
# 状态
# ==========================
if "cards" not in st.session_state:
    st.session_state.cards = []

# ==========================
# UI
# ==========================
st.title("🃏 牛牛计算器")

display = " ".join(st.session_state.cards) if st.session_state.cards else "READY"

st.markdown(f"""
<div class="display-screen">
    <div style="font-size:12px;color:#8e8e93;">
        已选 {len(st.session_state.cards)} / 5
    </div>
    <div style="font-size:30px;font-weight:bold;color:#007aff;">
        {display}
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================
# 🎯 4x4 键盘
# ==========================
keys = [
    'A','2','3','4',
    '5','6','7','8',
    '9','10','J','Q',
    'K','RE','AC',''
]

st.markdown('<div class="keyboard">', unsafe_allow_html=True)

for key in keys:
    if key == "":
        st.markdown("<div></div>", unsafe_allow_html=True)
    elif key == "AC":
        if st.button("AC"):
            st.session_state.cards = []
            st.rerun()
    elif key == "RE":
        if st.button("RE"):
            if st.session_state.cards:
                st.session_state.cards.pop()
                st.rerun()
    else:
        if st.button(key):
            if len(st.session_state.cards) < 5:
                st.session_state.cards.append(key)
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ==========================
# 自动结果
# ==========================
if len(st.session_state.cards) == 5:
    res = solve(st.session_state.cards)

    if res["score"] != -1:
        st.success(f"### {res['type']}")
        st.info(f"摆法：底[{' '.join(res['base'])}] 分[{' '.join(res['sub'])}]")
    else:
        st.error("### 结果：没牛")
