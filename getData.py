import pandas as pd
import numpy as np
import time
from datetime import datetime
from alpha_vantage.fundamentaldata import FundamentalData 
import FinanceDataReader as fdr
import requests
import json
from pandas.io.json import json_normalize
import streamlit as st
import makeData

# key='XA7Y92OE6LDOTLLE'
key='CBALDIGECB3UFF5R'
fd = FundamentalData(key, output_format='pandas')
now = datetime.now() +pd.DateOffset(days=-5)
today = '%s-%s-%s' % ( now.year, now.month, now.day)

def get_close_data(ticker):
    close_price = fdr.DataReader(ticker, today)
    latest_price = close_price.iloc[-1,0]

    return latest_price

def get_annual_fundamental_data(ticker) :
    income_df, meta_data = fd.get_income_statement_annual(symbol=ticker)
    balance_df, meta_data = fd.get_balance_sheet_annual(symbol=ticker)
    cashflow_df, meta_data = fd.get_cash_flow_annual(symbol=ticker)
    #index 변경
    income_df.set_index('fiscalDateEnding', inplace=True)
    income_df.index =  pd.to_datetime(income_df.index, format='%Y-%m-%d')
    balance_df.set_index('fiscalDateEnding', inplace=True)
    balance_df.index =  pd.to_datetime(balance_df.index, format='%Y-%m-%d')
    cashflow_df.set_index('fiscalDateEnding', inplace=True)
    cashflow_df.index =  pd.to_datetime(cashflow_df.index, format='%Y-%m-%d')

    return income_df, balance_df, cashflow_df


def get_quarterly_fundamental_data(ticker):
    income_q, meta_data = fd.get_income_statement_quarterly(symbol=ticker)
    balance_q, meta_data = fd.get_balance_sheet_quarterly(symbol=ticker)
    cashflow_q, meta_data = fd.get_cash_flow_quarterly(symbol=ticker)
    #index 변경
    income_q.set_index('fiscalDateEnding', inplace=True)
    income_q.index =  pd.to_datetime(income_q.index, format='%Y-%m-%d')
    balance_q.set_index('fiscalDateEnding', inplace=True)
    balance_q.index =  pd.to_datetime(balance_q.index, format='%Y-%m-%d')
    cashflow_q.set_index('fiscalDateEnding', inplace=True)
    cashflow_q.index =  pd.to_datetime(cashflow_q.index, format='%Y-%m-%d')

    return income_q, balance_q, cashflow_q

def get_company_overview(ticker):
    overview_df, meta_data = fd.get_company_overview(symbol=ticker)
    overview_df = overview_df.T
    overview_df.columns = ['OverView']

    return overview_df

def get_fundamental_data_by_Json(ticker, func):
    API_URL = "https://www.alphavantage.co/query" 
    choice1 = "quarterlyReports" #annualReports : quarterlyReports 둘다 5년치 데이터
    choice2 = "annualReports"
    data = { 
        "function": func, 
        "symbol": ticker,
        "outputsize" : "compact",
        "datatype": "json", 
        "apikey": key} 
    response = requests.get(API_URL, data) 
    response_json = response.json() # maybe redundant
    df = pd.DataFrame()
    adf = pd.DataFrame()

    if func == 'TIME_SERIES_DAILY' :
        df = pd.DataFrame.from_dict(response_json['Time Series (Daily)'], orient= 'index')
        df.index =  pd.to_datetime(df.index, format='%Y-%m-%d')
        df = df.rename(columns={ '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'})
        df = df.astype({'Open': 'float64', 'High': 'float64', 'Low': 'float64','Close': 'float64','Volume': 'float64',})
        df = df[[ 'Open', 'High', 'Low', 'Close', 'Volume']]
    elif func == 'INCOME_STATEMENT':
        df = pd.DataFrame(response_json[choice1])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
        #annual
        adf = pd.DataFrame(response_json[choice2])
        adf = adf.iloc[::-1]
        adf.set_index('fiscalDateEnding', inplace=True)
        adf.index = pd.to_datetime(adf.index, format='%Y-%m-%d')
        # print(df)
    elif func == 'BALANCE_SHEET':
        df = pd.DataFrame(response_json[choice1])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
        #annual data
        adf = pd.DataFrame(response_json[choice2])
        adf = adf.iloc[::-1]
        adf.set_index('fiscalDateEnding', inplace=True)
        adf.index = pd.to_datetime(adf.index, format='%Y-%m-%d')
    elif func == 'CASH_FLOW':
        df = pd.DataFrame(response_json[choice1])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
        df["FCF"] = df['operatingCashflow'].astype(float) - df['capitalExpenditures'].astype(float)
         #annual data
        adf = pd.DataFrame(response_json[choice2])
        adf = adf.iloc[::-1]
        adf.set_index('fiscalDateEnding', inplace=True)
        adf.index = pd.to_datetime(adf.index, format='%Y-%m-%d')
        adf["FCF"] = adf['operatingCashflow'].astype(float) - adf['capitalExpenditures'].astype(float)
    elif func == 'EARNINGS':
        df = pd.DataFrame(response_json['quarterlyEarnings'])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df.index =  pd.to_datetime(df.index, format='%Y-%m-%d')
        df['ttmEPS'] = round(df['reportedEPS'].astype(float).rolling(4).sum(),2)
        df['reportedEPS'] = df['reportedEPS'].replace('None','0').astype(float).round(3)
        df['estimatedEPS'] = df['estimatedEPS'].replace('None','0').astype(float).round(4)
        df['surprise'] = df['surprise'].replace('None','0').astype(float).round(4)
        df['surprisePercentage'] = df['surprisePercentage'].replace('None','0').astype(float).round(2)
        #년간 데이터
        adf = pd.DataFrame(response_json['annualEarnings'])
        adf = adf.iloc[::-1]
        adf.set_index('fiscalDateEnding', inplace=True)
        adf.index =  pd.to_datetime(adf.index, format='%Y-%m-%d')
        adf['reportedEPS'] = adf['reportedEPS'].replace('None','0').astype(float).round(3)
        adf['EPS_YoY'] = round(adf['reportedEPS'].pct_change()*100,2)       

    return df, adf

