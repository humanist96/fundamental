import streamlit as st

st.set_page_config(
    page_title="KB-부동산원 지수 분석 & 주식 기대수익률 계산 & 경제 매크로",
    page_icon="👋",
)

st.write("# Welcome to 부동산 & 주식 데이터 분석! 👋")

st.sidebar.success("Select a menu above.")

st.markdown(
    """ 

    **👈 Select a menu from the sidebar** 

    ### Menu 설명
    - 📆 apt weekly : 한국부동산원과 KB에서 매주 발표하는 부동산 지수를 다양한 차트와 테이블로 아파트 주간 동향을 살펴 봄
    - 🈷️ apt monthly : 한국부동산원과 KB에서 매달 발표하는 부동산 지수를 다양한 차트와 테이블로 아파트 매월 동향을 살펴 봄
    - 📊_apt_real.py : 한국부동산원과 KB에서 매달 발표하는 설거래가 지수를 다양한 차트와 테이블로 아파트 매월 동향을 살펴 봄
    - 🏗️ rebuild house : 네이버 부동산에서 가져온 전국의 아파트분양권, 재개발, 재건축 매물 위치와 정보 확인
    - 🪙 macro : 국내, 미국 주요 매크로 차트 보기
    - ⚛️ korchart : 국내 상장 주식의 기대수익률과 기본적인 재무 데이터 차트 보기
    - 💸 us-chart : 미국 상장 주식의 기대수익률과 기본적인 재무 데이터 차트 보기
    ### See more 
    - Ask a question in my E-mail : <humanist96@gmail.com>
"""
)
