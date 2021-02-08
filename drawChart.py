import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

import getData
import makeData

pd.set_option('display.float_format', '{:.2f}'.format)
now = datetime.now() +pd.DateOffset(days=-1)
today = '%s-%s-%s' % ( now.year, now.month, now.day)

## 특정 위치의 배경색 바꾸기
@st.cache
def draw_color_cell(x,color):
    color = f'background-color:{color}'
    return color
# PER 값 변경    
@st.cache
def change_per_value(x):
    if x >= 100 :
        x = 100
    elif x <= 0 :
        x = 0
    else:
        pass
    return x

def run():
    #Fundamental 데이터 가져오기
    # earning_q, earning_a = getData.get_fundamental_data_by_Json(input_ticker,"EARNINGS")
    # income_q, income_a = getData.get_fundamental_data_by_Json(input_ticker,"INCOME_STATEMENT")
    # balance_q, balance_a = getData.get_fundamental_data_by_Json(input_ticker,"BALANCE_SHEET")
    # cash_q, cash_a = getData.get_fundamental_data_by_Json(input_ticker,"CASH_FLOW")
    #Summary 데이터 가져오기    
    description_df, ratio_df, return_df, profit_df, dividend_df, volume_df, price_data, valuation_df = getData.get_overview(input_ticker)
    st.table(description_df)
    st.table(ratio_df)
    st.table(return_df)
    st.table(dividend_df)
    st.table(price_data)
    st.table(volume_df)
    st.table(valuation_df)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = valuation_df.at['RIM','Valuation'],
        delta = {'reference': valuation_df.at['Price','Valuation'], 'relative': True},
        title = {'text': "RIM-Price"},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    st.plotly_chart(fig)

    fig = go.Figure(go.Indicator(
        mode = "number+delta",
        value = valuation_df.at['Earnings Yield','Valuation'],
        title = {"text": "Earnings Yield<br><span style='font-size:0.8em;color:gray'>Demand Yield(15%)</span>"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        delta = {'reference': 15}))
    st.plotly_chart(fig)


if __name__ == "__main__":

    input_ticker = st.sidebar.text_input("ticker").upper()
    
    ticker_list = [ "SENEA", "IMKTA", "KBAL", "CMC", \
                    "APT","AMCX","BIIB", "BIG", "CI", "CPRX", "CHRS", "CSCO","CVS","DHT", "EURN", "HRB", "PRDO", \
                    "MO", "T", "O", "OMC", "SBUX", \
                    "MSFT", "MMM", "INVA", "SIGA", "WLKP", "VYGR", "KOF", "WSTG", "LFVN", "SUPN"]
    if input_ticker == "":
        input_ticker = st.sidebar.selectbox(
            'Ticker',ticker_list
        )
    
    input_ticker = input_ticker.upper()
    run()
    # submit = st.sidebar.button('Run app')
    # if submit:
    #     run()