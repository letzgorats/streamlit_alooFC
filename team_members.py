from utils import create_connection, get_image_url
from utils import supabase
import streamlit as st
import psycopg2
from streamlit_javascript import st_javascript  # 추가

def show_team_members():
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
                display_profile_card(member, True)

    else:
        # 특정 선수 프로필 상세 보기
        st.subheader(f"{member_info[0]} {member_info[1]}의 프로필 📄")
        display_profile_card(member_info,False)

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


# 컬럼 수 결정 함수
def get_num_columns():
    screen_width = st_javascript("window.innerWidth")
    if screen_width is None:
        screen_width = 800 # 기본값 설정
    if screen_width < 600:
        return 1
    else:
        return 3

# 프로필 카드 표시 함수
def display_profile_card(member, all_players):
    (first_name, last_name, position, role, jersey_number, city, district,
     height, weight, main_foot, shoe_size, body_type, support_team, support_player,
     commitment,image_path_in_storage) = member

    # 이제 supabase 클라이언트를 함수 인자로 전달할 필요 없이 사용 가능
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