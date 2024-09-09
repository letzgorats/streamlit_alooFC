# 베이스 이미지로 파이썬 사용
FROM python:3.11

# 작업 디렉터리 설정
WORKDIR /app

# 필요 패키지 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# Streamlit 포트 설정
EXPOSE 8501

# Streamlit 앱 실행 명령어
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
