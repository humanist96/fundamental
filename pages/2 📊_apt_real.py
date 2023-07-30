import datetime
import numpy as np
import pandas as pd
import sqlite3
from urllib.request import urlopen
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import drawAPT_weekly 
import drawAPT_update
import seaborn as sns
import gspread
from oauth2client.service_account import ServiceAccountCredentials

cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)

#############html 영역####################
html_header="""
<head>
<title>Korea local house analysis</title>
<meta charset="utf-8">
<meta name="keywords" content="house data, dashboard, analysis, EVA">
<meta name="description" content="house data dashboard">
<meta name="author" content="indiesoul">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h1 style="font-size:200%; color:#008080; font-family:Georgia">  🈷️ 월간 아파트 실거래가지수 분석 <br>
 <hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="월간 아파트 실거래가격 지수", page_icon="files/logo2.png", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

pd.set_option('display.float_format', '{:.2f}'.format)
#오늘날짜까지
utcnow= datetime.datetime.utcnow()
time_gap= datetime.timedelta(hours=9)
kor_time= utcnow+ time_gap

st.cache_resource(ttl=datetime.timedelta(days=1))
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)#, check_same_thread=False)
    except Exception as e:
       print(e)

    return conn

@st.cache_data(ttl=datetime.timedelta(days=1))
#월간 데이터
def load_index_data(flag):
    index_list = []
    if flag == "real":
      query_list = ["select * from rmae", "select * from rjeon"]#, "SELECT * FROM jratio"]
      conn = create_connection("files/one_monthly.db")
    elif flag == 'one':
      query_list = ["select * from one_mae", "select * from one_jeon"]#, "SELECT * FROM jratio"]
      conn = create_connection("/content/one_monthly.db")
    else:
      query_list = ["select * from mae", "select * from jeon"]
      conn = create_connection("/content/kb_monthly.db")
    for query in query_list:
        df = pd.read_sql(query, conn, index_col='date', parse_dates={'date', "%Y-%m"})
        # query = conn.execute(query)
        # cols = [column[0] for column in query.description]
        # df= pd.DataFrame.from_records(
        #             data = query.fetchall(),
        #             columns = cols
        #     )
        #df.index = pd.to_datetime(df.index, format = '%Y-%m-%d')
        df = df.apply(lambda x:x.replace('#DIV/0!','0').replace('#N/A','0')).apply(lambda x:x.replace('','0')).astype(float)
        df = df.round(decimals=1)
        index_list.append(df)
    #kb_conn.close()

    return index_list


if __name__ == "__main__":
    data_load_state = st.text('Loading Index Data...')
    index_list = load_index_data()
    mdf = index_list[0]
    jdf = index_list[1]
    real_index_list = load_index_data("real")
    one_index_list = load_index_data("one")
    kb_index_list = load_index_data("kb")
    mdf = real_index_list[0]
    jdf = real_index_list[1]
    omdf = one_index_list[0]
    ojdf = one_index_list[1]
    kbmdf = kb_index_list[0]
    kbjdf = kb_index_list[1]

    last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
    onelast_month = pd.to_datetime(str(omdf.index.values[-1])).strftime('%Y.%m')
    kblast_month = pd.to_datetime(str(kbmdf.index.values[-1])).strftime('%Y.%m')
    st.markdown(f'실거래가 최종업데이트: **{last_month}월**')
    st.markdown(f'부동산원 최종업데이트: **{onelast_month}월**')
    st.markdown(f'KB 최종업데이트: **{kblast_month}월**')
    with st.expander("See Raw Data"):
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                try:
                    st.dataframe(mdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
                except ValueError :
                    st.dataframe(mdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
            with col2:
                st.write("")
            with col3: 
                try:
                    st.dataframe(jdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
                except ValueError :
                    st.dataframe(jdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))

     #월간 증감률
     #변화율로 봅시다
    mdf_change = mdf.pct_change()*100
    mdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    mdf_change = mdf_change.astype(float).fillna(0)
    omdf_ch = omdf.pct_change()*100
    kbmdf_ch = kbmdf.pct_change()*100
    #전세
    jdf_change = jdf.pct_change()*100
    jdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    jdf_change = jdf_change.astype(float).fillna(0)
    ojdf_ch = ojdf.pct_change()*100
    kbjdf_ch = kbjdf.pct_change()*100
    
    mdf_change = mdf_change.iloc[1:].round(decimals=1)
    omdf_ch = omdf_ch.iloc[1:].round(decimals=1)
    kbmdf_ch = kbmdf_ch.iloc[1:].round(decimals=1)
    jdf_change = jdf_change.iloc[1:].round(decimals=1)
    ojdf_ch = ojdf_ch.iloc[1:].round(decimals=1)
    kbjdf_ch = kbjdf_ch.iloc[1:].round(decimals=1)

    cum_mdf = (1+mdf_change/100).cumprod() -1
    cum_mdf = cum_mdf.round(decimals=3)
    cum_jdf = (1+jdf_change/100).cumprod() -1
    cum_jdf = cum_jdf.round(decimals=3)
    

    #여기서부터는 선택
    my_choice = st.sidebar.radio(
                    "Select Menu", ('Basic','Index', 'Together'))
    if my_choice == 'Basic':
        mdf = mdf.loc['2006-01-01':]
        omdf = omdf.loc['2006-01-01':]
        kbmdf = kbmdf.loc['2006-01-01':]
        mdf_ch = mdf_change.loc['2006-01-01':]
        omdf_ch = omdf.loc['2006-01-01':]
        kbmdf_ch = kbmdf.loc['2006-01-01':]

        jdf = jdf.loc['2006-01-01':]
        ojdf = ojdf.loc['2006-01-01':]
        kbjdf = kbjdf.loc['2006-01-01':]
        jdf_ch = jdf_change.loc['2006-01-01':]
        ojdf_ch = ojdf_ch.loc['2006-01-01':]
        kbjdf_ch = kbjdf_ch.loc['2006-01-01':]

        # 데이터프레임의 컬럼명 추출 후, 같은 이름을 가진 컬럼만 병합
        common_col = list(set(mdf.columns.tolist()) & set(omdf.columns.tolist()) & set(kbmdf.columns.tolist()))
        submit = st.sidebar.button('지수 같이 보기')

        city_series = pd.Series(common_col)
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', common_col
            )

        if submit:
            tab1, tab2 = st.tabs(["⏰ 매매지수", "🗺️ 전세지수"])
            with tab1: #매매지수
                drawAPT_update.draw_index_together(selected_dosi, mdf, omdf, kbmdf, mdf_ch, omdf_ch, kbmdf_ch, "매매지수")
            with tab2: #매매지수
                drawAPT_update.draw_index_together(selected_dosi, jdf, ojdf, kbjdf, jdf_ch, ojdf_ch, kbjdf_ch, "전세지수")
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
    elif my_choice == 'Index':
        
        column_list = mdf.columns.to_list()
        city_series = pd.Series(column_list)
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', column_list
            )
    
        submit = st.sidebar.button('Draw Price Index')

        if submit:
        ### Block KB 지수 #########################################################################################
            flag = "아파트 실거래가격지수 "
            drawAPT_update.run_price_index(selected_dosi, selected_dosi, mdf, jdf, mdf_change, jdf_change, flag)
            ##매매/전세 tab 으로 구분하자.
            tab1, tab2 = st.tabs(["⏰ 매매지수", "🗺️ 전세지수"])
            with tab1: #매매지수

                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1: #4년 그래프와 평균 
                        try:
                            drawAPT_update.draw_4years_index(selected_dosi, mdf_change, "mae")
                        except Exception as e:
                            st.write(e)
                    with col2:
                        st.write("")
                    with col3:
                        try:
                            monthly_slice = mdf_change.loc[mdf_change.index.month == mdf_change.index[-1].month]
                            monthly_slice = monthly_slice.round(decimals=1)
                            col1, col2 = st.columns(2) 
                            col1.metric(label=str(datetime.datetime.utcnow().month)+"월", value = str(round(monthly_slice.loc[:,selected_dosi][-1],1))+"%")
                            col2.metric(label=str(datetime.datetime.utcnow().month)+"월 평균", value = str(round(monthly_slice.loc[:,selected_dosi].mean(),1))+"%")
                            titles = dict(text= '<b>['+selected_dosi +'] 연도별 ' +str(datetime.datetime.utcnow().month) +'월 매매가격 변동</b>', x=0.5, y = 0.9, xanchor='center', yanchor= 'top')
                            fig = px.bar(
                                    monthly_slice,
                                        x=monthly_slice.index.year,
                                        y=selected_dosi,
                                        color=selected_dosi,
                                        hover_name=selected_dosi,
                                        text=selected_dosi
                                    )
                            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template="ggplot2", xaxis_tickformat = '%Y')
                            st.plotly_chart(fig)
                        except Exception as e:
                            st.write(e)
                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        flag = "아파트 실거래가격지수 "
                        try:
                            drawAPT_update.basic_chart(selected_dosi, mdf, mdf_change, "mae")
                        except Exception as e:
                            st.write(e)
                    with col2:
                        st.write("")
                    with col3:
                        flag = "아파트 실거래가격지수 "
                        drawAPT_update.draw_flower(selected_dosi, selected_dosi, cum_mdf, cum_jdf, flag)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            with tab2: #전세지수
                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1: #4년 그래프와 평균 
                        try:
                            drawAPT_update.draw_4years_index(selected_dosi, jdf_change, "jeon")
                        except Exception as e:
                            st.write(e)
                    with col2:
                        st.write("")
                    with col3:
                        try:
                            monthly_slice = jdf_change.loc[jdf_change.index.month == jdf_change.index[-1].month]
                            monthly_slice = monthly_slice.round(decimals=1)
                            col1, col2 = st.columns(2) 
                            col1.metric(label=str(datetime.datetime.utcnow().month)+"월", value = str(round(monthly_slice.loc[:,selected_dosi][-1],1))+"%")
                            col2.metric(label=str(datetime.datetime.utcnow().month)+"월 평균", value = str(round(monthly_slice.loc[:,selected_dosi].mean(),1))+"%")
                            titles = dict(text= '<b>['+selected_dosi +'] 연도별 ' +str(datetime.datetime.utcnow().month) +'월 매매가격 변동</b>', x=0.5, y = 0.9, xanchor='center', yanchor= 'top')
                            fig = px.bar(
                                    monthly_slice,
                                        x=monthly_slice.index.year,
                                        y=selected_dosi,
                                        color=selected_dosi,
                                        hover_name=selected_dosi,
                                        text=selected_dosi
                                    )
                            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template="ggplot2", xaxis_tickformat = '%Y')
                            st.plotly_chart(fig)
                        except Exception as e:
                            st.write(e)
                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        flag = "아파트 실거래가격지수 "
                        try:
                            drawAPT_update.basic_chart(selected_dosi, jdf, jdf_change, "jeon")
                        except Exception as e:
                            st.write(e)
                    with col2:
                        st.write("")
                    with col3:
                        flag = "아파트 실거래가격지수 "
                        drawAPT_update.draw_flower(selected_dosi, selected_dosi, cum_mdf, cum_jdf, flag)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
    else: #KB는 자체적으로 볼때, 지역 같이 볼 때는 부동산원만 
        #지역과 기간 같이 보기
        period_ = mdf.index.strftime("%Y-%m").tolist()
        st.subheader("지역별 기간 상승률 분석")
        start_date, end_date = st.select_slider(
            'Select Date to Compare index change', 
            options = period_,
            value = (period_[0], period_[-1]))
        
        #부동산원 / KB
        slice_om = mdf.loc[start_date:end_date]
        slice_oj = jdf.loc[start_date:end_date]
        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
        diff = slice_om.index[-1] - slice_om.index[0]
        #information display
        cols = st.columns(4)
        cols[0].write(f"시작: {start_date}")
        cols[1].write(f"끝: {end_date}")
        cols[2].write(f"전체 기간: {round(diff.days/365,1)} 년")
        cols[3].write("")
        #st.dataframe(slice_om)
        change_odf = pd.DataFrame()
        change_odf['매매증감'] = (slice_om.iloc[-1]/slice_om.iloc[0]-1).to_frame()*100
        change_odf['전세증감'] = (slice_oj.iloc[-1]/slice_oj.iloc[0]-1).to_frame()*100
        change_odf = change_odf.dropna().astype(float).round(decimals=2)
        change_df = pd.DataFrame()
        change_df['매매증감'] = (slice_m.iloc[-1]/slice_m.iloc[0]-1).to_frame()*100
        change_df['전세증감'] = (slice_j.iloc[-1]/slice_j.iloc[0]-1).to_frame()*100
        change_df = change_df.dropna().astype(float).round(decimals=2)
        #상승률 누적
        slice_om = mdf.loc[start_date:end_date]
        slice_oj = jdf.loc[start_date:end_date]
        slice_om_ch = mdf_change.loc[start_date:end_date]
        slice_oj_ch = jdf_change.loc[start_date:end_date]
        slice_om_ch = slice_om_ch.round(decimals=2)
        slice_oj_ch = slice_oj_ch.round(decimals=2)
        slice_cum_omdf = (1+slice_om_ch/100).cumprod() -1
        slice_cum_omdf = slice_cum_omdf.round(decimals=4)
        slice_cum_ojdf = (1+slice_oj_ch/100).cumprod() -1
        slice_cum_ojdf = slice_cum_ojdf.round(decimals=4)

        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
        slice_m_ch = mdf_change.loc[start_date:end_date]
        slice_j_ch = jdf_change.loc[start_date:end_date]
        slice_m_ch = slice_m_ch.round(decimals=2)
        slice_j_ch = slice_j_ch.round(decimals=2)
        slice_cum_mdf = (1+slice_m_ch/100).cumprod() -1
        slice_cum_mdf = slice_cum_mdf.round(decimals=4)
        slice_cum_jdf = (1+slice_j_ch/100).cumprod() -1
        slice_cum_jdf = slice_cum_jdf.round(decimals=4)


        #지역 같이 
        citys = mdf.columns.tolist()
        options = st.multiselect('Select City to Compare index', citys, citys[:3])
        submit = st.button('analysis')
        if submit:
            ### 부동산원 index chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = '아파트 실거래가격 '
                    drawAPT_weekly.run_one_index_together(options, slice_om, slice_om_ch, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '아파트 실거래가격 '
                    drawAPT_weekly.run_one_jindex_together(options, slice_oj, slice_oj_ch, flag)
                    
            html_br="""
            <br>
            """ 
            ### KB index chart #########################################################################################
            # with st.container():
            #     col1, col2, col3 = st.columns([30,2,30])
            #     with col1:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.run_one_index_together(options, slice_m, slice_m_ch, flag)

            #     with col2:
            #         st.write("")
            #     with col3:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.run_one_jindex_together(options, slice_j, slice_j_ch, flag)
                    
            # html_br="""
            # <br>
            # """ 
            ### 부동산원 Bubble/ flower chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = '아파트 실거래가격'
                    drawAPT_weekly.draw_index_change_with_bubble_slice(options, change_odf, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '아파트 실거래가격'
                    drawAPT_weekly.draw_flower_together(options, slice_cum_omdf, slice_cum_ojdf, flag)
                    
            html_br="""
            <br>
            """             
            ### KB Bubble/ flower chart #########################################################################################
            # with st.container():
            #     col1, col2, col3 = st.columns([30,2,30])
            #     with col1:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.draw_index_change_with_bubble_slice(options, change_df, flag)

            #     with col2:
            #         st.write("")
            #     with col3:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.draw_flower_together(options, slice_cum_mdf, slice_cum_jdf, flag)
                    
            # html_br="""
            # <br>
            # """               
    
html_br="""
<br>
"""

html_line="""

<br>
<br>
<br>
<br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;">
<p style="color:Gainsboro; text-align: right;">By: 기하급수적 https://blog.naver.com/indiesoul2 / sizipusx2@gmail.com</p>
"""
st.markdown(html_line, unsafe_allow_html=True)