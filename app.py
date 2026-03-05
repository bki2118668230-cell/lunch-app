import streamlit as st
import pandas as pd
import gspread
import json
import traceback
st.set_page_config(page_title="프레시밀 예약 확인", page_icon="🍱", layout="centered")
st.markdown('<div style="font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 20px;">🍱 프레시밀 식사 예약 확인</div>', unsafe_allow_html=True)
def load_data():
    key_dict = json.loads(st.secrets["gcp_service_account"])
    client = gspread.service_account_from_dict(key_dict)
    
    # 여기서 파일을 못 찾으면 에러가 납니다!
    sheet = client.open("BKI프레시밀 오늘의 예약자 확인").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)
try:
    df = load_data()
    if df.empty:
        st.warning("오늘 등록된 식사 예약 명단이 없습니다.")
    else:
        emp_no = st.text_input("사번을 입력하세요", placeholder="예: 1234", max_chars=10)
        if st.button("예약 확인", use_container_width=True):
            df['사번'] = df['사번'].astype(str).str.strip()
            if str(emp_no).strip() in df['사번'].values:
                name = df[df['사번'] == str(emp_no).strip()]['사원명'].iloc[0]
                st.success(f"✅ {name}님 ({emp_no}) 오늘 식사 예약이 확인되었습니다!")
                st.balloons()
            else:
                st.error(f"❌ 사번: {emp_no} - 오늘 예약 명단에 없습니다.")
                
except Exception as e:
    st.error("🚨 삐빅! 에러 발생! 아래의 까만색 박스 안의 영어 글씨를 복사해서 알려주세요!")
    st.code(traceback.format_exc())
