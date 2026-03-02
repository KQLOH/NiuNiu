import streamlit as st
from itertools import combinations

def get_value(card):
    if card in ['J', 'Q', 'K', '10']: return 10
    if card == 'A': return 1
    return int(card)

def calculate_niuniu(cards, swap_36=True, baobao=True):
    best_result = {"type": "没牛", "score": -1, "sub_type": ""}
    
    # 处理 3/6 互换逻辑
    possible_hands = [cards]
    if swap_36:
        for i, card in enumerate(cards):
            if card == '3':
                new_hand = list(cards)
                new_hand[i] = '6'
                possible_hands.append(tuple(new_hand))
            elif card == '6':
                new_hand = list(cards)
                new_hand[i] = '3'
                possible_hands.append(tuple(new_hand))

    for hand in set(possible_hands):
        # 尝试所有 3 张牌作为底牌的组合
        for base_indices in combinations(range(5), 3):
            other_indices = [i for i in range(5) if i not in base_indices]
            
            base_cards = [hand[i] for i in base_indices]
            sub_cards = [hand[i] for i in other_indices]
            
            base_sum = sum(get_value(c) for c in base_cards)
            
            if base_sum % 10 == 0:
                # 检查宝宝 (对子)
                is_baobao = baobao and (get_value(sub_cards[0]) == get_value(sub_cards[1]))
                
                # 计算点数
                sub_sum = sum(get_value(c) for c in sub_cards)
                score = 10 if sub_sum % 10 == 0 else sub_sum % 10
                
                res_type = f"牛{score}" if score < 10 else "牛牛"
                if is_baobao: res_type = f"{sub_cards[0]}{sub_cards[1]} 宝宝"
                
                current_score = 20 if is_baobao else score
                if current_score > best_result["score"]:
                    best_result = {
                        "type": res_type,
                        "score": current_score,
                        "base": base_cards,
                        "sub": sub_cards
                    }
    return best_result

st.title("牛牛计算器 (Pro版)")
st.write("规则：3/6互变 + 宝宝对子")

input_cards = st.text_input("输入5张牌 (用空格隔开，如: 7 6 2 6 2)", "7 6 2 6 2").split()

if len(input_cards) == 5:
    res = calculate_niuniu(input_cards)
    st.divider()
    st.subheader(f"结果：{res['type']}")
    if res['score'] != -1:
        st.success(f"底牌：{res['base']}")
        st.success(f"分牌：{res['sub']}")
    else:
        st.error("这把没牛...")
