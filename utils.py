import os
import psycopg2
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
from PIL import Image
import jwt
import datetime

# 로컬 환경에서만 .env 파일 로드
# if os.getenv('DATABASE_URL') is None:
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')  # 보안을 위해 실제 비밀 키를 사용하세요
if not SECRET_KEY:
    st.error("SECRET_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

# 데이터베이스 연결 함수
def create_connection():
    # Fly.io 환경에서 DATABASE_URL 환경 변수를 사용
    DATABASE_URL = os.getenv('DATABASE_URL')

    if DATABASE_URL:  # Fly.io 환경일 때는 DATABASE_URL 사용
        conn = psycopg2.connect(DATABASE_URL, sslmode='disable')  # 보안을 위해 'require' 사용
    else:  # 로컬 환경일 때는 .env 파일의 변수 사용
        # load_dotenv()
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5433")
        )
    return conn

# Fly.io 환경에서 DATABASE_URL 환경 변수를 사용하여 환경 구분
# Supabase 클라이언트 생성 함수
def get_supabase_client():
    # if os.getenv('DATABASE_URL') is None: # 로컬 환경일 때만 .env 파일 로드
        # load_dotenv()
    # supabase url 과 키 가져오기
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    # supabase 클라이언트 생성
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

supabase = get_supabase_client()


# 이미지 URL 생성 함수
@st.cache_data(ttl=604500)
def get_image_url(path):
    # URL 만료 시간 설정 (예: 1시간 후 만료)
    expires_in = 604800  # 초 단위

    try:
        res = supabase.storage.from_('player-profiles').create_signed_url(path, expires_in)
        if res and 'signedURL' in res:
            return res.get('signedURL')

        else:
            st.error("이미지 URL을 생성하는 데 실패했습니다.")
            return None
    except Exception as e:
        st.error(f"An error occurred while creating the signed URL: {e}")
        return None

# 이미지 로드 함수
@st.cache_data
def load_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        return img
    except Exception as e:
        st.error(f"이미지 로드 중 오류 발생: {e}")
        return None


def initialize_database():
    conn = create_connection()
    cur = conn.cursor()
    conn.commit()
    cur.close()
    conn.close()


def generate_password_reset_token(user_id):
    if not SECRET_KEY:
        st.error("SECRET_KEY가 설정되지 않았습니다.")
        return None

    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # 30분 유효
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    if isinstance(token, bytes):
        token = token.decode('utf-8')
    st.write(f"Generated token: {token}")  # 디버깅용
    return token

def verify_password_reset_token(token):
    if not SECRET_KEY:
        st.error("SECRET_KEY가 설정되지 않았습니다.")
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        st.write(f"Token payload: {payload}")  # 디버깅용
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        st.error("토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        st.error("유효하지 않은 토큰입니다.")
    return None


import smtplib
from email.mime.text import MIMEText

def send_reset_email(to_email, reset_link):
    from_email = 'a01030659322@gmail.com'
    from_password = os.getenv('EMAIL_PASSWORD')  # 이메일 계정 비밀번호

    # 이메일 내용
    message = f"""안녕하세요,

    다음 링크를 클릭하여 비밀번호를 재설정하세요:
    {reset_link}

    이 링크는 30분 동안만 유효합니다.

    감사합니다.
    """

    msg = MIMEText(message)
    msg['Subject'] = '비밀번호 재설정 요청'
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        st.error(f"이메일 전송 중 오류 발생: {e}")
        return False  # 이메일 전송 실패 시 False 반환

    return True  # 이메일 전송 성공 시 True 반환
