import psycopg2
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
from PIL import Image
# from streamlit_image_zoom import image_zoom
from supabase import create_client, Client
from streamlit_javascript import st_javascript  # 추가


# 페이지 설정 (파비콘과 제목 변경)
st.set_page_config(page_title="AlooFC", page_icon="images/logo/alooFC_fabicon.ico")

# Fly.io 환경에서 DATABASE_URL 환경 변수를 사용하여 환경 구분
if os.getenv('DATABASE_URL') is None:  # 로컬 환경일 때만 .env 파일 로드
    load_dotenv()

# supabase url 과 키 가져오기
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
# supabase 클라이언트 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 이미지 로드 함수 (cache.data 캐싱 사용)
@st.cache_data
def load_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')  # PIL 이미지로 변환
        return img
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

# 이미지 URL 생성 함수
@st.cache_data
def get_image_url(path):
    # URL 만료 시간 설정 (예: 1시간 후 만료)
    expires_in = 3600  # 초 단위

    res = supabase.storage.from_('player-profiles').create_signed_url(path, expires_in)
    if res:
        return res.get('signedURL')
    else:
        st.error("이미지 URL을 생성하는 데 실패했습니다.")
        return None

# Initialize Cloudinary
# cloudinary.config(
#     cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
#     api_key=os.getenv('CLOUDINARY_API_KEY'),
#     api_secret=os.getenv('CLOUDINARY_API_SECRET'),
#     secure=True
# )

# 데이터베이스 연결 함수
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

# 화면 너비 가져오기 함수
def get_screen_width():
    width = st_javascript("window.innerWidth")
    return int(width) if width else 800  # 기본값 설정

screen_width = get_screen_width()

# 컬럼 수 결정 함수
def get_num_columns():
    if screen_width < 600:
        return 1
    else:
        return 3

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

