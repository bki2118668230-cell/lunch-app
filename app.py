import streamlit as st
import pandas as pd
import gspread
import json
import traceback

# 📱 스마트폰 화면 설정 (앱처럼 보이게)
st.set_page_config(page_title="프레시밀 예약 확인", page_icon="🍱", layout="centered")

# 🎨 디자인 (CSS)
st.markdown("""
<style>
    .main-title { font-size: 28px; font-weight: bold; color: #2c3e50; text-align: center; margin-bottom: 20px; }
    .success-box { background-color: #d4edda; color: #155724; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px; font-size: 20px; font-weight: bold;}
    .error-box { background-color: #f8d7da; color: #721c24; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px; font-size: 20px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# 🌟 대장님이 픽하신 멋진 사원증 이미지 추가!!
image_url = "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMTEyMTVfMTAy%2FMDAxNjM5NTM3MzMzNjgw.niVtkehnbZKQJORlo7SA6iXZVnf1YLeG3ikt63NYNvEg.Z98gouiZmmbIpm9XAGReQLX8VLtw83H1YSOz55_m7Tgg.JPEG.togle_kr%2F2_%25BB%25E7%25BA%25BB.jpg&type=sc960_832"
st.image(image_url, use_container_width=True)

st.markdown('<div class="main-title">🍱 프레시밀 식사 예약 확인</div>', unsafe_allow_html=True)

# ☁️ 구글 시트에서 명단 가져오기
@st.cache_data(ttl=300) # 5분마다 새로고침
def load_data():
    try:
        key_dict = json.loads(st.secrets["gcp_service_account"])
        client = gspread.service_account_from_dict(key_dict)
        
        # 🌟 띄어쓰기 완벽하게 맞춰진 구글 시트 이름!
        sheet = client.open("BKI 프레시밀 오늘의 예약자 확인").sheet1
        
        data = sheet.get_all_values()
        
        if not data or len(data) < 2:
            return pd.DataFrame(columns=["사번", "사원명"])
            
        df = pd.DataFrame(data[1:], columns=data[0])
        return df
        
    except Exception as e:
        st.error(f"데이터를 불러오는 데 실패했습니다. 관리자에게 문의하세요.")
        st.code(traceback.format_exc())
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("오늘 등록된 식사 예약 명단이 없습니다.")
else:
    # 🔍 검색창 만들기
    emp_no = st.text_input("사번을 입력하세요", placeholder="예: 1234", max_chars=10)
    
    if st.button("예약 확인", use_container_width=True):
        if emp_no:
            df['사번'] = df['사번'].astype(str).str.strip()
            emp_no_str = str(emp_no).strip()
            
            user_info = df[df['사번'] == emp_no_str]
            
            if not user_info.empty:
                name = user_info.iloc[0]['사원명']
                st.markdown(f'<div class="success-box">✅ {name}님 ({emp_no})<br>오늘 식사 예약이 확인되었습니다!</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f'<div class="error-box">❌ 사번: {emp_no}<br>오늘 예약 명단에 없습니다.</div>', unsafe_allow_html=True)
        else:
            st.warning("사번을 입력해 주세요.")
