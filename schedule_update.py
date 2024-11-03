import requests
import os
from datetime import datetime
from utils import create_connection
import schedule
import time

def update_matches():
    matches = get_epl_matches_from_api()
    current_season_id = 1  # 현재 시즌 ID 설정
    save_matches_to_db(matches, current_season_id)
    print(f"{datetime.now()}: 경기 데이터 업데이트 완료")

# 스케줄 설정
schedule.every().saturday.at("06:30").do(update_matches)
schedule.every().sunday.at("06:30").do(update_matches)
schedule.every().monday.at("06:30").do(update_matches)
schedule.every().tuesday.at("06:30").do(update_matches)

while True:
    schedule.run_pending()
    time.sleep(1)

def get_epl_matches_from_api():
    API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
    headers = {
        'X-Auth-Token': API_KEY
    }
    url = 'https://api.football-data.org/v2/competitions/PL/matches'

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"API 호출 실패: {response.status_code}")
        return []

    data = response.json()
    matches = data['matches']
    return matches

def save_matches_to_db(matches, season_id):
    conn = create_connection()
    cur = conn.cursor()

    for match in matches:
        match_id = match['id']
        match_date_str = match['utcDate']  # ISO 형식 날짜 문자열
        match_date = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%M:%SZ")
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        home_team_id = match['homeTeam']['id']
        away_team_id = match['awayTeam']['id']
        status = match['status']

        # 결과 설정
        result = None
        if status == 'FINISHED':
            home_score = match['score']['fullTime']['homeTeam']
            away_score = match['score']['fullTime']['awayTeam']
            if home_score > away_score:
                result = '승'
            elif home_score == away_score:
                result = '무'
            else:
                result = '패'

        # 데이터베이스에 삽입 또는 업데이트
        cur.execute("""
            INSERT INTO epl_matches (match_id, season_id, match_date, home_team, away_team, home_team_id, away_team_id, result, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (match_id) DO UPDATE SET
                match_date = EXCLUDED.match_date,
                home_team = EXCLUDED.home_team,
                away_team = EXCLUDED.away_team,
                home_team_id = EXCLUDED.home_team_id,
                away_team_id = EXCLUDED.away_team_id,
                result = EXCLUDED.result,
                status = EXCLUDED.status;
        """, (match_id, season_id, match_date, home_team, away_team, home_team_id, away_team_id, result, status))

    conn.commit()
    cur.close()
    conn.close()
