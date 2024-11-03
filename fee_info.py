import streamlit as st

def show_fee_info():
    st.header("Aloo FC 팀 회비 정보 💰")
    st.write("아래 링크를 통해 팀 회비를 납부해주세요:")
    # 회비 링크 추가
    fee_link = "https://www.imchongmoo.com/share/MtE8J8n0p48O3xGNNIqXapjzLtbXTcfye9AfJCKo5jWCqNGw1PlEbuZWRIScu8lbiZyULuCGXbKViaNpfoZCUv1GtmoRX6lxV0cPsj5-x_g"
    st.markdown(f"[팀 회비 납부 링크]({fee_link})", unsafe_allow_html=True)