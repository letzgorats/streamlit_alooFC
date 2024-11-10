
# import psycopg2
# 페이지 설정 (파비콘과 제목 변경)# 페이지 설정 (파비콘과 제목 변경)
import streamlit as st
st.set_page_config(page_title="AlooFC", page_icon="images/logo/alooFC_fabicon.ico")
# from streamlit_image_zoom import image_zoom
from team_intro import show_team_intro
from team_members import show_team_members
from fee_info import show_fee_info
from utils import get_supabase_client
from attendance import show_attendance
from player_stats import show_player_stats
from auth import login, logout, is_logged_in, signup, reset_password_confirm, reset_password
from prediction import prediction_app  # 예측 투표 기능 임포트
from prediction import calculate_prediction_rates
import urllib.parse



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
            color: {header_color};
            font-weight: bold;
            margin-bottom: 10px;
            word-wrap: break-word; /* 단어를 줄 바꿈 */
        }}
        .card p {{
            font-size: 14px;
            line-height: 1.5;
            color: {text_color};
            margin: 5px 0;
            
        }}
        
        .card h2 {{
            color: {header_color};
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
        
        /* 버튼 스타일 수정 */
        div.stButton > button {{
            color: {text_color} !important;
            background-color: #4CAF50; /* 원하는 버튼 배경색으로 설정 */
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
        }}
        
        /* 버튼에 호버 효과 추가 */
        div.stButton > button:hover {{
            background-color: #45a049;
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


def main():
    # Streamlit 앱 실행
    st.title("⚽️ Aloo FC ⚽️")

    # 사이드바에 기능 구현
    st.sidebar.title("📋 AlooFC 메뉴 ")
    menu = st.sidebar.radio("메뉴를 선택하세요", ["팀 소개", "팀 멤버 리스트", "회비 정보","참석률 분석","시즌 기록","EPL 예측 투표","예측률 순위표"])

    # Supabase 클라이언트 생성
    supabase = get_supabase_client()

    # 이전 메뉴와 현재 메뉴를 비교하여 메뉴가 변경되었을 때만 세션 상태 초기화
    if 'previous_menu' not in st.session_state:
        st.session_state['previous_menu'] = menu
    elif st.session_state['previous_menu'] != menu:
        reset_session_state()
        st.session_state['previous_menu'] = menu

    # URL 쿼리 파라미터 확인
    query_params = st.query_params
    if 'token' in query_params:
        encoded_token = query_params['token'][0]
        # 토큰을 URL 디코딩
        reset_token = urllib.parse.unquote(encoded_token)
        # 토큰을 문자열로 변환 (PyJWT 버전에 따라 필요)
        reset_token = urllib.parse.unquote(encoded_token)
        reset_password_confirm(reset_token)
        return

    # 회원가입 및 비밀번호 재설정 페이지 표시
    if st.session_state.get('show_signup', False):
        signup()
        return

    if st.session_state.get('show_reset_password', False):
        reset_password()
        return

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

    # 6. EPL 예측 투표
    elif menu == "EPL 예측 투표":
        # 로그인 여부 확인
        if is_logged_in():
            prediction_app()
            # 로그아웃 버튼 추가
            if st.sidebar.button("로그아웃"):
                logout()
                st.rerun()
        else:
            st.warning("이 페이지는 로그인한 사용자만 접근 가능합니다.")
            login()  # 로그인 페이지로 이동
    elif menu == "예측률 순위표":
        calculate_prediction_rates()

def reset_session_state():
    # 세션 상태에서 페이지 전환에 사용되는 키들을 삭제하여 초기화
    keys_to_reset = ['show_signup', 'show_reset_password']
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

if __name__ == "__main__":
    main()

