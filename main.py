import psycopg2
import streamlit as st
import folium
from streamlit_folium import st_folium

from dotenv import load_dotenv
import os
import pandas as pd

# .env 파일 로드
load_dotenv()


# PostgreSQL 연결 설정
def create_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn


# 팀 멤버 데이터 가져오기
def get_team_members():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, city, height, shoe_size, body_type, weight, support_team, commitment FROM team_members")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# 팀 멤버 이름 목록 가져오기 (검색용)
def get_member_names():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM team_members")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]


# Streamlit 앱 실행
st.title("Aloo FC 팀 관리 시스템 ⚽️")

# 사이드바에 기능 구현
st.sidebar.title("📋 AlooFC 메뉴")
menu = st.sidebar.radio("메뉴를 선택하세요", ["팀 소개", "팀 멤버 리스트", "회비 정보"])

# 1. 팀 소개 탭
if menu == "팀 소개":
    st.header("Aloo FC 팀 소개 📢")
    st.image("images/alooFC_logo.png", caption="Aloo FC 로고", width=200)
    st.write("Aloo FC는 풋살을 사랑하는 열정적인 팀입니다. 항상 최선을 다해 경기에 임합니다!")

    # 유니폼 이미지
    st.markdown("## 👕 유니폼 소개")
    st.image("images/team_uniform.jpg", caption="Aloo FC 유니폼", width=300)

    st.markdown("## 🌠 주 활동 지역")
    # 서울 지도 추가
    # 부천 클리어 풋살장의 좌표
    bucheon_clear_futsal_location = [37.505653, 126.753796]

    # Folium 지도 생성 (부천 클리어 풋살장의 좌표로 설정)
    m = folium.Map(location=bucheon_clear_futsal_location, zoom_start=15)

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

# 2. 팀 멤버 리스트 탭
elif menu == "팀 멤버 리스트":
    st.header("팀 멤버 리스트 👥")

    # 팀원 검색 기능 추가
    search_name = st.selectbox("선수를 선택하세요:", options=get_member_names())

    if search_name:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            f"SELECT name, city, height, shoe_size, body_type, weight, support_team, commitment FROM team_members WHERE name = %s",
            (search_name,))
        member_info = cur.fetchone()
        cur.close()
        conn.close()

        if member_info:
            st.subheader(f"{search_name}의 프로필 📄")
            image_path = f"images/{member_info[0].lower()}_profile.jpg"
            st.image(image_path, width=200)

            # 팀 멤버 상세 정보 출력
            st.markdown(f"**이름:** {member_info[0]}")
            st.markdown(f"**사는 곳:** {member_info[1]}")
            st.markdown(f"**키:** {member_info[2]} cm")
            st.markdown(f"**신발 사이즈:** {member_info[3]} mm")
            st.markdown(f"**체형:** {member_info[4]}")
            st.markdown(f"**몸무게:** {member_info[5]} kg")
            st.markdown(f"**응원하는 팀:** {member_info[6]}")
            st.markdown(f"**각오 한 마디:** {member_info[7]}")
    else:
        team_members = get_team_members()
        for member in team_members:
            with st.container():
                col1, col2 = st.columns([1, 2])
                image_path = f"images/{member[0].lower()}_profile.jpg"
                with col1:
                    st.image(image_path, width=150)
                with col2:
                    st.markdown(f"### {member[0]}")
                    st.markdown(f"**사는 곳:** {member[1]}")
                    st.markdown(f"**키:** {member[2]} cm")
                    st.markdown(f"**신발 사이즈:** {member[3]} mm")
                    st.markdown(f"**체형:** {member[4]}")
                    st.markdown(f"**몸무게:** {member[5]} kg")
                    st.markdown(f"**응원하는 팀:** {member[6]}")
                    st.markdown(f"**각오 한 마디:** {member[7]}")
                st.markdown("---")

# 3. 회비 정보 탭
elif menu == "회비 정보":
    st.header("Aloo FC 팀 회비 정보 💰")
    st.write("아래 링크를 통해 팀 회비를 납부해주세요:")

    # 회비 링크 추가
    fee_link = "https://www.imchongmoo.com/share/MtE8J8n0p48O3xGNNIqXapjzLtbXTcfye9AfJCKo5jWAgjMGWwfOIplciNkIQbDSsmfZXJ372Lfhp3EmoitAWA"
    st.markdown(f"[팀 회비 납부 링크]({fee_link})", unsafe_allow_html=True)

# 스타일 적용
st.markdown("""
    <style>
        .container {
            background-color: #e0f7fa;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
        }
        .header {
            color: #00796b;
            font-size: 24px;
        }
        img {
            border-radius: 50%;
        }
    </style>
""", unsafe_allow_html=True)

