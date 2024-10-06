import streamlit as st
import folium
from streamlit_folium import st_folium
from utils import load_image

def show_team_intro():
    st.header("Aloo FC 팀 소개 📢")
    st.write("Aloo FC 로고:")
    # streamlit 기본 이미지 표시로 변경
    img = load_image("images/logo/alooFC_logo.png")

    if img:
        st.image(img, caption="Aloo FC 로고", width=200)
    st.write("Aloo FC는 풋살을 사랑하는 열정적인 팀입니다. 항상 최선을 다해 경기에 임합니다!")

    # 유니폼 이미지 (비율 고정 안함)
    st.markdown("## 👕 유니폼 소개")
    st.image("images/uniform/team_uniform.jpg", caption="Aloo FC 유니폼", width=400, use_column_width='auto')

    st.markdown("## 🌠 주 활동 지역")
    # 부천 클리어 풋살장의 좌표
    bucheon_clear_futsal_location = [37.505653, 126.753796]
    # Folium 지도 생성 (부천 클리어 풋살장의 좌표로 설정)
    m = folium.Map(location=bucheon_clear_futsal_location, zoom_start=12)

    # 부천 클리어 풋살장 마커 추가
    folium.Marker(
        location=bucheon_clear_futsal_location,
        popup="부천 클리어 풋살장",
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)

    # 목동의 좌표
    mokdong_location = [37.5326, 126.8746]

    # 목동 마커 추가
    folium.Marker(
        location=mokdong_location,
        popup="목동",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

    # Folium 지도를 Streamlit에 표시
    st_folium(m, width=700, height=500)