# 전체 배경과 페이지 스타일 적용 및 manifest.json 설정 추가
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
            text-align: center;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            
        }}
        
        .card img {{
            width: 150px;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
        }}
        .card h4 {{
            color: {{header_color}};
            font-weight: bold;
            margin-bottom: 10px;
            word-wrap: break-word; /* 단어를 줄 바꿈 */
        }}
        .card p {{
            font-size: 14px;
            line-height: 1.5;
            color: {{text_color}};
            margin: 5px 0;
            
        }}
        
        .card h2 {{
            color: {{header_color}};
        }}
        
        .profile-card {{
                        background-color: {card_color};
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        margin: auto;
                        width: 60%;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                    }}
        .profile-card img {{
            border-radius: 50%;
            width: 200px;
            height: 200px;
            object-fit: cover;
            margin-bottom: 20px;
        }}
        .profile-card h2 {{
            color:  {header_color};
            margin-bottom: 10px;
        }}
        .profile-card p {{
            font-size: 16px;
            color: {text_color};
            margin: 5px 0;
        }}
        
        /* 이미지 스타일 */
        img {{
            border-radius: 50% / 40%;
            object-fit: cover;
            width: 150px;
            height: 200px;

            /* 손가락 확대 허용 */
            touch-action: auto;
            user-select: none;
            max-width: 100%;
            height: auto;
            transition: transform 0.3s ease-in-out;
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

        /* 모바일 지도 반응형 설정 */
        @media screen and (max-width: 768px) {{
            .folium-map {{
                width: 100% !important;
                height: 300px !important;  /* 모바일 화면에서 지도의 높이 조정 */
            }}
        }}
        /* 모바일 환경에서 카드 너비 조정 */
        @media screen and (max-width: 600px) {{
            .card {{
                width: 100%;
            }}
            .profile-card {{
                width: 100%;
            }}

        }}
    </style>

    <!-- 아이콘과 파비콘 설정 -->
    <link rel="icon" href="images/logo/alooFC_fabicon.ico" type="image/x-icon">
    <link rel="apple-touch-icon" sizes="192x192" href="images/logo/alooFC_logo_192x192.png">
    <link rel="icon" type="image/png" sizes="512x512" href="images/logo/alooFC_logo_512x512.png">

    <!-- Manifest 설정 -->
    <link rel="manifest" href="/manifest.json">
""", unsafe_allow_html=True)


# 팀 멤버 데이터 가져오기
def get_team_members():
    with st.spinner('팀 멤버 데이터를 불러오는 중입니다...'):
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT first_name, last_name, position, role, jersey_number, city, district, 
                   height, weight, main_foot, shoe_size, body_type, support_team, support_player, commitment, image_path_in_storage 
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

# 프로필 카드 표시 함수
def display_profile_card(member,all_players):
    (first_name, last_name, position, role, jersey_number, city, district,
     height, weight, main_foot, shoe_size, body_type, support_team, support_player,
     commitment,image_path_in_storage) = member

    image_url = get_image_url(image_path_in_storage)

    if all_players:

        if image_url:
            st.markdown(f"""
                <div class="card">
                    <img src="{image_url}" alt="{first_name} {last_name}" width="150" height="200"">
                    <h4>{first_name} {last_name}</h4>
                    <p><strong>직책:</strong> {role}</p>
                    <p><strong>포지션:</strong> {position}</p>
                    <p><strong>등번호:</strong> {jersey_number}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"{first_name} {last_name} 님의 이미지를 불러올 수 없습니다.")

    else:
        if image_url:
            st.markdown(f"""
                <div class="profile-card">
                    <img src="{image_url}" alt="{first_name} {last_name}" width="150" height="200"">
                    <h4>{first_name} {last_name}</h4>
                    <p><strong>직책:</strong> {role}</p>
                    <p><strong>포지션:</strong> {position}</p>
                    <p><strong>등번호:</strong> {jersey_number}</p>
                    <p><strong>지역:</strong> {city}, {district}</p>
                    <p><strong>키:</strong> {height} cm </p>
                    <p><strong>몸무게:</strong> {weight} kg </p>
                    <p><strong>주발:</strong> {main_foot}</p>
                    <p><strong>신발 사이즈:</strong> {shoe_size}</p>
                    <p><strong>체형:</strong> {body_type}</p>
                    <p><strong>응원하는 팀:</strong> {support_team}</p>
                    <p><strong>좋아하는 선수:</strong> {support_player}</p>
                    <p><strong>각오 한 마디:</strong> {commitment}</p>
                </div>
            """, unsafe_allow_html=True)

        else:
            st.warning(f"{first_name} {last_name} 님의 이미지를 불러올 수 없습니다.")


# Streamlit 앱 실행
st.title("⚽️ Aloo FC ⚽️")

# 사이드바에 기능 구현
st.sidebar.title("📋 AlooFC 메뉴 ")
menu = st.sidebar.radio("메뉴를 선택하세요", ["팀 소개", "팀 멤버 리스트", "회비 정보"])

# 1. 팀 소개 탭
if menu == "팀 소개":
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

# 2. 팀 멤버 리스트 탭
elif menu == "팀 멤버 리스트":
    st.header("팀 멤버 리스트 👥")
    # 팀원 검색 기능 추가 (모든 선수 보기 포함)
    search_name = st.selectbox("선수를 검색하시면 세부정보를 확인할 수 있습니다:", options=get_member_names())

    member_info = None  # 초기화

    if search_name != '모든 선수 보기':
        # 특정 선수 검색 시 해당 선수의 프로필과 정보 출력
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
                SELECT first_name, last_name, position, role, jersey_number, city, district, 
                       height, weight, main_foot, shoe_size, body_type, support_team, support_player, commitment, image_path_in_storage 
                FROM team_members WHERE first_name || ' ' || last_name = %s
            """, (search_name,))
        member_info = cur.fetchone()
        cur.close()
        conn.close()

    if not member_info:
        # '모든 선수 보기' 선택 시 모든 선수의 프로필 사진 출력
        team_members = get_team_members()
        # 3명씩 한 줄에 나열
        num_cols = get_num_columns()
        cols = st.columns(num_cols)

        for i, member in enumerate(team_members):
            with cols[i % num_cols]:
                # 각 선수 카드 스타일
                display_profile_card(member,True)

    else:
        # 특정 선수 프로필 상세 보기
        st.subheader(f"{member_info[0]} {member_info[1]}의 프로필 📄")
        display_profile_card(member_info,False)


# 3. 회비 정보 탭
elif menu == "회비 정보":
    st.header("Aloo FC 팀 회비 정보 💰")
    st.write("아래 링크를 통해 팀 회비를 납부해주세요:")
    # 회비 링크 추가
    fee_link = "https://www.imchongmoo.com/share/MtE8J8n0p48O3xGNNIqXapjzLtbXTcfye9AfJCKo5jX-uqYuLbLYDyIhRDUrI9K7Kymvtu7mkw-U8VVjOLrMeQ"
    st.markdown(f"[팀 회비 납부 링크]({fee_link})", unsafe_allow_html=True)