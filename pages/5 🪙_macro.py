
import pandas as pd
import requests
import json
import streamlit as st
from pandas.io.json import json_normalize
import numpy as np
#from tqdm.notebook import tqdm as tn
import time
import datetime
import FinanceDataReader as fdr
import ecos_chart as ec
import seaborn as sns
cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)

utcnow= datetime.datetime.utcnow()
time_gap= datetime.timedelta(hours=9)
kor_time= utcnow+ time_gap

pd.set_option('display.float_format', '{:.2f}'.format)
#############html 영역####################
html_header="""
<head>
<title>Ecos chart</title>
<meta charset="utf-8">
<meta name="keywords" content="chart, analysis">
<meta name="description" content="House data analysis">
<meta name="author" content="indiesoul">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h2 style="font-size:200%; color:#008080; font-family:Georgia">경제 Macro 조회<br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="Macro 조회", page_icon="files/logo2.png", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)


@st.cache_data(ttl=datetime.timedelta(days=1))
def query_ecos(stat_code, stat_item, start_date, end_date, cycle_type="Q"):
    auth_key = "71BO71RCBA99FVU3BETA/" #발급 받은 Key 를 넣으면 더 많은 데이터 수집 가능
    req_type = "json/"
    lang = "kr/"
    start_no = "1/"
    end_no ="10000/"
    stat_code = stat_code + "/"
    #stat_code = stat_code.split('/')[0] + "/"
    cycle_type = cycle_type + "/"
    start_date = start_date + "/"
    end_date = end_date + "/"
    #item_no = stat_code.split('/')[1]
    item_no = stat_item

    url = "http://ecos.bok.or.kr/api/StatisticSearch/" +  \
        auth_key + req_type + lang + start_no + end_no + \
        stat_code + cycle_type + start_date + end_date + item_no
    print(url)
    r = requests.get(url)
    if '해당하는 데이터가 없습니다' in r.text:
        return None
    
    jo = json.loads(r.text)
    print(jo)
    df = json_normalize(jo['StatisticSearch']['row'])
    if cycle_type != 'Q':
        df['TIME'] = df['TIME'] + '0101'
        df['TIME'] = df['TIME'].str.replace(r'(\d{4})(\d{2})(\d{2})(.*)', r'\1-\2-\3')
    return df

def run(stat_ticker, kor_exp):
    start_date = "200010"
    end_date = kor_time.strftime('%Y%m')
    cycle_type = "M"
    if source == 'Ecos':
        if stat_ticker == '901Y009':
            item_symbols = {'소비자물가지수':'901Y009/0','생산자물가지수':'404Y014/*AA'}
        elif stat_ticker == '721Y001':
             item_symbols =  {'국고채(3년)':'721Y001/5020000','국고채(10년)':'721Y001/5050000', '기준금리':'722Y001/0101000'} 
        elif stat_ticker == '402Y014':
            item_symbols = {'수출금액지수':'403Y001/*AA','수입금액지수':'403Y003/*AA'}
        elif stat_ticker == '104Y014':
            item_symbols = {'예금은행 총수신(말잔)':'104Y013/BCB8', '비예금은행 총수신(말잔)':'111Y007/1000000', '예금은행 대출금(말잔)':'104Y016/BDCA1', '비예금은행 대출금(말잔)':'111Y009/1000000'}
        elif stat_ticker == '151Y005':
        #가계 신용: 가계 저축과 가계대출(주택담보대출+기타대출) + 판매신용
            item_symbols = {'주택담보대출':'151Y005/11100A0','기타대출':'151Y005/11100B0'}
        elif stat_ticker == '722Y001':
            item_symbols = {'한국은행기준금리':'722Y001/0101000'}
        else:
            item_symbols = {'가계대출':'121Y006/BECBLA03', '저축성수신':'121Y002/BEABAA2', '기준금리':'722Y001/0101000'}
        item_index_tickers = list(item_symbols.values())
        all_data = {}
        for ticker in item_index_tickers:
            stat_code = ticker.split('/')[0]
            stat_item = ticker.split('/')[1]
            #stat_item = ticker.split('/')[2]
            all_data[ticker] = query_ecos(stat_code, stat_item, start_date, end_date, cycle_type)    
        #컬럼명 종목명으로 변경
        data_df = pd.DataFrame({tic: data['DATA_VALUE'] for tic, data in all_data.items()})
        data_df.columns = item_symbols.keys()
        #날짜 설정
        tempdf = all_data.get(item_index_tickers[0])
        data_df.set_index(keys=tempdf['TIME'], inplace=True)
        with st.expander("See Raw Data"):
            try:
                st.dataframe(data_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
            except ValueError :
                st.dataframe(data_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
        if stat_ticker == '151Y005' or stat_ticker == '104Y014':#예금/대출일 경우 조 단위로 변경
            data_df = data_df.astype(float)/1000
            data_df = data_df.round(decimals=1)
            data_ch = data_df.pct_change()*100
            data_ch = data_ch.round(decimals=2)
            ec.ecos_monthly_chart(kor_exp, data_df, data_ch)
        elif stat_ticker == '721Y001': #장단기금리차
            data_df = data_df.astype(float).round(2)
            data_df.loc[:,"장단기금리차"] = round(data_df.loc[:,'국고채(10년)'] - data_df.loc[:,'국고채(3년)'],2)    
            data_df.loc[:,'color'] = np.where(data_df['장단기금리차']<0, 'red', 'blue')
            ec.ecos_spread_chart(kor_exp, data_df)
        elif stat_ticker == '104Y014':
            ec.ecos_monthly_chart(kor_exp, data_df, data_ch)
            data_df.loc[:,'총수신(말잔)'] = data_df['예금은행 총수신(말잔)']+ data_df['비예금은행 총수신(말잔)']
            data_df.loc[:,'총대출(말잔)'] = data_df['예금은행 대출금(말잔)']+ data_df['비예금은행 대출금(말잔)']
            data_df.loc[:,'스프레드'] = data_df['총수신(말잔)']+ data_df['총대출(말잔)']
            sub_df = sub_df = data_df.iloc[:,4:]
            sub_ch = sub_df.pct_change()*100
            sub_ch = sub_ch.round(decimals=2)
            ec.ecos_monthly_chart(kor_exp, sub_df, sub_ch)
        elif stat_ticker == '121Y002':
            data_df = data_df.astype(float)
            data_ch = data_df.pct_change()*100
            data_ch = data_ch.round(decimals=2)
            ec.ecos_monthly_chart(kor_exp, data_df, data_ch) 
            data_df.loc[:,"여수신금리차"] = round(data_df.loc[:,'가계대출'] - data_df.loc[:,'저축성수신'],2)
            ec.ecos_spread_chart(kor_exp, data_df)
        else:
            data_df = data_df.astype(float)
            data_ch = data_df.pct_change()*100
            data_ch = data_ch.round(decimals=2)
            ec.ecos_monthly_chart(kor_exp, data_df, data_ch)           
    else:
        fred_df = fdr.DataReader(f'FRED:{stat_ticker}', start='2000')
        # st.dataframe(fred_df)
        ec.fred_monthly_chart(stat_ticker, kor_exp, fred_df)



if __name__ == "__main__":
    st.write(kor_time)
    data_load_state = st.text('Loading 통계정보 List...')
    source = st.sidebar.radio(
            label = "Choose the Source", 
            options=('Ecos', 'Fred'),
            index = 0,
            horizontal= True)
    
    eco_dict = {"물가":"901Y009", "장단기금리":"721Y001", "수출입금액":"402Y014","전체여수신":"104Y014","가계신용":"151Y005", "한국은행 기준금리":"722Y001", "은행 수신/대출 금리(신규)":"121Y002"}
    fred_dict = {"개인소비지출":"PCE"}

    data_load_state.text("Done! (using st.cache)")
    # st.dataframe(tickers)
    # st.dataframe(krx) 
    if source == 'Ecos':
        org_list = eco_dict.keys() #tickers
    else:
        org_list = fred_dict.keys()
    stat_name = st.sidebar.selectbox(
        '통계 목록', org_list)
    if source == 'Ecos':
        stat_ticker = eco_dict.get(stat_name)
    else:
        stat_ticker = fred_dict.get(stat_name)
    #st.dataframe(basic_df)
    submit = st.sidebar.button('Get Data')

    if submit:
        run(stat_ticker, stat_name)