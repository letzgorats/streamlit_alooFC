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
    <div style="display: inline-block; text-align: center; width: 50px;">
        <img src="{path}" style="width: 100%; height: auto !important;">
        <div style="font-size: 12px; font-weight: bold;">{name}</div>
    </div>
    '''

def show_player_stats():
    st.header("시즌별 선수 기록 🏅")

    # 현재 시즌 계산
    current_season = get_current_season()

    # 시즌 선택 옵션
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT season_name FROM seasons")
    seasons = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    # 시즌 리스트에 현재 시즌이 없을 경우 대비
    if current_season not in seasons:
        st.error(f"현재 시즌({current_season})이 seasons 테이블에 없습니다. 데이터베이스를 확인해주세요.")
        return

    selected_season = st.selectbox("시즌을 선택하세요:", seasons, index=seasons.index(current_season))

    # 안내 멘트 추가
    st.write("아래 표는 공격포인트 순으로 정렬되어 있습니다.")

    # 선택된 시즌의 선수 기록 가져오기
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
            SELECT
                tm.image_path_in_storage AS 이미지_경로,
                tm.first_name || ' ' || tm.last_name AS 이름,
                COALESCE(tm.jersey_number::TEXT, '') AS 등번호,
                COUNT(DISTINCT ps.match_id) AS 경기_횟수,
                COALESCE(SUM(ps.goals), 0) AS 골,
                COALESCE(SUM(ps.assists), 0) AS 어시스트,
                COALESCE(SUM(ps.goals + ps.assists), 0) AS 공격포인트,
                COALESCE(SUM(CASE WHEN ps.mom THEN 1 ELSE 0 END), 0) AS MOM_횟수,
                ROUND(COALESCE(SUM(ps.goals + ps.assists), 0)::numeric / NULLIF(COUNT(DISTINCT ps.match_id), 0), 2) AS 경기당_공포_전환율,
                CASE WHEN COUNT(DISTINCT ps.injury) = 1 AND MAX(ps.injury) = 'x' THEN 'x'
                     ELSE STRING_AGG(DISTINCT CASE WHEN ps.injury <> 'x' THEN ps.injury ELSE NULL END, ', ')
                END AS 부상현황
            FROM team_members tm
            LEFT JOIN player_stats ps ON tm.member_id = ps.member_id
            LEFT JOIN matches m ON ps.match_id = m.match_id
            LEFT JOIN seasons s ON m.season_id = s.season_id
            WHERE s.season_name = %s
            GROUP BY tm.member_id, tm.image_path_in_storage, tm.jersey_number
        """, (selected_season,))
    data = cur.fetchall()
    cur.close()
    conn.close()

    # 데이터프레임 생성
    df = pd.DataFrame(data,
                      columns=['이미지_경로', '이름', '등번호', '경기 횟수', '골', '어시스트', '공격포인트', 'MOM 횟수', '경기당 공포 전환율', '부상현황'])

    # 부상현황이 없을 경우 'x'로 표시
    df['부상현황'] = df['부상현황'].fillna('x')

    # 이미지 URL 생성
    df['이미지_URL'] = df['이미지_경로'].apply(get_image_url)


    df['선수'] = df.apply(lambda row: path_to_image_html_with_name(row['이미지_URL'], row['이름']), axis=1)

    # 불필요한 컬럼 제거 및 순서 조정
    df = df[['선수', '등번호', '경기 횟수', '골', '어시스트', '공격포인트', 'MOM 횟수', '경기당 공포 전환율', '부상현황']]

    # 공격포인트를 기준으로 정렬
    df.sort_values(by=['공격포인트', '골'], ascending=[False, False], inplace=True)

    # 인덱스 리셋 및 제거
    df.reset_index(drop=True, inplace=True)

    # 스타일 적용
    df_styled = df.style.format({'선수': lambda x: x})
    df_styled = df_styled.hide()  # 인덱스 숨기기
    df_styled = df_styled.set_table_styles([
        # 테이블 테두리 및 글씨 굵게
        {'selector': '', 'props': [('border', '3px solid #000'), ('font-weight', 'bold')]},
        {'selector': 'td', 'props': [('font-size', '12px'), ('color', 'inherit'), ('border', '1px solid #000')]},
        {'selector': 'th.col_heading',
         'props': [('background-color', '#4CAF50'), ('color', '#FFFFFF'), ('font-size', '14px'),
                   ('border', '1px solid #000')]},
        # 그림자 효과
        {'selector': '', 'props': [('box-shadow', '0 4px 8px 0 rgba(0, 0, 0, 0.2)')]},
        # 기타 스타일
        {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
        {'selector': 'tr:hover', 'props': [('background-color', '#f1f1f1')]},
    ]).set_properties(**{'text-align': 'center'})

    # 인덱스 제거하여 테이블 표시
    st.write(df_styled.to_html(escape=False), unsafe_allow_html=True)

    # 작은 테이블 생성
    # 최대 MOM 횟수 랭킹
    mom_rank = df[['선수', '경기 횟수', 'MOM 횟수']].sort_values(by='MOM 횟수', ascending=False).head(5)

    # 득점왕 랭크
    goal_rank = df[['선수', '경기 횟수', '골']].sort_values(by='골', ascending=False).head(5)

    # 어시스트왕 랭크
    assist_rank = df[['선수', '경기 횟수', '어시스트']].sort_values(by='어시스트', ascending=False).head(5)

    # 경기당 공포 전환율 랭크
    apg_rank = df[['선수', '경기당 공포 전환율']].sort_values(by='경기당 공포 전환율', ascending=False).head(5)

    # 작은 테이블 표시 (상단에 배치)
    st.markdown("---")  # 구분선 추가

    # 첫 번째 행
    cols = st.columns(2)

    with cols[0]:
        st.subheader("⚽ 득점왕 랭크")
        df_goal_styled = goal_rank.style.format({'선수': lambda x: x}).hide()
        df_goal_styled = df_goal_styled.set_table_styles([
            # 테이블 테두리 및 글씨 굵게
            {'selector': '', 'props': [('border', '3px solid #000'), ('font-weight', 'bold')]},
            {'selector': 'td', 'props': [('font-size', '10px'), ('color', 'inherit'), ('border', '1px solid #000')]},
            {'selector': 'th.col_heading',
             'props': [('background-color', '#FFD700'), ('color', '#000000'), ('font-size', '12px'),
                       ('border', '1px solid #000')]},
            # 그림자 효과
            {'selector': '', 'props': [('box-shadow', '0 4px 8px 0 rgba(255, 165, 0, 0.2)')]},  # 오렌지색 그림자
            # 기타 스타일
            {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
            {'selector': 'tr:hover', 'props': [('background-color', '#f1f1f1')]},
        ]).set_properties(**{'text-align': 'center'})
        st.write(df_goal_styled.to_html(escape=False), unsafe_allow_html=True)

    with cols[1]:
        st.subheader("🎯 어시스트왕 랭크")
        df_assist_styled = assist_rank.style.format({'선수': lambda x: x}).hide()
        df_assist_styled = df_assist_styled.set_table_styles([
            # 테이블 테두리 및 글씨 굵게
            {'selector': '', 'props': [('border', '3px solid #000'), ('font-weight', 'bold')]},
            {'selector': 'td', 'props': [('font-size', '10px'), ('color', 'inherit'), ('border', '1px solid #000')]},
            {'selector': 'th.col_heading',
             'props': [('background-color', '#FFD700'), ('color', '#000000'), ('font-size', '12px'),
                       ('border', '1px solid #000')]},
            # 그림자 효과
            {'selector': '', 'props': [('box-shadow', '0 4px 8px 0 rgba(255, 165, 0, 0.2)')]},  # 오렌지색 그림자
            # 기타 스타일
            {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
            {'selector': 'tr:hover', 'props': [('background-color', '#f1f1f1')]},
        ]).set_properties(**{'text-align': 'center'})
        st.write(df_assist_styled.to_html(escape=False), unsafe_allow_html=True)

    # 두 번째 행
    cols = st.columns(2)

    with cols[0]:
        st.subheader("🏅 최대 MOM 랭크")
        df_mom_styled = mom_rank.style.format({'선수': lambda x: x}).hide()
        df_mom_styled = df_mom_styled.set_table_styles([
            # 테이블 테두리 및 글씨 굵게
            {'selector': '', 'props': [('border', '3px solid #000'), ('font-weight', 'bold')]},
            {'selector': 'td', 'props': [('font-size', '10px'), ('color', 'inherit'), ('border', '1px solid #000')]},
            {'selector': 'th.col_heading',
             'props': [('background-color', '#FFD700'), ('color', '#000000'), ('font-size', '12px'),
                       ('border', '1px solid #000')]},
            # 그림자 효과
            {'selector': '', 'props': [('box-shadow', '0 4px 8px 0 rgba(255, 165, 0, 0.2)')]},  # 오렌지색 그림자
            # 기타 스타일
            {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
            {'selector': 'tr:hover', 'props': [('background-color', '#f1f1f1')]},
        ]).set_properties(**{'text-align': 'center'})
        st.write(df_mom_styled.to_html(escape=False), unsafe_allow_html=True)

    with cols[1]:
        st.subheader("📊 경기당 공포 전환율 랭크")
        df_apg_styled = apg_rank.style.format({'선수': lambda x: x}).hide()
        df_apg_styled = df_apg_styled.set_table_styles([
            # 테이블 테두리 및 글씨 굵게
            {'selector': '', 'props': [('border', '3px solid #000'), ('font-weight', 'bold')]},
            {'selector': 'td', 'props': [('font-size', '10px'), ('color', 'inherit'), ('border', '1px solid #000')]},
            {'selector': 'th.col_heading',
             'props': [('background-color', '#FFD700'), ('color', '#000000'), ('font-size', '12px'),
                       ('border', '1px solid #000')]},
            # 그림자 효과
            {'selector': '', 'props': [('box-shadow', '0 4px 8px 0 rgba(255, 165, 0, 0.2)')]},  # 오렌지색 그림자
            # 기타 스타일
            {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
            {'selector': 'tr:hover', 'props': [('background-color', '#f1f1f1')]},
        ]).set_properties(**{'text-align': 'center'})
        st.write(df_apg_styled.to_html(escape=False), unsafe_allow_html=True)