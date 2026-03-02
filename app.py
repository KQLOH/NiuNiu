import streamlit as st
from itertools import combinations

# 设置页面配置
st.set_page_config(page_title="牛牛高级计算器", layout="centered")

def get_value(card):
    """转换牌面点数为计算数值"""
    card = card.upper()
    if card in ['J', 'Q', 'K', '10']: return 10
    if card == 'A': return 1
    try:
        return int(card)
    except:
        return 0

def calculate_niuniu(cards, swap_36=True, baobao=True):
    """
    核心算法：支持 3/6 互换和宝宝规则
    """
    # 统一转为元组，避免 set() 报错
    cards = tuple(c.upper() for c in cards)
    possible_hands = {cards}
    
    if swap_36:
        # 生成所有 3/6 替换的组合
        for i, card in enumerate(cards):
            temp_hands = set()
            for hand in possible_hands:
                hand_list = list(hand)
                if card == '3':
                    hand_list[i] = '6'
                    temp_hands.add(tuple(hand_list))
                elif card == '6':
                    hand_list[i] = '3'
                    temp_hands.add(tuple(hand_list))
            possible_hands.update(temp_hands)

    best_result = {"type": "没牛", "score": -1, "base": None, "sub": None}

    for hand in possible_hands:
        # 尝试所有 3 张牌作为底牌
        for base_idx in combinations(range(5), 3):
            other_idx = [i for i in range(5) if i not in base_idx]
            
            base_cards = [hand[i] for i in base_idx]
            sub_cards = [hand[i] for i in other_idx]
            
            base_sum = sum(get_value(c) for c in base_cards)
            
            if base_sum % 10 == 0:
                # 逻辑：宝宝 (分牌数值一样)
                is_baobao = baobao and (get_value(sub_cards[0]) == get_value(sub_cards[1]))
                
                sub_sum = sum(get_value(c) for c in sub_cards)
                score = 10 if sub_sum % 10 == 0 else sub_sum % 10
                
                # 权重计算：宝宝(20) > 牛牛(10) > 牛1-9
                current_score = 20 if is_baobao else score
                
                if current_score > best_result["score"]:
                    res_type = f"牛{score}" if score < 10 else "牛牛"
                    if is_baobao:
                        res_type = f"宝宝 ({sub_cards[0]} 对子)"
                        
                    best_result = {
                        "type": res_type,
                        "score": current_score,
                        "base": base_cards,
                        "sub": sub_cards
                    }
    return best_result

# UI 部分
st.title("🃏 牛牛专业计算器")
st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.header("规则设置")
    use_swap = st.checkbox("开启 3/6 互换", value=True)
    use_baobao = st.checkbox("开启 宝宝对子", value=True)
    st.info("注：J Q K 均计为 10 点")

# 输入框
user_input = st.text_input("请输入 5 张牌（用空格隔开）", placeholder="例如: 7 6 2 6 2")

if user_input:
    cards = user_input.split()
    if len(cards) != 5:
        st.warning("请输入刚好 5 张牌！")
    else:
        result = calculate_niuniu(cards, use_swap, use_baobao)
        
        if result["score"] != -1:
            st.balloons()
            st.success(f"### 最终结果：{result['type']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("底牌 (凑倍数)", " / ".join(result['base']))
            with col2:
                st.metric("分牌 (点数)", " / ".join(result['sub']))
        else:
            st.error("### 结果：没牛（乌龙）")
            st.info("换把牌试试吧！")

st.markdown("---")
st.caption("Developed for personal use | Rules: 3=6 Swap & Baobao")
