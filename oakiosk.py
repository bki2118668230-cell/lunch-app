import streamlit as st
import requests
import json
import time

# -------------------------------------------------------------------
# 🚨 대장님이 발급받은 슬랙 웹훅 주소를 아래 따옴표 안에 꼭! 붙여넣으세요! 🚨
# -------------------------------------------------------------------
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# --- 2. [핵심] 장소별 맞춤 보물지도 설정 ---
# 대장님이 장소, 물건, 숨겨진 위치를 마음대로 찍어내는 공장입니다!
INVENTORY_DATA = {
    "🏢 3층 OA실": {
        "🧻 화장실 휴지": "복합기 옆 철제 캐비닛 2번째 칸",
        "📄 A4 복사 용지": "복합기 바로 밑 서랍장",
        "🔋 건전지 (AAA/AA)": "출입문 옆 작은 소품함 안"
    },
    "☕️ 5층 탕비실": {
        "🧻 화장실 휴지": "정수기 밑 하부장 왼쪽 칸",
        "☕️ 커피 원두": "싱크대 상부장 오른쪽 끝 칸",
        "🥤 종이컵": "커피머신 바로 아래 서랍"
    },
    "🛋️ 7층 라운지": {
        "🔋 건전지 (AAA/AA)": "TV 아래 서랍장 첫 번째 칸",
        "🧻 물티슈": "소파 옆 테이블 아래 바구니"
    }
}

# --- 페이지 설정 ---
st.set_page_config(page_title="브랜드웍스 비품 요정", page_icon="🧚", layout="centered")

# --- 상태 관리 ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_item' not in st.session_state:
    st.session_state.selected_item = None

# --- 화면 1단계: 장소 및 물품 선택 ---
if st.session_state.step == 1:
    st.title("🧚 무인 비품 요정")
    
    # 📍 1. 장소 선택 드롭다운 (여기서 고르면 아래 버튼들이 싹 바뀝니다!)
    selected_location = st.selectbox(
        "📍 현재 계신 곳을 선택해주세요:",
        list(INVENTORY_DATA.keys())
    )
    
    st.markdown("### 앗! 필요한 비품이 떨어졌나요?\n아래에서 찾으시는 물품을 꾹! 눌러주세요.")
    st.write("---")
    
    # 선택된 장소에 맞는 물품 리스트만 가져오기
    items_for_location = INVENTORY_DATA[selected_location]
    item_names = list(items_for_location.keys())
    
    # 물품 버튼들을 동적으로 생성 (가로 2줄로 예쁘게)
    for i in range(0, len(item_names), 2):
        col1, col2 = st.columns(2)
        with col1:
            if st.button(item_names[i], use_container_width=True):
                st.session_state.selected_item = item_names[i]
                st.session_state.selected_location = selected_location
                st.session_state.step = 2
                st.rerun()
        with col2:
            if i + 1 < len(item_names):
                if st.button(item_names[i+1], use_container_width=True):
                    st.session_state.selected_item = item_names[i+1]
                    st.session_state.selected_location = selected_location
                    st.session_state.step = 2
                    st.rerun()

# --- 화면 2단계: 숨겨진 보관소 안내 ---
elif st.session_state.step == 2:
    loc = st.session_state.selected_location
    item = st.session_state.selected_item
    
    # 선택한 장소의 해당 물품 숨겨진 위치 찰떡같이 가져오기!
    hidden_spot = INVENTORY_DATA[loc][item]
    
    st.title(f"{item} 찾으시나요?! 👀")
    st.info(f"💡 **잠깐만요!**\n\n현재 계신 **[{loc}]** 의 **[{hidden_spot}]** 에 항상 여분을 넉넉하게 채워두고 있습니다! 총무팀을 부르기 전에 먼저 거기를 확인해 주시겠어요?")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎉 앗, 찾았어요! (종료)", type="primary", use_container_width=True):
            st.success("다행이네요! 오늘도 좋은 하루 보내세요! (3초 뒤 처음으로 돌아갑니다)")
            time.sleep(3)
            st.session_state.step = 1
            st.session_state.selected_item = None
            st.rerun()
            
    with col2:
        if st.button("🚨 헐... 거기도 텅 비었어요!", type="secondary", use_container_width=True):
            st.session_state.step = 3
            st.rerun()

# --- 화면 3단계: 장바구니 담기 (슬랙으로 알림 쏘기!) ---
elif st.session_state.step == 3:
    loc = st.session_state.selected_location
    item_name = st
