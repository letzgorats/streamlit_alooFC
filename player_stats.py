import streamlit as st
import pandas as pd
from utils import create_connection, get_image_url
from datetime import datetime

def get_current_season():
    # 현재 시즌 계산 (8월~다음해 7월)
    today = datetime.today()
    year = today.year
    month = today.month

    if month >= 8:
        current_season = f"{str(year)[-2:]}/{str(year+1)[-2:]}"
    else:
        current_season = f"{str(year-1)[-2:]}/{str(year)[-2:]}"
    return current_season


def path_to_image_html_with_name(path, name):
    return f'''
    <div style="display: inline-block; text-align: center; width: 100px;">
        <img src="{path}" style="width: 80px; height: auto !important;">
        <div style="font-size: 12px; font-weight: bold;">{name}</div>
    </div>
    '''

@st.cache_data(ttl=3600)
def get_seasons():
    with create_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT season_name FROM seasons")
            seasons = [row[0] for row in cur.fetchall()]
    return seasons

def style_dataframe(df, header_bg_color='#4CAF50'):
    # 현재 테마 가져오기
    theme = st.get_option('theme.base')
    if theme == 'dark':
        table_bg_color = '#2c2c2c'  # 다크 모드용 테이블 배경색
        text_color = 'white'
        border_color = 'white'
        hover_bg_color = '#93db95'
    else:
        table_bg_color = '#ffffff'
        text_color = 'black'
        border_color = 'black'
        hover_bg_color = '#93db95'

    df_styled = df.style.format({'선수': lambda x: x}).hide()

    # '선수' 칸의 너비 조절
    df_styled.set_table_styles(
        [{'selector': 'th.col_heading.level0', 'props': [('min-width', '80px')]},
         {'selector': 'td', 'props': [('min-width', '80px')]}],
        overwrite=False
    )

    df_styled = df_styled.set_table_styles([
        # 인덱스 숨기기
        {'selector': '.row_heading, .blank', 'props': [('display', 'none')]},
        {'selector': 'th.col_heading.level0', 'props': [('display', 'table-cell')]},
        # 테이블 전체 배경색 설정
        {'selector': 'table.dataframe tbody tr', 'props': [('background-color', table_bg_color + ' !important')]},
        # 셀 글자색 및 경계선 설정
        {'selector': 'table.dataframe tbody td', 'props': [('color', text_color + ' !important'), ('border', f'1px solid {border_color} !important')]},
        # 헤더 스타일
        {'selector': 'thead th',
         'props': [('background-color', header_bg_color), ('color', 'white'), ('font-size', '14px'),
                   ('border', f'1px solid {border_color}')]},
        # 테이블 테두리 및 글씨 굵게
        {'selector': '', 'props': [('border', f'3px solid {border_color}'), ('font-weight', 'bold')]},
        # 호버 효과
        {'selector': 'tbody tr:hover', 'props': [('background-color', hover_bg_color)]},

    ]).set_properties(**{'text-align': 'center'})
    return df_styled

