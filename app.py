import streamlit as st
import pandas as pd
import gspread
import json

# 📱 스마트폰 화면 설정 (앱처럼 보이게)
st.set_page_config(page_title=, page_icon="🍱", layout="centered")

# 🎨 디자인 (CSS)
st.markdown("""
<style>
    .main-title { font-size: 28px; font-weight: bold; color: #2c3e50; text-align: center; margin-bottom: 20px; }
    .success-box { background-color: #d4edda; color: #155724; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px; font-size: 20px; font-weight: bold;}
    .error-box { background-color: #f8d7da; color: #721c24; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px; font-size: 20px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMTEyMTVfMTAy%2FMDAxNjM5NTM3MzMzNjgw.niVtkehnbZKQJORlo7SA6iXZVnf1YLeG3ikt63NYNvEg.Z98gouiZmmbIpm9XAGReQLX8VLtw83H1YSOz55_m7Tgg.JPEG.togle_kr%2F2_%25BB%25E7%25BA%25BB.jpg&type=sc960_832', unsafe_allow_html=True)

# ☁️ 구글 시트에서 명단 가져오기
@st.cache_data(ttl=300) # 5분마다 새로고침
def load_data():
    try:
        # 1. 깃허브 비밀금고에서 구글 열쇠(JSON) 꺼내오기
        key_dict = json.loads(st.secrets["gcp_service_account"])
        
        # 2. 🌟 최신 gspread 방식으로 로그인 (200 에러 충돌 완벽 해결!)
        client = gspread.service_account_from_dict(key_dict)
        
        # 3. 구글 시트 열기
        sheet = client.open("BKI프레시밀 오늘의 예약자 확인").sheet1
        
        # 4. 더 안전한 방식으로 데이터 가져오기
        data = sheet.get_all_values()
        
        # 데이터가 없으면 빈 명단 반환
        if not data or len(data) < 2:
            return pd.DataFrame(columns=["사번", "사원명"])
            
        # 첫 번째 줄(헤더)을 컬럼명으로 사용
        df = pd.DataFrame(data[1:], columns=data[0])
        return df
        
    except Exception as e:
        st.error(f"데이터를 불러오는 데 실패했습니다. 관리자에게 문의하세요. ({e})")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("오늘 등록된 식사 예약 명단이 없습니다.")
else:
    # 🔍 검색창 만들기
    emp_no = st.text_input("사번을 입력하세요", placeholder="예: 1234", max_chars=10)
    
    if st.button("예약 확인", use_container_width=True):
        if emp_no:
            # 사번 비교를 위해 문자열로 통일
            df['사번'] = df['사번'].astype(str).str.strip()
            emp_no_str = str(emp_no).strip()
            
            # 명단에 사번이 있는지 확인
            user_info = df[df['사번'] == emp_no_str]
            
            if not user_info.empty:
                name = user_info.iloc[0]['사원명']
                st.markdown(f'<div class="success-box">✅ {name}님 ({emp_no})<br>오늘 식사 예약이 확인되었습니다!</div>', unsafe_allow_html=True)
                st.balloons() # 🎉 축하 풍선 효과!
            else:
                st.markdown(f'<div class="error-box">❌ 사번: {emp_no}<br>오늘 예약 명단에 없습니다.</div>', unsafe_allow_html=True)
        else:
            st.warning("사번을 입력해 주세요.")
