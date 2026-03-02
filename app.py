import streamlit as st
from itertools import combinations

# 设置页面
st.set_page_config(page_title="牛牛计算器", layout="centered")

# --- 核心逻辑 (保持不变) ---
def get_value(card):
    if card in ['J', 'Q', 'K', '10']: return 10
    if card == 'A': return 1
    return int(card)

def calculate_niuniu(cards, swap_36=True, baobao=True):
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
                is_baobao = baobao and (get_value(sub_cards[0]) == get_value(sub_cards[1]))
                sub_sum = sum(get_value(c) for c in sub_cards)
                score = 10 if sub_sum % 10 == 0 else sub_sum % 10
                current_score = 20 if is_baobao else score
                if current_score > best_result["score"]:
                    best_result = {"type": f"宝宝 ({sub_cards[0]})" if is_baobao else (f"牛{score}" if score < 10 else "牛牛"),
                                   "score": current_score, "base": base_cards, "sub": sub_cards}
    return best_result

# --- UI 界面 ---
st.title("📱 快捷牛牛计算器")

# 初始化 Session State 用来存储选中的牌
if 'my_cards' not in st.session_state:
    st.session_state.my_cards = []

# 显示当前选中的牌
st.subheader("当前手牌：")
card_display = " ".join(st.session_state.my_cards)
st.info(card_display if card_display else "请点击下方按钮选牌")

# 模拟计算器键盘 (3列布局)
cols = st.columns(3)
keys = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

for i, key in enumerate(keys):
    with cols[i % 3]:
        if st.button(key, use_container_width=True):
            if len(st.session_state.my_cards) < 5:
                st.session_state.my_cards.append(key)
                st.rerun()

# 功能按钮：清空
if st.button("🔴 清空重选", use_container_width=True):
    st.session_state.my_cards = []
    st.rerun()

st.divider()

# 自动计算结果
if len(st.session_state.my_cards) == 5:
    res = calculate_niuniu(st.session_state.my_cards)
    if res["score"] != -1:
        st.success(f"### 结果：{res['type']}")
        st.write(f"**底牌：** {', '.join(res['base'])} | **分牌：** {', '.join(res['sub'])}")
    else:
        st.error("### 结果：没牛")
