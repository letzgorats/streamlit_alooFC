import streamlit as st
import folium
from streamlit_folium import st_folium
from utils import load_image, get_match_counts_by_place
from dotenv import load_dotenv
import requests
import os

load_dotenv()
KAKAO_JS_API_KEY = os.getenv("KAKAO_JS_API_KEY")  # JavaScript API 키 가져오기
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")  # REST API 키 가져오기

# 주소를 좌표로 변환하는 함수
def get_coordinates(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": address}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()
        if result["documents"]:
            y = result["documents"][0]["y"]  # 위도
            x = result["documents"][0]["x"]  # 경도
            return float(y), float(x)
    return None, None


def show_team_intro():
    st.header("Aloo FC 팀 소개 📢")
    st.write("Aloo FC 로고:")
    # streamlit 기본 이미지 표시로 변경
    img = load_image("images/logo/alooFC_logo.png")

    if img:
        st.image(img, caption="Aloo FC 로고", width=200)
    st.write("Aloo FC는 풋살을 사랑하는 열정적인 팀입니다. 항상 최선을 다해 경기에 임합니다!")

    # 유니폼 이미지 (비율 고정 안함)
    st.markdown("## 👕 유니폼 소개")
    st.image("images/uniform/team_uniform.jpg", caption="Aloo FC 유니폼", width=400, use_column_width='auto')

    st.markdown("## 🌠 주 활동 지역")

    # 37.5163550343008
    # 126.779867163442

    # 주소를 기반으로 좌표를 가져오기
    address = "경기 부천시 원미구 옥산로 255 4층"
    latitude, longitude = get_coordinates(address)


    if latitude is None or longitude is None:
        st.error("주소를 변환할 수 없습니다.")
        return

    # 장소별 경기 횟수 데이터 불러오기
    match_counts_df = get_match_counts_by_place()
    bucheon_clear_count = match_counts_df[match_counts_df['place'] == '부천 클리어 풋살장']['match_count'].values[0]

    # 좌표를 기반으로 카카오맵 JavaScript 삽입
    # 동적 로드를 위한 Kakao Maps HTML 및 JavaScript 코드
    kakao_map_html = f"""
            <meta name="referrer" content="no-referrer">
            <div id="map" style="width:100%;height:500px;"></div>
            <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_API_KEY}&autoload=false&libraries=services"></script>
            <script>
                kakao.maps.load(function() {{
                    var mapContainer = document.getElementById('map'), 
                        mapOption = {{
                            center: new kakao.maps.LatLng({latitude}, {longitude}), 
                            level: 3
                        }};
                    var map = new kakao.maps.Map(mapContainer, mapOption);

                    // 마커 설정
                    var marker = new kakao.maps.Marker({{
                        map: map,
                        position: new kakao.maps.LatLng({latitude}, {longitude})
                    }});

                    // 인포윈도우로 장소에 대한 설명 표시
                    var infowindow = new kakao.maps.InfoWindow({{
                        content: '<div style="width:150px;text-align:center;padding:6px 0;">부천 클리어 풋살장<br>{bucheon_clear_count}회</div>'
                    }});
                    infowindow.open(map, marker);
                }});
            </script>
        """

    st.components.v1.html(kakao_map_html, height=500)

    # 장소별 경기 횟수 표시
    st.markdown("### 📍 장소별 경기 횟수")
    for _, row in match_counts_df.iterrows():
        place_text = f"**🏟️ {row['place']}**"
        count_text = f"<span style='color:green; font-size:20px;'>{row['match_count']}회</span>"
        st.markdown(f"{place_text} : {count_text}", unsafe_allow_html=True)


    # # 부천 클리어 풋살장의 좌표
    # bucheon_clear_futsal_location = [37.505653, 126.753796]
    # # Folium 지도 생성 (부천 클리어 풋살장의 좌표로 설정)
    # m = folium.Map(location=bucheon_clear_futsal_location, zoom_start=12)
    #
    # # 부천 클리어 풋살장 마커 추가
    # folium.Marker(
    #     location=bucheon_clear_futsal_location,
    #     popup="부천 클리어 풋살장",
    #     icon=folium.Icon(color='green', icon='info-sign')
    # ).add_to(m)
    #
    # # 목동의 좌표
    # mokdong_location = [37.5326, 126.8746]
    #
    # # 목동 마커 추가
    # folium.Marker(
    #     location=mokdong_location,
    #     popup="목동",
    #     icon=folium.Icon(color='blue', icon='info-sign')
    # ).add_to(m)
    #
    # # Folium 지도를 Streamlit에 표시
    # st_folium(m, width=700, height=500)