@st.cache_data(ttl=3600)
def load_player_stats(selected_season):
    with create_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    tm.image_path_in_storage AS 이미지_경로,
                    tm.first_name || ' ' || tm.last_name AS 이름,
                    COALESCE(tm.jersey_number::TEXT, '') AS 등번호,
                    COUNT(DISTINCT a.match_id) AS 경기_횟수,  -- attendance 테이블을 기준으로 경기 횟수 계산
                    COALESCE(SUM(ps.goals), 0) AS 골,
                    COALESCE(SUM(ps.assists), 0) AS 어시스트,
                    COALESCE(SUM(ps.goals + ps.assists), 0) AS 공격포인트,
                    COALESCE(SUM(CASE WHEN ps.mom THEN 1 ELSE 0 END), 0) AS MOM_횟수,
                    ROUND(COALESCE(SUM(ps.goals + ps.assists), 0)::numeric / NULLIF(COUNT(DISTINCT a.match_id), 0), 2) AS 경기당_공포_전환율,
                    CASE 
                        WHEN COUNT(DISTINCT ps.injury) = 1 AND MAX(ps.injury) = 'x' THEN 'x'
                        ELSE STRING_AGG(DISTINCT CASE 
                            WHEN ps.injury <> 'x' AND (ps.injury_recovered = false OR ps.injury_recovered IS NULL) THEN ps.injury 
                            ELSE NULL 
                        END, ', ')
                    END AS 부상현황
                FROM team_members tm
                LEFT JOIN attendance a ON tm.member_id = a.member_id AND a.attendance_status = true
                LEFT JOIN player_stats ps ON tm.member_id = ps.member_id AND a.match_id = ps.match_id
                LEFT JOIN matches m ON a.match_id = m.match_id
                LEFT JOIN seasons s ON m.season_id = s.season_id
                WHERE s.season_name = %s
                GROUP BY tm.member_id, tm.image_path_in_storage, tm.jersey_number
            """, (selected_season,))
            data = cur.fetchall()

    df = pd.DataFrame(data, columns=['이미지_경로', '이름', '등번호', '경기 횟수', '골', '어시스트', '공격포인트', 'MOM 횟수', '경기당 공포 전환율', '부상현황'])

    df['부상현황'] = df['부상현황'].fillna('x')
    df['이미지_URL'] = df['이미지_경로'].apply(get_image_url)
    df['선수'] = df.apply(lambda row: path_to_image_html_with_name(row['이미지_URL'], row['이름']), axis=1)
    df = df[['선수', '등번호', '경기 횟수', '골', '어시스트', '공격포인트', 'MOM 횟수', '경기당 공포 전환율', '부상현황']]
    df.sort_values(by=['공격포인트', '골'], ascending=[False, False], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

def show_player_stats():
    st.header("시즌별 선수 기록 🏅")

    # 현재 시즌 계산
    current_season = get_current_season()

    # 시즌 선택 옵션
    seasons = get_seasons()

    # 시즌 리스트에 현재 시즌이 없을 경우 대비
    if current_season not in seasons:
        st.error(f"현재 시즌({current_season})이 seasons 테이블에 없습니다. 데이터베이스를 확인해주세요.")
        return

    selected_season = st.selectbox("시즌을 선택하세요:", seasons, index=seasons.index(current_season))

    # 안내 멘트 추가
    st.write("아래 표는 공격포인트 순으로 정렬되어 있습니다.")

    # 선택된 시즌의 선수 기록 가져오기
    with st.spinner('데이터를 불러오는 중입니다...'):
        df = load_player_stats(selected_season)

    # df를 정렬한 후 인덱스를 재설정했으므로, 인덱스는 0부터 시작합니다.
    top_indices = df.index[:3]  # 상위 3명
    bottom_indices = df.index[-3:]  # 하위 3명

    # 상위 3명과 하위 3명의 인덱스 구하기
    top_indices = df.index[:3]  # 상위 3명
    bottom_indices = df.index[-3:]  # 하위 3명

    # 행별 스타일 적용 함수 정의
    def highlight_rows(row):
        background = ''
        if row.name in top_indices:
            background = 'background-color: rgba(142, 206, 245, 0.5) !important; color: black !important;'
        elif row.name in bottom_indices:
            background = 'background-color: rgba(243, 75, 87, 0.5) !important; color: black !important;'
        else:
            background = ''
        return [background] * len(row)

    # 메인 테이블 스타일 적용 및 표시
    df_styled = style_dataframe(df)
    df_styled = df_styled.apply(highlight_rows, axis=1)  # 행별로 스타일 적용
    st.write(df_styled.to_html(escape=False), unsafe_allow_html=True)

    # 작은 테이블 생성
    mom_rank = df[['선수', '경기 횟수', 'MOM 횟수']].sort_values(by='MOM 횟수', ascending=False).head(5)
    goal_rank = df[['선수', '경기 횟수', '골']].sort_values(by='골', ascending=False).head(5)
    assist_rank = df[['선수', '경기 횟수', '어시스트']].sort_values(by='어시스트', ascending=False).head(5)
    apg_rank = df[['선수', '경기당 공포 전환율']].sort_values(by='경기당 공포 전환율', ascending=False).head(5)

    # 작은 테이블도 동일한 스타일 적용
    def style_small_dataframe(df):
        # 현재 테마 가져오기
        theme = st.get_option('theme.base')
        if theme == 'dark':
            table_bg_color = '#2c2c2c'
            text_color = 'white'
            border_color = 'white'
            hover_bg_color = '#93db95'
        else:
            table_bg_color = 'white'
            text_color = 'black'
            border_color = 'black'
            hover_bg_color = '#93db95'

        df_styled = df.style.format({'선수': lambda x: x}).hide()
        df_styled = df_styled.set_table_styles([
            # 인덱스 숨기기
            {'selector': '.row_heading, .blank', 'props': [('display', 'none')]},
            {'selector': 'th.col_heading.level0', 'props': [('display', 'table-cell')]},
            # 테이블 전체 배경색 설정
            {'selector': 'tbody tr', 'props': [('background-color', table_bg_color)]},
            # 셀 글자색 및 경계선 설정
            {'selector': 'tbody td', 'props': [('color', text_color), ('border', f'1px solid {border_color}')]},
            # 헤더 스타일
            {'selector': 'thead th',
             'props': [('background-color', '#FFD700'), ('color', 'white'), ('font-size', '14px'),
                       ('border', f'1px solid {border_color}')]},
            # 테이블 테두리 및 글씨 굵게
            {'selector': '', 'props': [('border', f'3px solid {border_color}'), ('font-weight', 'bold')]},
            # 호버 효과
            {'selector': 'tbody tr:hover', 'props': [('background-color', hover_bg_color)]},
        ]).set_properties(**{'text-align': 'center'})
        return df_styled


    # 작은 테이블 표시
    st.markdown("---")

    # 첫 번째 행
    cols = st.columns(2)
    with cols[0]:
        st.subheader("⚽ 득점왕 랭크")
        df_goal_styled = style_small_dataframe(goal_rank)
        st.write(df_goal_styled.to_html(escape=False), unsafe_allow_html=True)
    with cols[1]:
        st.subheader("🎯 어시스트왕 랭크")
        df_assist_styled = style_small_dataframe(assist_rank)
        st.write(df_assist_styled.to_html(escape=False), unsafe_allow_html=True)

    # 두 번째 행
    cols = st.columns(2)
    with cols[0]:
        st.subheader("🏅 최대 MOM 랭크")
        df_mom_styled = style_small_dataframe(mom_rank)
        st.write(df_mom_styled.to_html(escape=False), unsafe_allow_html=True)
    with cols[1]:
        st.subheader("📊 경기당 공포 전환율 랭크")
        df_apg_styled = style_small_dataframe(apg_rank)
        st.write(df_apg_styled.to_html(escape=False), unsafe_allow_html=True)