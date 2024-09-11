import psycopg2
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
from PIL import Image

# 이미지 캐싱 함수 (st.cache_resource 사용)
@st.cache_resource
def load_image(image_path):
    img = Image.open(image_path)
    return img


# Fly.io 환경에서 DATABASE_URL 환경 변수를 사용하여 환경 구분
if os.getenv('DATABASE_URL') is None:  # 로컬 환경일 때만 .env 파일 로드
    load_dotenv()

def create_connection():
    # Fly.io 환경에서 DATABASE_URL 환경 변수를 사용
    DATABASE_URL = os.getenv('DATABASE_URL')

    if DATABASE_URL:  # Fly.io 환경일 때는 DATABASE_URL 사용
        conn = psycopg2.connect(DATABASE_URL, sslmode='disable')  # 보안을 위해 'require' 사용
    else:  # 로컬 환경일 때는 .env 파일의 변수 사용
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5433")
        )
    return conn

# 다크모드/라이트모드 선택 기능 추가
mode = st.sidebar.selectbox("모드를 선택하세요", ["라이트 모드", "다크 모드"])

# CSS 스타일 설정
# 사이드바 배경색 설정
if mode == "다크 모드":
    background_color = "#1e1e1e"
    text_color = "#ffffff"
    card_color = "#2c2c2c"
    sidebar_bg = "#333333"  # 다크모드용 사이드바 배경색
    header_color = "#4CAF50"
else:
    background_color = "#d6ccc2"  # 라이트 모드 전체 배경 색상
    text_color = "#000000"
    card_color = "#f5f5f5"
    sidebar_bg = "#f5f5f5"  # 라이트모드용 사이드바 배경색
    header_color = "#4CAF50"

# 전체 배경과 페이지 스타일 적용
st.markdown(f"""
    <style>
        /* 배경색과 텍스트 스타일 */
        .stApp {{
            background-color: {background_color};
            color: {text_color};
        }}
        /* 사이드바 배경색 설정 */
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
        }}
        /* 카드 스타일 */
        .card {{
            background-color: {card_color};
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            text-align: center;
        }}
        /* 이미지 모양을 원형에 가깝게 조정 및 클릭 기능 제거 */
        img {{
            pointer-events: none;  /* 클릭 기능 완전히 제거 */
            border-radius: 50% / 40%;  /* 직사각형에 가까운 타원형 */
            object-fit: cover;
            width: 150px;
            height: 200px;
        }}
        /* 프로필 제목 (큰 제목 포함, 색상 변경) */
        h1, h2, h3, h4 {{
            color: {header_color};
            font-weight: bold;
        }}
        /* 카드 내부의 텍스트 */
        p {{
            margin: 5px 0;
            font-size: 14px;
            line-height: 1.5;
            color: {text_color};
        }}
    </style>
""", unsafe_allow_html=True)



# 팀 멤버 데이터 가져오기
def get_team_members():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT first_name, last_name, position, role, jersey_number, city, district, 
               height, weight, main_foot, shoe_size, body_type, support_team, commitment 
        FROM team_members
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# 팀 멤버 이름 목록 가져오기 (검색용)
def get_member_names():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT first_name || ' ' || last_name FROM team_members")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return ['모든 선수 보기'] + [row[0] for row in rows]

# Streamlit 앱 실행
st.title("⚽️ Aloo FC ⚽️")


# 사이드바에 기능 구현
st.sidebar.title("📋 AlooFC 메뉴 ")
menu = st.sidebar.radio("메뉴를 선택하세요", ["팀 소개", "팀 멤버 리스트", "회비 정보"])

# 1. 팀 소개 탭
if menu == "팀 소개":
    st.header("Aloo FC 팀 소개 📢")
    st.image(load_image("images/logo/alooFC_logo.png"), caption="Aloo FC 로고", width=200)
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

# 2. 팀 멤버 리스트 탭
elif menu == "팀 멤버 리스트":
    st.header("팀 멤버 리스트 👥")

    # 팀원 검색 기능 추가 (모든 선수 보기 포함)
    search_name = st.selectbox("선수를 선택하세요:", options=get_member_names())

    member_info = None  # 초기화

    if search_name != '모든 선수 보기':
        # 특정 선수 검색 시 해당 선수의 프로필과 정보 출력
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
                SELECT first_name, last_name, position, role, jersey_number, city, district, 
                       height, weight, main_foot, shoe_size, body_type, support_team, support_player, commitment 
                FROM team_members WHERE first_name || ' ' || last_name = %s
            """, (search_name,))
        member_info = cur.fetchone()
        cur.close()
        conn.close()

    if not member_info:
        # '모든 선수 보기' 선택 시 모든 선수의 프로필 사진 출력
        team_members = get_team_members()

        # 3명씩 한 줄에 나열
        cols = st.columns(3)

        for i, member in enumerate(team_members):
            with cols[i % 3]:
                # 각 선수 카드 스타일
                image_path = f"images/24_25_players_profile/{member[1].lower()}_{member[0].lower()}_profile.jpg"
                img = load_image(image_path)
                st.image(img, width=150, use_column_width=False)  # 직사각형에 가까운 타원형 이미지 적용

                st.markdown(f"""
                            <div class="card">
                                <h4 style="color: #4CAF50;">{member[0]} {member[1]}</h4>
                                <p style="font-weight: bold;"><strong>직책:</strong> {member[3]}</p>
                                <p><strong>포지션:</strong> {member[2]}</p>
                                <p><strong>등번호:</strong> {member[4]}</p>
                            </div>
                            """, unsafe_allow_html=True)
    else:

        st.subheader(f"{member_info[0]} {member_info[1]}의 프로필 📄")
        image_path = f"images/24_25_players_profile/{member_info[1].lower()}_{member_info[0].lower()}_profile.jpg"
        st.image(load_image(image_path), width=200)

        # 팀 멤버 상세 정보 출력
        st.markdown(f"**이름:** {member_info[0]} {member_info[1]}")
        st.markdown(f"**포지션:** {member_info[2]}")
        st.markdown(f"**직책:** {member_info[3]}")
        st.markdown(f"**등번호:** {member_info[4]}")
        st.markdown(f"**지역:** {member_info[5]}, {member_info[6]}")
        st.markdown(f"**키:** {member_info[7]} cm")
        st.markdown(f"**몸무게:** {member_info[8]} kg")
        st.markdown(f"**주발:** {member_info[9]}")
        st.markdown(f"**신발 사이즈:** {member_info[10]} mm")
        st.markdown(f"**체형:** {member_info[11]}")
        st.markdown(f"**응원하는 팀:** {member_info[12]}")
        st.markdown(f"**좋아하는 선수:** {member_info[13]}")
        st.markdown(f"**각오 한 마디:** {member_info[14]}")

# 3. 회비 정보 탭
elif menu == "회비 정보":
    st.header("Aloo FC 팀 회비 정보 💰")
    st.write("아래 링크를 통해 팀 회비를 납부해주세요:")

    # 회비 링크 추가
    fee_link = "https://www.imchongmoo.com/share/MtE8J8n0p48O3xGNNIqXapjzLtbXTcfye9AfJCKo5jX-uqYuLbLYDyIhRDUrI9K7Kymvtu7mkw-U8VVjOLrMeQ"
    st.markdown(f"[팀 회비 납부 링크]({fee_link})", unsafe_allow_html=True)
