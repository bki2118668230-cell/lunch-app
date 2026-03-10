import streamlit as st
import requests
import json
import time
import os

# --- 1. [비밀 금고에서 주소 꺼내오기] ---
try:
    SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK"]
except:
    SLACK_WEBHOOK_URL = "" 

# --- 2. [핵심] 장소별 맞춤 보물지도 & 해결책 설정 ---
# 🚨 대장님 명령대로 모든 구역 토너 교체 문구에 \n (줄바꿈) 완벽 적용!
INVENTORY_DATA = {
    "🏢 사무실 1-1 구역 OA": {
        "🧻 티슈": "쇼룸 우측 정수기 옆 첫번째 캐비닛",
        "💦 물티슈": "쇼룸 우측 정수기 옆 첫번째 두번째 캐비넷",
        "🔋 건전지": "복합기 옆 사무용품 보관함",
        "🖨️ 복합기 작동 불가!": "복합기 우측 하단 전원버튼을 껐다 켜주세요",
        "🖨️ 복합기 토너 교체": "복합기 하단 토너 보관함을 확인해주세요\n👉 복합기 화면가이드에 맞춰 교체 진행해주세요!"
    },
    "🏢 사무실 1-2 구역 OA": {
        "🧻 티슈": "OA실 싱크대 위 1번 칸",
        "💦 물티슈": "OA실 싱크대 위 우측 끝 ",
        "🔋 건전지": "OA실 책상 위 사무용품 보관함",
        "🧴 퐁퐁": "OA실 싱크대 위 2번쨰 선반",
        "🧽 수세미": "OA실 싱크대 위 2번째 선반",
        "🖨️ 복합기 작동 불가!": "복합기 우측 하단 전원버튼을 껐다 켜주세요",
        "🖨️ 복합기 토너 교체": "복합기 하단 토너 보관함을 확인해주세요\n👉 복합기 화면가이드에 맞춰 교체 진행해주세요!"
    },
    "🏢 사무실 2 구역 OA": {
        "🧻 티슈": "OA 하단 선반",
        "💦 물티슈": "OA 하단 선반 모나리자 박스",
        "🔋 건전지": "OA 우측 끝 사무용품 보관함",
        "🧴 퐁퐁": "싱크대 위 좌측 2번째 상부장",
        "🧽 수세미": "싱크대 위 1번째 상부장",
        "🖨️ 복합기 작동 불가!": "복합기 우측 하단 전원버튼을 껐다 켜주세요",
        "🖨️ 복합기 토너 교체": "복합기 하단 토너 보관함을 확인해주세요\n👉 복합기 화면가이드에 맞춰 교체 진행해주세요!"
    }
}

# --- 3. 📸 [사진 앨범 세팅 (구역별로 완전 분리!)] ---
IMAGE_DATA = {
    "🏢 사무실 1-1 구역 OA": {
        "🧻 티슈": "1-1_tissue.jpg",
        "💦 물티슈": "1-1_wipes.jpg",
        "🔋 건전지": "1-1_battery.jpg",
        "🖨️ 복합기 작동 불가!": "printer_error.png",
        "🖨️ 복합기 토너 교체": "toner.jpg" 
    },
    "🏢 사무실 1-2 구역 OA": {
        "🧻 티슈": "1-2_tissue.jpg",
        "💦 물티슈": "1-2_wipes.jpg",
        "🔋 건전지": "1-2_battery.jpg",
        "🧴 퐁퐁": "1-2_pongpong.jpg",
        "🧽 수세미": "1-2_sponge.jpg",
        "🖨️ 복합기 작동 불가!": "printer_error.png",
        "🖨️ 복합기 토너 교체": "toner.jpg" 
    },
    "🏢 사무실 2 구역 OA": {
        "🧻 티슈": "2_tissue.jpg",
        "💦 물티슈": "2_wipes.jpg",
        "🔋 건전지": "2_battery.jpg",
        "🧴 퐁퐁": "2_pongpong.jpg",
        "🧽 수세미": "2_sponge.jpg",
        "🖨️ 복합기 작동 불가!": "printer_error.png",
        "🖨️ 복합기 토너 교체": "toner.jpg" 
    }
}

# --- 페이지 설정 ---
st.set_page_config(page_title="브랜드웍스 비품 요정", page_icon="🧚", layout="centered")

