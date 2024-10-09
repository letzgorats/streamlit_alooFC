import os
import psycopg2
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
from PIL import Image

# 데이터베이스 연결 함수
def create_connection():
    # Fly.io 환경에서 DATABASE_URL 환경 변수를 사용
    DATABASE_URL = os.getenv('DATABASE_URL')

    if DATABASE_URL:  # Fly.io 환경일 때는 DATABASE_URL 사용
        conn = psycopg2.connect(DATABASE_URL, sslmode='disable')  # 보안을 위해 'require' 사용
    else:  # 로컬 환경일 때는 .env 파일의 변수 사용
        load_dotenv()
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
    if os.getenv('DATABASE_URL') is None: # 로컬 환경일 때만 .env 파일 로드
        load_dotenv()
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

    res = supabase.storage.from_('player-profiles').create_signed_url(path, expires_in)
    if res:
        return res.get('signedURL')
    else:
        st.error("이미지 URL을 생성하는 데 실패했습니다.")
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








