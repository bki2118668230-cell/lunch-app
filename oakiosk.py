import streamlit as st
import requests
import json
import time

# --- 1. [비밀 금고에서 주소 꺼내오기] ---
try:
    SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK"]
except:
    SLACK_WEBHOOK_URL = "" 

# --- 2. [핵심] 장소별 맞춤 보물지도 설정 (리모델링 완료!) ---
INVENTORY_DATA = {
    "🏢 사무실 1-1 구역 OA": {
        "🧻 티슈": "OA실 공용 캐비닛 1번 칸",
        "💦 물티슈": "복합기 바로 옆 선반",
        "🔋 건전지": "비품 서랍장 두 번째 칸"
    },
    "🏢 사무실 1-2 구역 OA": {
        "🧻 티슈": "OA실 공용 캐비닛 1번 칸",
        "💦 물티슈": "복합기 바로 옆 선반",
        "🔋 건전지": "비품 서랍장 두 번째 칸",
        "🧴 퐁퐁": "탕비실 싱크대 아래 하부장",
        "🧽 수세미": "탕비실 싱크대 상부장 왼쪽"
    },
    "🏢 사무실 2 구역 OA": {
        "🧻 티슈": "OA실 공용 캐비닛 1번 칸",
        "💦 물티슈": "복합기 바로 옆 선반",
        "🔋 건전지": "비품 서랍장 두 번째 칸",
        "🧴 퐁퐁": "탕비실 싱크대 아래 하부장",
        "🧽 수세미": "탕비실 싱크대 상부장 왼쪽"
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
        "📍 현재 계신 구역을 선택해주세요:",
        list(INVENTORY_DATA.keys())
    )
    
    st.markdown("### 앗! 필요한 비품이 떨어졌나요?\n아래에서 찾으시는 물품을 선택해주세요.")
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
    
    st.title(f"[{item}] 찾으시나요? 👀")
    st.info(f"💡 **잠깐만요!**\n\n현재 계신 **{loc}**의 **[{hidden_spot}]**에 항상 여분을 채워두고 있습니다. 총무팀에 요청하기 전, 먼저 확인해 주시겠어요?")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎉 앗, 찾았어요! (종료)", type="primary", use_container_width=True):
            st.success("다행이네요! 오늘도 좋은 하루 보내세요! (2초 뒤 처음으로 돌아갑니다)")
            time.sleep(2)
            st.session_state.step = 1
            st.session_state.selected_item = None
            st.rerun()
            
    with col2:
        if st.button("🚨 헐... 거기도 텅 비었어요!", type="secondary", use_container_width=True):
            
            # 화면 알림창도 점잖게 수정
            st.success("✅ 총무팀에 전달되었습니다. 빠른 시일 내에 보충해 두겠습니다. (2초 뒤 처음으로 돌아갑니다)")
            
            # 요정 호들갑 끄고, 점잖고 깔끔한 슬랙 메시지로 변경!
            if SLACK_WEBHOOK_URL != "":
                slack_msg = {
                    "blocks": [
                        {"type": "header", "text": {"type": "plain_text", "text": "🔔 [비품 보충 요청]", "emoji": True}},
                        {"type": "section", "text": {"type": "mrkdwn", "text": f"*📍 요청 구역:* {loc}\n*📦 부족 품목:* {item}\n\n해당 구역의 여분 비품이 모두 소진되었습니다. 다음 발주 및 보충 시 확인 부탁드립니다."}}
                    ]
                }
                try:
                    requests.post(SLACK_WEBHOOK_URL, data=json.dumps(slack_msg), headers={'Content-Type': 'application/json'})
                except:
                    pass
            
            time.sleep(2)
            st.session_state.step = 1
            st.session_state.selected_item = None
            st.rerun()
