import psycopg2
import streamlit as st
from dotenv import load_dotenv
import os

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

# Streamlit 앱 실행
st.title("Aloo FC 팀 멤버 리스트")

# 팀 멤버 데이터를 가져와 출력
team_members = get_team_members()
for member in team_members:
    st.write(f"**이름:** {member[0]}, **사는 곳:** {member[1]}, **키:** {member[2]} cm, **신발 사이즈:** {member[3]} mm")
    st.write(f"**체형:** {member[4]}, **몸무게:** {member[5]} kg, **응원하는 팀:** {member[6]}")
    st.write(f"**각오 한 마디:** {member[7]}")
    st.write("---")
