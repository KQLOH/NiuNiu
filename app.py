import streamlit as st
from itertools import combinations

# 页面基础配置
st.set_page_config(page_title="牛牛计算器", layout="centered")

# --- 自定义 CSS 让 UI 更像手机 App ---
st.markdown("""
    <style>
    /* 调整按钮高度和字体 */
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px !important;
        font-weight: bold;
        border-radius: 12px;
    }
    /* 黑色显示屏效果 */
    .display-screen {
        background-color: #1c1c1e;
        color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        text-align: right;
        min-height: 100px;
        margin-bottom: 10px;
        border: 2px solid #3a3a3c;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 核心逻辑 ---
def get_value(card):
    card = card.upper()
    if card in ['J', 'Q', 'K', '10']: return 10
    if card == 'A': return 1
    return int(card)

def calculate_niuniu(cards, swap_36=True, baobao=True):
    # 统一转为元组，防止 set() 报错
    cards = tuple(c.upper() for c in cards)
    possible_hands = {cards}
    
    if swap_36:
        for i, card in enumerate(cards):
            temp_hands = set()
            for hand in possible_hands:
                hand_list = list(hand)
                if card == '3':
                    hand_list[i] = '6'; temp_hands.add(tuple(hand_list))
                elif card == '6':
                    hand_list[i] = '3'; temp_hands.add(tuple(hand_list))
            possible_hands.update(temp_hands)

    best_result = {"type": "没牛", "score": -1, "base": None, "sub": None}

    for hand in possible_hands:
        for base_idx in combinations(range(5), 3):
            other_idx = [i for i in range(5) if i not in base_idx]
            base_cards = [hand[i] for i in base_idx]
            sub_cards = [hand[i] for i in other_idx]
            if sum(get_value(c) for c in base_cards) % 10 == 0:
                # 宝宝规则：分牌点数一样
                is_baobao = baobao and (get_value(sub_cards[0]) == get_value(sub_cards[1]))
                sub_sum = sum(get_value(c) for c in sub_cards)
                score = 10 if sub_sum % 10 == 0 else sub_sum % 10
                current_score = 20 if is_baobao else score
                if current_score > best_result["score"]:
                    res_type = f"牛{score}" if score < 10 else "牛牛"
                    if is_baobao: res_type = f"宝宝 ({sub_cards[0]} 对子)"
                    best_result = {"type": res_type, "score": current_score, "base": base_cards, "sub": sub_cards}
    return best_result

# --- 初始化 Session State (存储状态) ---
if 'cards' not in st.session_state:
    st.session_state.cards = []

# --- UI 界面 ---
st.title("📱 牛牛计算器")

# 显示屏部分
display_text = " ".join(st.session_state.cards) if st.session_state.cards else "等待选牌..."
st.markdown(f'''
    <div class="display-screen">
        <div style="font-size: 14px; color: #8e8e93;">已选 {len(st.session_state.cards)} / 5</div>
        <div style="font-size: 36px; font-weight: bold; color: #007aff;">{display_text}</div>
    </div>
''', unsafe_allow_html=True)

# 功能键：AC 和 Redo
col_ac, col_redo = st.columns(2)
with col_ac:
    if st.button("AC (清空)", type="primary", use_container_width=True):
        st.session_state.cards = []
        st.rerun()
with col_redo:
    if st.button("Redo (退格)", use_container_width=True):
        if st.session_state.cards:
            st.session_state.cards.pop()
            st.rerun()

# 键盘布局 (4列)
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

# 结果显示
if len(st.session_state.cards) == 5:
    result = calculate_niuniu(st.session_state.cards)
    if result["score"] != -1:
        st.balloons()
        st.success(f"### 最终结果：{result['type']}")
        st.info(f"💡 摆法：底牌 [{', '.join(result['base'])}] | 分牌 [{', '.join(result['sub'])}]")
    else:
        st.error("### 结果：没牛（乌龙）")
else:
    st.info("请选满 5 张牌查看结果")

st.caption("规则：3/6 互通 | 相同点数分牌为宝宝")
