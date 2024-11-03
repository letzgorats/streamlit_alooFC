import streamlit as st
from utils import create_connection
from datetime import datetime, timedelta
import pandas as pd

def prediction_app():
    st.header("EPL 경기 예측 투표 ⚽")

    if 'user_id' not in st.session_state:
        st.error("로그인이 필요합니다.")
        return

    user_id = st.session_state['user_id']

    now = datetime.utcnow()

    conn = create_connection()
    cur = conn.cursor()

    # 예정된 경기 목록 가져오기
    cur.execute("""
        SELECT match_id, home_team, away_team, match_date
        FROM epl_matches
        WHERE status = 'SCHEDULED'
        ORDER BY match_date ASC
    """)
    matches = cur.fetchall()

    if not matches:
        st.info("예측할 수 있는 경기가 없습니다.")
        return

    predictions = {}

    for match in matches:
        match_id, home_team, away_team, match_date = match

        # 예측 제출 기한 확인 (경기 시작 30분 전까지)
        deadline = match_date - timedelta(minutes=30)
        if now > deadline:
            continue

        st.subheader(f"{home_team} vs {away_team} ({match_date.strftime('%Y-%m-%d %H:%M')} UTC)")

        # 이미 예측을 제출했는지 확인
        cur.execute("""
            SELECT prediction FROM predictions
            WHERE user_id = %s AND match_id = %s
        """, (user_id, match_id))
        existing_prediction = cur.fetchone()

        if existing_prediction:
            st.write(f"이미 예측을 제출하셨습니다: **{existing_prediction[0]}**")
        else:
            prediction = st.radio(
                label="예측 결과를 선택하세요:",
                options=[f"{home_team} 승", "무승부", f"{away_team} 승"],
                key=f"prediction_{match_id}"
            )
            predictions[match_id] = prediction

    if predictions:
        if st.button("예측 제출"):
            save_prediction(user_id,predictions)
            st.success("예측이 제출되었습니다.")
            st.rerun()
    else:
        st.info("예측할 경기가 없거나 모든 경기에 대한 예측을 이미 제출하셨습니다.")

    cur.close()
    conn.close()

def save_prediction(user_id, predictions):
    conn = create_connection()
    cur = conn.cursor()
    try:
        for match_id, prediction in predictions.items():
            cur.execute("""
                        INSERT INTO predictions (user_id, match_id, prediction)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, match_id) DO NOTHING;
                    """, (user_id, match_id, prediction))
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"예측 저장 중 오류 발생: {e}")
    finally:
        cur.close()
        conn.close()

def calculate_prediction_rates():
    st.header("예측률 순위표 📊")

    conn = create_connection()
    cur = conn.cursor()

    # 모든 사용자 가져오기
    cur.execute("SELECT user_id, username FROM users")
    users = cur.fetchall()

    data = []

    for user in users:
        user_id, username = user

        # 총 예측 경기 수
        cur.execute("""
            SELECT COUNT(*) FROM predictions
            WHERE user_id = %s
        """, (user_id,))
        total_predictions = cur.fetchone()[0]

        if total_predictions == 0:
            continue

        # 맞춘 경기 수 계산
        cur.execute("""
            SELECT COUNT(*)
            FROM predictions p
            JOIN epl_matches m ON p.match_id = m.match_id
            WHERE p.user_id = %s AND m.status = 'FINISHED' AND (
                (p.prediction = %s AND m.result = '승') OR
                (p.prediction = '무승부' AND m.result = '무') OR
                (p.prediction = %s AND m.result = '패')
            )
        """, (user_id, f"{username} 승", f"{username} 승"))
        correct_predictions = cur.fetchone()[0]

        # 예측률 계산
        accuracy = (correct_predictions / total_predictions) * 100

        data.append({
            '사용자명': username,
            '예측 경기 수': total_predictions,
            '맞춘 경기 수': correct_predictions,
            '예측 성공률 (%)': round(accuracy, 2)
        })

    df = pd.DataFrame(data)
    if df.empty:
        st.info("예측 데이터가 없습니다.")
        return

    df = df.sort_values(by='예측 성공률 (%)', ascending=False)

    st.dataframe(df)

    # '축잘알'과 '축알못' 멤버 표시
    display_experts_and_novices(df)

    cur.close()
    conn.close()

def display_experts_and_novices(df):
    highest_accuracy = df['예측 성공률 (%)'].max()
    lowest_accuracy = df['예측 성공률 (%)'].min()

    experts = df[df['예측 성공률 (%)'] == highest_accuracy]['사용자명'].tolist()
    novices = df[df['예측 성공률 (%)'] == lowest_accuracy]['사용자명'].tolist()

    st.subheader("🎉 축잘알 멤버")
    st.write(", ".join(experts))

    st.subheader("😅 축알못 멤버")
    st.write(", ".join(novices))
