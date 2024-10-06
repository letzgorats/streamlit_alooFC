import streamlit as st
import pandas as pd
import psycopg2
from utils import create_connection
import plotly.express as px
from utils import get_image_url, supabase

def show_attendance():
    st.header("팀 멤버 참석률 분석 📊")

    # 데이터베이스 연결
    conn = create_connection()
    cur = conn.cursor()

    # 참석 데이터 가져오기
    cur.execute("""
        SELECT tm.first_name || ' ' || tm.last_name AS full_name,
               COUNT(a.attendance_status) AS total_games,
               SUM(CASE WHEN a.attendance_status THEN 1 ELSE 0 END) AS attended_games
        FROM team_members tm
        LEFT JOIN attendance a ON tm.member_id = a.member_id
        GROUP BY tm.member_id
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    # 데이터프레임으로 변환
    df = pd.DataFrame(data, columns=['이름', '총 경기 수', '참석 경기 수'])
    df['참석률 (%)'] = (df['참석 경기 수'] / df['총 경기 수']) * 100

    # 참석률 순위표
    df_sorted = df.sort_values(by='참석률 (%)', ascending=False)

    # 참석률 그래프
    fig = px.bar(df_sorted, x='참석률 (%)', y='이름', orientation='h', color='참석률 (%)',
                 color_continuous_scale='Blues')
    st.plotly_chart(fig)

    # 참석왕 및 불참왕 계산
    max_attendance = df['참석률 (%)'].max()
    min_attendance = df['참석률 (%)'].min()

    attendance_kings = df[df['참석률 (%)'] == max_attendance]['이름'].tolist()
    absence_kings = df[df['참석률 (%)'] == min_attendance]['이름'].tolist()

    # 참석왕 표시
    st.subheader("🏆 참석왕")
    display_member_card(attendance_kings)

    # 불참왕 표시
    st.subheader("😢 불참왕")
    display_member_card(absence_kings)

    # 최근 2개월 데이터 처리
    show_recent_attendance()

def display_member_card(members):
    for member_name in members:
        # 멤버 정보 가져오기
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT first_name, last_name, role, position, image_path_in_storage
            FROM team_members
            WHERE first_name || ' ' || last_name = %s
        """, (member_name,))
        member_info = cur.fetchone()
        cur.close()
        conn.close()

        if member_info:
            first_name, last_name, role, position, image_path = member_info
            image_url = get_image_url(supabase, image_path)
            st.markdown(f"""
                <div class="card">
                    <img src="{image_url}" alt="{first_name} {last_name}">
                    <h4>{first_name} {last_name}</h4>
                    <p><strong>직책:</strong> {role}</p>
                    <p><strong>포지션:</strong> {position}</p>
                </div>
            """, unsafe_allow_html=True)

def show_recent_attendance():
    st.subheader("📅 최근 2개월 참석 현황")

    # 현재 날짜 기준 최근 두 달 계산
    from datetime import datetime, timedelta
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = last_month.replace(day=1)

    months = [first_day_of_last_month.strftime('%Y-%m'), first_day_of_current_month.strftime('%Y-%m')]

    conn = create_connection()
    cur = conn.cursor()

    # 각 월별 참석 데이터 가져오기
    for month in months:
        st.markdown(f"### {month} 참석 현황")
        cur.execute(f"""
            SELECT tm.first_name || ' ' || tm.last_name AS full_name,
                   SUM(CASE WHEN a.attendance_status THEN 1 ELSE 0 END) AS attended_games
            FROM team_members tm
            LEFT JOIN attendance a ON tm.member_id = a.member_id
            LEFT JOIN matches m ON a.match_id = m.match_id
            WHERE TO_CHAR(m.match_date, 'YYYY-MM') = %s
            GROUP BY tm.member_id
        """, (month,))
        data = cur.fetchall()

        df = pd.DataFrame(data, columns=['이름', '참석 경기 수'])
        df['참석 경기 수'] = df['참석 경기 수'].fillna(0)

        # 그래프 표시
        fig = px.bar(df, x='이름', y='참석 경기 수', color='참석 경기 수',
                     color_continuous_scale='Greens')
        st.plotly_chart(fig)

    cur.close()
    conn.close()
