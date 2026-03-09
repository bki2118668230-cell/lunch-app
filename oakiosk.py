import streamlit as st
import requests
import json
import time

# --- 1. [비밀 금고에서 주소 꺼내오기] ---
try:
    SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK"]
except:
    SLACK_WEBHOOK_URL = "" 

# --- 2. [핵심] 장소별 맞춤 보물지도 & 해결책 설정 ---
INVENTORY_DATA = {
    "🏢 사무실 1-1 구역 OA": {
        "🧻 티슈": "OA실 공용 캐비닛 1번 칸",
        "💦 물티슈": "복합기 바로 옆 선반",
        "🔋 건전지": "비품 서랍장 두 번째 칸",
        "🖨️ 복합기 작동 불가!": "복합기 우측 하단 전원버튼을 껐다 켜주세요"  # 👈 추가 완료!
    },
    "🏢 사무실 1-2 구역 OA": {
        "🧻 티슈": "OA실 공용 캐비닛 1번 칸",
        "💦 물티슈": "복합기 바로 옆 선반",
        "🔋 건전지": "비품 서랍장 두 번째 칸",
        "🧴 퐁퐁": "탕비실 싱크대 아래 하부장",
        "🧽 수세미": "탕비실 싱크대 상부장 왼쪽",
        "🖨️ 복합기 작동 불가!": "복합기 우측 하단 전원버튼을 껐다 켜주세요"  # 👈 추가 완료!
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
    
    st.markdown("### 앗! 필요한 비품이나 도움이 필요한가요?\n아래에서 해당하는 항목을 선택해주세요.")
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

# --- 화면 2단계: 숨겨진 보관소(해결책) 안내 및 슬랙 전송 ---
elif st.session_state.step == 2:
    loc = st.session_state.selected_location
    item = st.session_state.selected_item
    
    hidden_spot = INVENTORY_DATA[loc][item]
    
    # 누른 버튼이 복합기인지 비품인지에 따라 인사말 다르게 하기!
    if "복합기" in item:
        st.title("🖨️ 복합기에 문제가 생겼군요! 💦")
        st.info(f"💡 **총무팀에 연락하기 전에 먼저 이렇게 해보시겠어요?**\n\n👉 **{hidden_spot}**")
    else:
        st.title(f"[{item}] 찾으시나요? 👀")
        st.info(f"💡 **잠깐만요!**\n\n현재 계신 **{loc}**의 **[{hidden_spot}]**에 항상 여분을 채워두고 있습니다. 총무팀에 요청하기 전, 먼저 확인해 주시겠어요?")
        
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎉 앗, 해결했어요! (종료)", type="primary", use_container_width=True):
            st.success("다행이네요! 오늘도 좋은 하루 보내세요! (2초 뒤 처음으로 돌아갑니다)")
            time.sleep(2)
            st.session_state.step = 1
            st.session_state.selected_item = None
            st.rerun()
            
    with col2:
        # 🚨 여기서도 버튼 이름을 상황에 맞게 조금 센스있게!
        btn_text = "🚨 헐... 그래도 안 돼요!" if "복합기" in item else "🚨 헐... 거기도 텅 비었어요!"
        
        if st.button(btn_text, type="secondary", use_container_width=True):
            
            st.success("✅ 총무팀에 전달되었습니다. 빠른 시일 내에 확인하겠습니다. (2초 뒤 처음으로 돌아갑니다)")
            
            # 슬랙 요정이 눈치껏 다르게 말함!
            if SLACK_WEBHOOK_URL != "":
                if "복합기" in item:
                    slack_msg = {"text": f"<@U04DBLZ8TDW> 님! 🚨 {loc} 복합기가 고장 났대요! 전원 껐다 켜도 안 된대요! 확인해주세요! 😢"}
                else:
                    slack_msg = {"text": f"<@U04DBLZ8TDW> 님! {loc}에 {item} 비품이 다 떨어졌어요. 채워주세요! 😢"}
                
                try:
                    requests.post(SLACK_WEBHOOK_URL, data=json.dumps(slack_msg), headers={'Content-Type': 'application/json'})
                except:
                    pass
            
            time.sleep(2)
            st.session_state.step = 1
            st.session_state.selected_item = None
            st.rerun()
