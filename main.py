import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Aloo FC")

# 출석률 데이터
data = {
    'name':['김정엽','김상민','변장석','전영성'],
    'August' : [1, 1, 1, 1],
    'September': [0, 0, 0, 0],
    'October': [0, 0, 0, 0],
    'November': [0, 0, 0, 0],
    'December': [0, 0, 0, 0],
    'January': [0, 0, 0, 0],
    'February': [0, 0, 0, 0],
    'March': [0, 0, 0, 0],
    'April': [0, 0, 0, 0],
    'May': [0, 0, 0, 0],
    'June': [0, 0, 0, 0],
    'July': [0, 0, 0, 0],
}

df = pd.DataFrame(data)

# 출석률 계산
df['Attendance Rate'] = df.iloc[:, 1:].mean(axis=1) * 100

# 출석률에 의해 정렬
df = df.sort_values('Attendance Rate',ascending=False)

# Stremlit UI
st.title('Aloo FC 월별 출석률')
st.table(df)

# 출석률 시각화
plt.figure(figsize=(10,5))
plt.bar(df['name'],df['Attendance Rate'])
plt.xlabel('Player')
plt.ylabel('Attendance Rate(%)')
plt.title('출석률')
st.pyplot(plt)