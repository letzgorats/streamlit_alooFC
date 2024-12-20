import streamlit as st
import folium
from streamlit_folium import st_folium
from utils import load_image, get_match_counts_by_place,get_match_counts_with_coordinates
from dotenv import load_dotenv
import requests
import os
import json

def show_team_intro():
    st.header("Aloo FC 팀 소개 📢")
    # streamlit 기본 이미지 표시로 변경
    img = load_image("images/logo/alooFC_logo.png")

    if img:
        st.image(img, caption="Aloo FC 로고", width=200)
    st.write("Aloo FC는 풋살을 사랑하는 열정적인 팀입니다. 항상 최선을 다해 경기에 임합니다!")

    # 유니폼 이미지 (비율 고정 안함)
    st.markdown("## 👕 유니폼 소개")
    st.image("images/uniform/team_uniform.jpg", caption="Aloo FC 유니폼", width=400, use_column_width='auto')

    load_dotenv()
    KAKAO_JS_API_KEY = os.getenv("KAKAO_JS_API_KEY")  # JavaScript API 키 가져오기

    st.markdown("## 🌠 주 활동 지역")

    # 동적으로 데이터 가져오기
    locations = get_match_counts_with_coordinates()


    # 좌표가 없으면 에러 표시
    if not locations:
        st.error("장소 데이터를 가져오지 못했습니다. 주소 또는 API 키를 확인하세요.")
        return

    # JSON 변환
    locations_json = json.dumps(locations, ensure_ascii=False)


    # 좌표를 기반으로 카카오맵 JavaScript 삽입
    # 동적 로드를 위한 Kakao Maps HTML 및 JavaScript 코드
    # 지도 HTML 생성
    kakao_map_html = f"""
        <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
        <meta name="referrer" content="no-referrer">
        <div id="map" style="width:100%;height:500px;"></div>
        <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_API_KEY}&autoload=false&libraries=services"></script>
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                kakao.maps.load(function() {{
                    var mapContainer = document.getElementById('map'), 
                        mapOption = {{
                            center: new kakao.maps.LatLng({locations[0]['latitude']}, {locations[0]['longitude']}), 
                            level: 7
                        }};
                    var map = new kakao.maps.Map(mapContainer, mapOption);

                    var locations = {locations_json};
                    locations.forEach(function(location) {{
                        var marker = new kakao.maps.Marker({{
                            map: map,
                            position: new kakao.maps.LatLng(location.latitude, location.longitude)
                        }});
                        var infowindow = new kakao.maps.InfoWindow({{
                            content: `<div style="width:150px;text-align:center;">${{location.name}}<br>${{location.match_count}}회</div>`
                        }});
                        infowindow.open(map, marker);
                    }});
                }});
            }});
        </script>
    """
    st.components.v1.html(kakao_map_html, height=500)

    # 장소별 경기 횟수 표시
    st.markdown("### 📍 장소별 경기 횟수")
    for loc in locations:
        st.markdown(
            f"**🏟️ {loc['name']}** : <span style='color:green; font-size:20px;'>{loc['match_count']}회</span>",
            unsafe_allow_html=True
        )
