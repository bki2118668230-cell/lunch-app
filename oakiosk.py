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
INVENTORY_DATA = {
    "🏢 사무실 1-1 구역 OA": {
        "🧻 티슈": "쇼룸 우측 정수기 옆 캐비넷 안에 있습니다",
        "💦 물티슈": "쇼룸 우측 정수기 옆 캐니벳 안에 있습니다",
        "🔋 건전지": "복합기 옆 테이블 사무용품 보관함 안에 있습니다",
        "🖨️ 복합기 작동 불가!": "복합기 우측 하단 전원버튼을 껐다 켜주세요"
    },
    "🏢 사무실 1-2 구역 OA": {
        "🧻 티슈": "싱크대 위 선반 안에 있습니다",
        "💦 물티슈": "싱크대 우측 끝 선반 안에 있습니다",
        "🔋 건전지": "OA공간 내 테이블위 사무용품 보관함 안에 있습니다",
        "🧴 퐁퐁": "싱크대 위 2번째 선반 안에 있습니다",
        "🧽 수세미": "싱크대 위 2번째 선반 안에 있습니다",
        "🖨️ 복합기 작동 불가!": "복합기 우측 하단 전원버튼을 껐다 켜주세요"
    },
    "🏢 사무실 2 구역 OA": {
        "🧻 티슈": "하단 서랍을 확인해주세요 ",
        "💦 물티슈": "하단 서랍을 확인해주세",
        "🔋 건전지": "사무용품 보관함 안에 보관중입니다",
        "🧴 퐁퐁": "싱크대 위 2번째 선반에 보관중입니다 ",
        "🧽 수세미": "싱크대 위 1번째 선반에 보관중입니다",
        "🖨️ 복합기 작동 불가!": "복합기 우측 하단 전원버튼을 껐다 켜주세요"
    }
}

# --- 3. 📸 [사진 앨범 세팅 (구역별로 완전 분리!)] ---
# 🚨 깃허브에 올리신 구역별 사진 이름을 정확히 적어주세요! (예: 1-1_tissue.jpg)
# 만약 아직 안 찍은 사진이 있다면 그냥 빈칸("")으로 두셔도 에러 안 나고 잘 돌아갑니다!
IMAGE_DATA = {
    "🏢 사무실 1-1 구역 OA": {
        "🧻 티슈": "1-1_tissue.jpg",
        "💦 물티슈": "1-1_wipes.jpg",
        "🔋 건전지": "1-1_battery.jpg",
        "🖨️ 복합기 작동 불가!": "printer_error.png" # 복합기는 다 똑같이 생겼으면 같은 사진 써도 됩니다!
    },
    "🏢 사무실 1-2 구역 OA": {
        "🧻 티슈": "1-2_tissue.jpg",
        "💦 물티슈": "1-2_wipes.jpg",
        "🔋 건전지": "1-1_battery.jpg",
        "🧴 퐁퐁": "1-2_pongpong.jpg",
        "🧽 수세미": "1-2_sponge.jpg",
        "🖨️ 복합기 작동 불가!": "printer_error.jpg"
    },
    "🏢 사무실 2 구역 OA": {
        "🧻 티슈": "2_tissue.jpg",
        "💦 물티슈": "2_wipes.jpg",
        "🔋 건전지": "1-1_battery.jpg",
        "🧴 퐁퐁": "2_pongpong.jpg",
        "🧽 수세미": "2_sponge.jpg",
        "🖨️ 복합기 작동 불가!": "printer_error.jpg"
    }
}

# --- 페이지 설정 ---
st.set_page_config(page_title="브랜드웍스 비품 요정", page_icon="🧚", layout="centered")

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
    
    # 📸 [사진 띄우기 마법!]
    # 이제 구역(loc)을 먼저 찾고, 그 안에서 물건(item) 사진을 찾습니다!
    image_file = IMAGE_DATA.get(loc, {}).get(item, "")
    
    if "복합기" in item:
        st.title("🖨️ 복합기에 문제가 생겼군요! 💦")
        if image_file != "" and os.path.exists(image_file):
            st.image(image_file, use_container_width=True)
        st.info(f"💡 **총무팀에 연락하기 전에 먼저 이렇게 해보시겠어요?**\n\n👉 **{hidden_spot}**")
    else:
        st.title(f"[{item}] 찾으시나요? 👀")
        if image_file != "" and os.path.exists(image_file):
            st.image(image_file, use_container_width=True)
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
        btn_text = "🚨 헐... 그래도 안 돼요!" if "복합기" in item else "🚨 헐... 거기도 텅 비었어요!"
        
        if st.button(btn_text, type="secondary", use_container_width=True):
            st.success("✅ 총무팀에 전달되었습니다. 빠른 시일 내에 확인하겠습니다. (2초 뒤 처음으로 돌아갑니다)")
            
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
