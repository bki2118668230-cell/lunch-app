import streamlit as st
import requests
import json
import time

# --- 1. [비밀 금고에서 주소 꺼내오기] ---
# 대장님이 스트림릿 설정(Secrets)에 숨겨둔 주소를 몰래 꺼내옵니다.
try:
    SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK"]
except:
    SLACK_WEBHOOK_URL = "" # 설정 안 되어있으면 무시

# --- 2. [핵심] 장소별 맞춤 보물지도 설정 ---
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
    
    selected_location = st.selectbox(
        "📍 현재 계신 곳을 선택해주세요:",
        list(INVENTORY_DATA.keys())
    )
    
    st.markdown("### 앗! 필요한 비품이 떨어졌나요?\n아래에서 찾으시는 물품을 꾹! 눌러주세요.")
    st.write("---")
    
    items_for_location = INVENTORY_DATA[selected_location]
    item_names = list(items_for_location.keys())
    
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

# --- 화면 2단계: 숨겨진 보관소 안내 및 슬랙 전송 ---
elif st.session_state.step == 2:
    loc = st.session_state.selected_location
    item = st.session_state.selected_item
    
    hidden_spot = INVENTORY_DATA[loc][item]
    
    st.title(f"{item} 찾으시나요?! 👀")
    st.info(f"💡 **잠깐만요!**\n\n현재 계신 **[{loc}]** 의 **[{hidden_spot}]** 에 항상 여분을 넉넉하게 채워두고 있습니다! 총무팀을 부르기 전에 먼저 거기를 확인해 주시겠어요?")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        # [왼쪽 버튼] 앗 찾았어요!
        if st.button("🎉 앗, 찾았어요! (종료)", type="primary", use_container_width=True):
            st.success("다행이네요! 오늘도 좋은 하루 보내세요! (2초 뒤 처음으로 돌아갑니다)")
            time.sleep(2)
            st.session_state.step = 1
            st.session_state.selected_item = None
            st.rerun()
            
    with col2:
        # [오른쪽 버튼] 헐 거기도 텅 비었어요! (대장님 요청 디자인 반영!)
        if st.button("🚨 헐... 거기도 텅 비었어요!", type="secondary", use_container_width=True):
            
            # 1. 앗 찾았어요 처럼 크고 듬직한 초록색 알림창 띄우기!
            st.success("✅ 총무 공지방에 전달 하였습니다! 빠른 시일 내에 꽉꽉 채워둘게요! (2초 뒤 처음으로 돌아갑니다)")
            
            # 2. 슬랙으로 알림 발사!
            if SLACK_WEBHOOK_URL != "":
                slack_msg = {
                    "blocks": [
                        {"type": "header", "text": {"type": "plain_text", "text": "🚨 [비품 충전 SOS!]", "emoji": True}},
                        {"type": "section", "text": {"type": "mrkdwn", "text": f"*📍 호출 장소:* {loc}\n*📦 요청 품목:* {item}\n\n*대장님! 숨겨둔 여분까지 다 떨어졌습니다! 빠른 충전 부탁드립니다! 🛒*"}}
                    ]
                }
                try:
                    requests.post(SLACK_WEBHOOK_URL, data=json.dumps(slack_msg), headers={'Content-Type': 'application/json'})
                except:
                    pass
            
            # 3. 2초 동안 초록색 알림창 보여주고 초기화면으로 뿅!
            time.sleep(2)
            st.session_state.step = 1
            st.session_state.selected_item = None
            st.rerun()
