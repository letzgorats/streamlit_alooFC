# import psycopg2
import streamlit as st
# from streamlit_image_zoom import image_zoom
from team_intro import show_team_intro
from team_members import show_team_members
from fee_info import show_fee_info
from utils import get_supabase_client
from attendance import show_attendance
from player_stats import show_player_stats

# 페이지 설정 (파비콘과 제목 변경)
st.set_page_config(page_title="AlooFC", page_icon="images/logo/alooFC_fabicon.ico")

# Initialize Cloudinary
# cloudinary.config(
#     cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
#     api_key=os.getenv('CLOUDINARY_API_KEY'),
#     api_secret=os.getenv('CLOUDINARY_API_SECRET'),
#     secure=True
# )


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
        
        /* 작은 카드 스타일 */
        .small-card {{
            background-color: #ffffff;  /* 카드 배경색 (원하시는 색상으로 변경 가능) */
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            width: 150px;  /* 카드 너비 */
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
        }}
        
        .small-card img {{
            width: 100px;
            height: 130px;
            object-fit: cover;
            border-radius: 50%;
            margin-bottom: 5px;
        }}
        
        .small-card h4 {{
            color: {header_color};
            font-size: 16px;
            margin-bottom: 5px;
        }}
        
        .small-card p {{
            font-size: 12px;
            color: {text_color};
            margin: 2px 0;
        }}
        
        /* 참석왕/불참왕 동일 참석률 멤버 이름 스타일 */
        .attendance-king-names {{
            color: #FF005C;  /* 핑크색 */
            font-size: 14px;
        }}
        
        .absence-king-names {{
            color: gray;
            font-size: 14px;
        }}
        /* 컬럼 내부 요소 정렬 */
        .stColumn > div {{
            display: flex;
            flex-direction: column;
            align-items: center;
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


# Streamlit 앱 실행
st.title("⚽️ Aloo FC ⚽️")

# 사이드바에 기능 구현
st.sidebar.title("📋 AlooFC 메뉴 ")
menu = st.sidebar.radio("메뉴를 선택하세요", ["팀 소개", "팀 멤버 리스트", "회비 정보","참석률 분석","시즌 기록"])

# Supabase 클라이언트 생성
supabase = get_supabase_client()

# 1. 팀 소개 탭
if menu == "팀 소개":
    show_team_intro()

# 2. 팀 멤버 리스트 탭
elif menu == "팀 멤버 리스트":
    show_team_members()

# 3. 회비 정보 탭
elif menu == "회비 정보":
    show_fee_info()

# 4. 참석률 분석 탭
elif menu == "참석률 분석":
    show_attendance()

# 5. 시즌 기록 탭
elif menu == "시즌 기록":
    show_player_stats()
