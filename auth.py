# auth.py

import streamlit as st
from utils import create_connection,send_reset_email,verify_password_reset_token,generate_password_reset_token
from werkzeug.security import generate_password_hash, check_password_hash
import urllib.parse

def signup():
    st.title("회원가입")
    username = st.text_input("사용자명", key="signup_username")
    email = st.text_input("이메일 주소", key="signup_email")
    password = st.text_input("비밀번호", type="password", key="signup_password")
    password_confirm = st.text_input("비밀번호 확인", type="password", key="signup_password_confirm")
    if st.button("회원가입", key="signup_button"):
        if not username or not email or not password or not password_confirm:
            st.warning("모든 필드를 입력해주세요.")
        elif password != password_confirm:
            st.error("비밀번호가 일치하지 않습니다.")
        else:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            if cur.fetchone():
                st.error("이미 존재하는 사용자명 또는 이메일입니다.")
            else:
                hashed_password = generate_password_hash(password)
                cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
                conn.commit()
                st.success("회원가입이 완료되었습니다. 로그인해주세요.")
                st.info("로그인 페이지로 이동합니다.")
                st.session_state['show_signup'] = False
                st.rerun()
            cur.close()
            conn.close()

def reset_password():
    st.title("비밀번호 재설정")
    email = st.text_input("가입한 이메일 주소를 입력하세요", key="reset_email")
    if st.button("비밀번호 재설정 링크 보내기", key="reset_button"):
        if not email:
            st.warning("이메일 주소를 입력해주세요.")
        else:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if user:
                user_id = user[0]
                # 비밀번호 재설정 토큰 생성
                reset_token = generate_password_reset_token(user_id)
                if reset_token is None:
                    st.error("토큰 생성에 실패했습니다.")
                    return
                # # 토큰을 문자열로 변환 (PyJWT 버전에 따라 필요)
                # if isinstance(reset_token, bytes):
                #     reset_token = reset_token.decode('utf-8')
                # 토큰을 URL 인코딩
                encoded_token = urllib.parse.quote(reset_token)
                # 이메일로 비밀번호 재설정 링크 전송
                reset_link = f"http://localhost:8501?token={encoded_token}"
                email_sent = send_reset_email(email, reset_link)
                if email_sent:
                    st.success("비밀번호 재설정 링크를 이메일로 전송했습니다.")
                else:
                    st.error("이메일 전송에 실패했습니다. 이메일 주소를 확인하거나 나중에 다시 시도해주세요.")
            else:
                st.error("해당 이메일로 가입된 사용자가 없습니다.")
            cur.close()
            conn.close()

def reset_password_confirm(token):
    st.title("비밀번호 재설정")

    # 토큰을 URL 디코딩
    token = urllib.parse.unquote(token)
    # 토큰을 문자열로 변환 (PyJWT 버전에 따라 필요)
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    user_id = verify_password_reset_token(token)
    if user_id is None:
        return

    new_password = st.text_input("새로운 비밀번호를 입력하세요", type="password", key="new_password")
    new_password_confirm = st.text_input("새로운 비밀번호 확인", type="password", key="new_password_confirm")

    if st.button("비밀번호 재설정", key="confirm_reset_button"):
        if not new_password or not new_password_confirm:
            st.warning("모든 필드를 입력해주세요.")
        elif new_password != new_password_confirm:
            st.error("비밀번호가 일치하지 않습니다.")
        else:
            conn = create_connection()
            cur = conn.cursor()
            hashed_password = generate_password_hash(new_password)
            cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (hashed_password, user_id))
            conn.commit()
            cur.close()
            conn.close()
            st.success("비밀번호가 재설정되었습니다. 로그인해주세요.")
            st.rerun()


def login():
    st.title("로그인")
    username = st.text_input("사용자명", key="login_username")
    password = st.text_input("비밀번호", type="password", key="login_password")
    if st.button("로그인", key="login_button"):
        if username and password:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_id, password FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            if user and check_password_hash(user[1], password):
                st.session_state['user_id'] = user[0]
                st.session_state['username'] = username
                st.session_state['logged_in'] = True
                st.success(f"{username}님, 환영합니다!")
                st.rerun()
            else:
                st.error("사용자명 또는 비밀번호가 올바르지 않습니다.")
            cur.close()
            conn.close()
        else:
            st.warning("모든 필드를 입력해주세요.")

    st.write("계정이 없으신가요?")
    if st.button("회원가입", key="show_signup_button"):
        st.session_state['show_signup'] = True
        st.rerun()

    st.write("비밀번호를 잊으셨나요?")
    if st.button("비밀번호 재설정", key="reset_password_button"):
        st.session_state['show_reset_password'] = True
        st.rerun()

def logout():
    st.session_state.clear()
    st.success("로그아웃되었습니다.")
    st.rerun()

def is_logged_in():
    return st.session_state.get('logged_in', False)