# 🚨 [초강력 스크롤 마법 추가] 1-2구역 탭에서도 무조건 스크롤 되게 만들기! 🚨
st.markdown("""
    <style>
    /* 1. 어떤 브라우저든 화면 전체 스크롤 무조건 허용 */
    html, body, [data-testid="stAppViewContainer"], .main {
        overflow-y: auto !important;
        touch-action: pan-y !important;
    }
    
    /* 2. 사진 크기 최적화 및 터치 먹통 방어막(pointer-events) 설치! */
    [data-testid="stImage"] img {
        max-height: 40vh !important; /* 버튼이 잘 보이게 사진 높이를 조금 더 줄임 (45->40) */
        object-fit: contain !important;
        border-radius: 10px; 
        pointer-events: none !important; /* 🔥 핵심: 사진 위를 터치해도 스크롤이 되게 만듦! */
    }
    
    /* 3. 화면 맨 밑에 숨쉴 공간을 줘서 버튼이 위로 쑥 올라오게 함 */
    .block-container {
        padding-bottom: 5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 상태 관리 ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_item' not in st.session_state:
    st.session_state.selected_item = None
if 'selected_location' not in st.session_state:
    st.session_state.selected_location = list(INVENTORY_DATA.keys())[0]

# --- 화면 1단계: 장소 및 물품 선택 ---
if st.session_state.step == 1:
    st.title("🧚 무인 비품 요정")
    
    locations_list = list(INVENTORY_DATA.keys())
    
    if st.session_state.selected_location in locations_list:
        default_idx = locations_list.index(st.session_state.selected_location)
    else:
        default_idx = 0
        
    current_loc = st.selectbox(
        "📍 현재 계신 구역을 선택해주세요:",
        locations_list,
        index=default_idx
    )
    
    st.session_state.selected_location = current_loc
    
    st.markdown("### 앗! 필요한 비품이나 도움이 필요한가요?\n아래에서 해당하는 항목을 선택해주세요.")
    st.write("---")
    
    items_for_location = INVENTORY_DATA[current_loc]
    item_names = list(items_for_location.keys())
    
    for i in range(0, len(item_names), 2):
        col1, col2 = st.columns(2)
        with col1:
            if st.button(item_names[i], use_container_width=True):
                st.session_state.selected_item = item_names[i]
                st.session_state.step = 2
                st.rerun()
        with col2:
            if i + 1 < len(item_names):
                if st.button(item_names[i+1], use_container_width=True):
                    st.session_state.selected_item = item_names[i+1]
                    st.session_state.step = 2
                    st.rerun()

# --- 화면 2단계: 숨겨진 보관소(사진) 안내 및 슬랙 전송 ---
elif st.session_state.step == 2:
    loc = st.session_state.selected_location
    item = st.session_state.selected_item
    
    hidden_spot = INVENTORY_DATA[loc][item]
    image_file = IMAGE_DATA.get(loc, {}).get(item, "")
    
    if "작동 불가" in item:
        st.title("🖨️ 복합기에 문제가 생겼군요! 💦")
        if image_file != "" and os.path.exists(image_file):
            st.image(image_file, use_container_width=True)
        st.info(f"💡 **총무팀에 연락하기 전에 먼저 이렇게 해보시겠어요?**\n\n👉 **{hidden_spot}**")
        btn_text = "🚨 헐... 그래도 안 돼요!"
        
    elif "토너" in item:
        st.title("🖨️ 토너 교체가 필요하시군요! 💦")
        if image_file != "" and os.path.exists(image_file):
            st.image(image_file, use_container_width=True)
        st.info(f"💡 **총무팀에 연락하기 전에 먼저 확인해 주시겠어요?**\n\n👉 **{hidden_spot}**")
        btn_text = "🚨 헐... 거기도 여분이 없어요(또는 못하겠어요)!"
        
    else:
        st.title(f"[{item}] 찾으시나요? 👀")
        if image_file != "" and os.path.exists(image_file):
            st.image(image_file, use_container_width=True)
        st.info(f"💡 **잠깐만요!**\n\n현재 계신 **{loc}**의 **[{hidden_spot}]**에 항상 여분을 채워두고 있습니다. 총무팀에 요청하기 전, 먼저 확인해 주시겠어요?")
        btn_text = "🚨 헐... 거기도 텅 비었어요!"
        
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
        if st.button(btn_text, type="secondary", use_container_width=True):
            st.success("✅ 총무팀에 전달되었습니다. 빠른 시일 내에 확인하겠습니다. (2초 뒤 처음으로 돌아갑니다)")
            
            if SLACK_WEBHOOK_URL != "":
                if "작동 불가" in item:
                    slack_msg = {"text": f"<@U04DBLZ8TDW> 님! 🚨 {loc} 복합기가 고장 났대요! 전원 껐다 켜도 안 된대요! 확인해주세요! 😢"}
                elif "토너" in item:
                    slack_msg = {"text": f"<@U04DBLZ8TDW> 님! 🚨 {loc} 복합기 토너가 다 떨어졌대요! 확인 및 교체가 필요합니다! 😢"}
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