def get_overview(ticker):
    API_URL = "https://www.alphavantage.co/query" 
    data = { 
        "function": "OVERVIEW", 
        "symbol": ticker,
        "outputsize" : "compact",
        "datatype": "json", 
        "apikey": key} 
    response = requests.get(API_URL, data) 
    response_json = response.json() # maybe redundant
    df = pd.DataFrame()

    df = pd.json_normalize(response_json)
    description_data = ['MarketCapitalization', 'Symbol', 'AssetType', 'Name', 'Description', 'Exchange', 'Currency', 'Country', 'Sector', \
                        'Industry', 'Address', 'FullTimeEmployees', 'FiscalYearEnd', 'LatestQuarter', 'LastSplitFactor', 'LastSplitDate']
    profit_data = ['RevenueTTM', 'RevenuePerShareTTM', 'ProfitMargin','GrossProfitTTM', 'OperatingMarginTTM', 'EBITDA', \
                    'QuarterlyEarningsGrowthYOY', 'QuarterlyRevenueGrowthYOY']
    dividend_data = ['DividendPerShare', 'DividendYield', 'PayoutRatio', \
                        'ForwardAnnualDividendRate', 'ForwardAnnualDividendYield', 'DividendDate', 'ExDividendDate']
    ratio_data = ['EPS','DilutedEPSTTM', 'PERatio', 'TrailingPE', 'ForwardPE', \
                    'BookValue', 'PriceToBookRatio','PEGRatio', 'EVToRevenue', 'EVToEBITDA','PriceToSalesRatioTTM']
    return_data = ['ReturnOnEquityTTM', 'ReturnOnAssetsTTM']
    price_data = ['Beta', '52WeekHigh', '52WeekLow', '50DayMovingAverage', '200DayMovingAverage']
    volume_data = ['SharesOutstanding', 'SharesFloat', 'SharesShort', 'SharesShortPriorMonth', 'ShortRatio', 'ShortPercentOutstanding', \
                    'ShortPercentFloat', 'PercentInsiders', 'PercentInstitutions']
    valuation_data = ['AnalystTargetPrice']

    description_df = df[description_data].T
    description_df.columns = ['Description']
    change_cap = format(round(float(description_df.loc['MarketCapitalization','Description']) / 1000000,2),',')
    description_df.loc['MarketCapitalization'] = str(change_cap) + "M"
    ratio_df = df[ratio_data].T
    ratio_df.columns = ['Ratio']
    #PERR, PBRR 추가 해보자
    ratio_df.loc['PERR'] = round(float(df.loc[0, 'TrailingPE'])/(float(df.loc[0, 'ReturnOnEquityTTM'])*100),2)
    ratio_df.loc['PBRR'] = round(float(df.loc[0, 'PriceToBookRatio'])/(float(df.loc[0, 'ReturnOnEquityTTM'])*100/10),2)
    return_df = df[return_data].T.astype(float)*100
    return_df = return_df.round(2).astype(str) + "%"
    return_df.columns = ['Return']
    profit_df = df[profit_data].T
    profit_df.columns = ['Profitability']
    dividend_df = df[dividend_data].T
    dividend_df.columns = ['Dividend']
    volume_df = df[volume_data].T
    volume_df.columns = ['Volume']
    price_df = df[price_data].T
    price_df.columns = ['Price']

    #최근 종목 close 값
    last_price = get_close_data(ticker)
    df['Price'] = last_price
    valuation_df = makeData.valuation(df.T, ticker)
    
    return description_df, ratio_df, return_df, profit_df, dividend_df, volume_df, price_df, valuation_df