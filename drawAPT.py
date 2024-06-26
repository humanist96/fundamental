from datetime import datetime

import numpy as np
import pandas as pd

from pandas.io.json import json_normalize

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import streamlit as st
import FinanceDataReader as fdr

#choroplethViz
import mapboxgl
from mapboxgl.viz import *
from mapboxgl.utils import create_color_stops
from mapboxgl.utils import create_numeric_stops

pd.set_option('display.float_format', '{:.2f}'.format)
# 챠트 기본 설정 
# marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473'] #'rgb(255,69,0)'
marker_colors = ['rgb(244,201,107)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(27,38,81)', 'rgb(153,204,0)', \
                       'rgb(153,51,102)', 'rgb(255,0,0)', 'rgb(0,255,0)', 'rgb(0,0,255)', 'rgb(255,204,0)', \
                        'rgb(255,0,255)', 'rgb(0,255,255)', 'rgb(128,0,0)', 'rgb(0,128,0)', 'rgb(0,0,128)', \
                         'rgb(128,128,0)', 'rgb(128,0,128)', 'rgb(0,128,128)', 'rgb(192,192,192)', 'rgb(153,153,255)', \
                             'rgb(255,255,0)', 'rgb(255,255,204)', 'rgb(102,0,102)', 'rgb(255,128,128)', 'rgb(0,102,204)',\
                                 'rgb(255,102,0)', 'rgb(51,51,51)', 'rgb(51,153,102)', 'rgb(51,153,102', 'rgb(204,153,255)']
template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
pio.templates["myID"] = go.layout.Template(
    layout_annotations=[
        dict(
            name="draft watermark",
            text="Graph by Kevin",
            textangle=0,
            opacity=0.5,
            font=dict(color="red", size=20),
            xref="paper",
            yref="paper",
            x=0.9,
            y=-0.2,
            showarrow=False,
        )
    ]
)


def run_pop_index(selected_city2, df, df_change, sdf, sdf_change, not_sell_df):
    last_month = pd.to_datetime(str(df.index.values[-1])).strftime('%Y.%m')

    titles = dict(text= '['+selected_city2 +'] 세대수 증감', x=0.5, y = 0.9) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(mode='lines', name = '인구수', x =  df.index, y= df[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name = '세대수', x =  sdf.index, y= sdf[selected_city2], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Bar(name = '세대수 증감', x = sdf_change.index, y = sdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[3]), secondary_y = True)
    fig.add_trace(go.Bar(name = '인구수 증감', x = df_change.index, y = df_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    # fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='인구세대수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='증감', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="%") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    # fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)


    with st.beta_expander("See explanation"):
            st.markdown(f'인구-세대수 최종업데이트: **{last_month}월**')
            st.write(f"인구수 Source : https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1B040A3 ")
            st.write(f"세대수 Source : https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1B040B3 ")

    #미분양 그래프
    titles = dict(text= ' ('+ selected_city2 + ') 준공 후 미분양', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = '60~85㎡', x =  not_sell_df.index, y= not_sell_df[(selected_city2, '60~85㎡')], marker_color = marker_colors[1]), secondary_y = True)
    fig.add_trace(go.Bar(name ='85㎡초과', x =  not_sell_df.index, y= not_sell_df[(selected_city2, '85㎡초과')], marker_color = marker_colors[2]), secondary_y = True)                                             
    fig.add_trace(go.Bar(name ='60㎡이하', x =  not_sell_df.index, y= not_sell_df[(selected_city2, '60㎡이하')], marker_color = marker_colors[4]), secondary_y = True)
    fig.add_trace(go.Scatter(mode='lines', name ='전체', x =  not_sell_df.index, y= not_sell_df[(selected_city2, '소계')], marker_color = marker_colors[0]), secondary_y = False)
    # fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(title_text='호', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = True)
    fig.update_yaxes(title_text='소계', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    # fig.add_hline(y=100.0, line_color="pink", annotation_text="100>매수자많음", annotation_position="bottom right")
    st.plotly_chart(fig)


def run_price_index(selected_city2, mdf,jdf, mdf_change, jdf_change, bubble_df2, m_power) :
    kb_last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
   
    titles = dict(text= '('+selected_city2 +') 월간 매매-전세 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)

    
    fig.add_trace(go.Scatter(mode='lines', name = '매매지수', x =  mdf.index, y= mdf[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='전세지수', x =  jdf.index, y= jdf[selected_city2], marker_color = marker_colors[3]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='지수 증감', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="%") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                    dict(count=10,
                        label="10y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
            )      
        )
    st.plotly_chart(fig)

    #bubble index chart
    titles = dict(text= '('+selected_city2 +') 월간 버블 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    # fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    # fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)

    
    fig.add_trace(go.Scatter(mode='lines', name = '버블지수', x =  bubble_df2.index, y= bubble_df2[selected_city2], marker_color = marker_colors[3]), secondary_y = True)
    fig.add_trace(go.Scatter(mode='lines', name ='전세파워', x =  m_power.index, y= m_power[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='전세파워', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='blue',  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='버블지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='red', secondary_y = True) #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    st.plotly_chart(fig)
    with st.beta_expander("See explanation"):
            st.markdown(f'매매-전세 지수 최종업데이트: **{kb_last_month}월**')
            st.write(f"Source : https://onland.kbstar.com/quics?page=C060737 ")

    #box chart
    fig2 = go.Figure()
    title = '('  + selected_city2 + ') Index Change Statistics'
    titles = dict(text= title, x=0.5, y = 0.9) 
    fig2.add_trace(go.Box(x=mdf_change.loc[:,selected_city2], name='Index Change', boxpoints='all', marker_color = 'indianred',
                    boxmean='sd', jitter=0.3, pointpos=-1.8 ))
    fig2.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    # fig2.add_trace(go.Box(x=earning_df.loc[:,'EPS Change'], name='EPS Change'))
    st.plotly_chart(fig2)

def run_sentimental_index():
    # st.dataframe(senti_df)
     # 챠트 기본 설정 
    # marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,255,255)', 'rgb(237,234,255)']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    titles = dict(text= ' 매수매도 우위 지수('+ selected_dosi + ')', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '매도자 많음', x =  js_1.index, y= js_1[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='매수자 많음', x =  js_2.index, y= js_2[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.add_hline(y=100.0, line_color="pink", annotation_text="100>매수자많음", annotation_position="bottom right")
    fig.add_vrect(x0="2017-08-07", x1="2017-08-14", 
              annotation_text="8.2 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2018-09-17", x1="2018-10-01", 
              annotation_text="9.13 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2019-12-16", x1="2020-02-24", 
              annotation_text="12.16/2.24 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-06-22", x1="2020-07-13", 
              annotation_text="6.17/7.10 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-08-10", x1="2020-08-17", 
              annotation_text="8.4 대책", annotation_position="bottom left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                    dict(count=10,
                        label="10y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
            )      
        )
    st.plotly_chart(fig)

def draw_basic(last_df,df, geo_data, last_pop, power_df):

    #마지막 달
    # last_month = pd.to_datetime(str(selected_df.index.values[-1])).strftime('%Y.%m')

    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,255,255)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
    # 월간 인구수 세대수 증감
    title = dict(text='주요 시-구 월간 인구수-세대수 증감', x=0.5, y = 0.9) 
    fig1 = px.scatter(last_pop, x='인구증감', y='세대증감', color='세대증감', size=abs(last_pop['세대증감']), 
                        text= last_pop.index, hover_name=last_pop.index, color_continuous_scale='Bluered')
    fig1.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template="seaborn")
    fig1.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig1.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    st.plotly_chart(fig1)

    #버블지수/전세파워 table 추가
    title = dict(text='주요 시-구 월간 전세파워-버블지수 합산 순위', x=0.5, y = 0.9) 
    fig = go.Figure(data=[go.Table(
                        header=dict(values=['<b>지역</b>','<b>전세파워</b>', '<b>버블지수</b>', '<b>전세파워 rank</b>', \
                                            '<b>버블지수 rank</b>', '<b>전세+버블 score</b>', '<b>전체 rank</b>'],
                                    fill_color='royalblue',
                                    align=['right','left', 'left', 'left', 'left', 'left', 'left'],
                                    font=dict(color='white', size=12),
                                    height=40),
                        cells=dict(values=[power_df.index, power_df['전세파워'], power_df['버블지수'], power_df['jrank'], \
                                            power_df['brank'], power_df['score'], power_df['rank']], 
                                    fill=dict(color=['paleturquoise', 'white', 'white','white', 'white', 'white', 'white']),
                                    align=['right','left', 'left', 'left', 'left', 'left', 'left'],
                                    font_size=12,
                                    height=30))
                    ])
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template="seaborn")
    st.plotly_chart(fig)

    #choroplethmapbax
    token = 'pk.eyJ1Ijoic2l6aXB1c3gyIiwiYSI6ImNrbzExaHVvejA2YjMyb2xid3gzNmxxYmoifQ.oDEe7h9GxzzUUc3CdSXcoA'

    df = pd.merge(df, last_pop, how='inner', left_index=True, right_index=True)

    for col in df.columns:
        df[col] = df[col].astype(str)
    # for col in last_pop.columns:
    #     last_pop[col] = last_pop[col].astype(str)

    df['text'] = '<b>' + df.index + '</b> <br>' + \
                    '매매증감:' + df['매매증감'] + '<br>' + \
                    '전세증감:' + df['전세증감'] + '<br>' + \
                    '인구증감:' + df['인구증감'] + '<br>' + \
                    '세대증감:' + df['세대증감']
    titles = dict(text='주요 시-구 주간 전세지수 증감',  x=0.5, y = 0.95) 
    fig = go.Figure(go.Choroplethmapbox(geojson=geo_data, locations=df['SIG_CD'], z=df['전세증감'].astype(float),
                                        colorscale="Reds", zmin=df['전세증감'].astype(float).min(), zmax=df['전세증감'].astype(float).max(), marker_line_width=0))
    fig.update_traces(autocolorscale=False,
                        text=df['text'], # hover text
                        marker_line_color='white', # line markers between states
                        colorbar_title="전세증감")
    # fig.update_traces(hovertext=df['index'])
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token,
                    mapbox_zoom=6, mapbox_center = {"lat": 37.414, "lon": 127.177})
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)

    titles = dict(text='주요 시-구 월간 매매지수 증감',  x=0.5, y = 0.9) 
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
    fig = px.bar(last_df, x= last_df.index, y=last_df.iloc[:,0], color=last_df.iloc[:,0], color_continuous_scale='Bluered', \
                text=last_df.index)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_traces(texttemplate='%{label}', textposition='outside')
    fig.update_layout(uniformtext_minsize=6, uniformtext_mode='show')
    fig.update_yaxes(title_text='월간 매매지수 증감률', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.add_hline(y=last_df.iloc[0,0].astype(float), line_dash="dash", line_color="red", annotation_text=f"전국 증감률: {round(last_df.iloc[0,0],2)}", \
                annotation_position="bottom right")
    st.plotly_chart(fig)
    # st.dataframe(last_df.T.style.highlight_max(axis=1))

    with st.beta_container():
        #매매/전세 증감률 Bubble Chart
        title = dict(text='주요 시-구 월간 매매/전세지수 증감', x=0.5, y = 0.9) 
        fig1 = px.scatter(last_df, x='매매증감', y='전세증감', color='매매증감', size=abs(last_df['전세증감']), 
                            text= last_df.index, hover_name=last_df.index, color_continuous_scale='Bluered')
        fig1.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
        fig1.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
        fig1.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
        st.plotly_chart(fig1)

def draw_pir(selected_city2, pir_df, income_df, price_df):
    titles = dict(text= '('+selected_city2 +') 분기 PIR 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(mode='lines', name = 'PIR', x =  pir_df.index, y= pir_df[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Bar(name = '가구소득', x = income_df.index, y = income_df[selected_city2], marker_color=  marker_colors[2], opacity=0.3), secondary_y = True)
    fig.add_trace(go.Bar(name = '주택가격', x = price_df.index, y = price_df[selected_city2], marker_color=  marker_colors[1], opacity=0.3), secondary_y = True)
    fig.update_layout(barmode='stack')
    
    # fig.add_trace(go.Scatter(mode='lines', name ='전세지수', x =  jdf.index, y= jdf[selected_city2], marker_color = marker_colors[3]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='PIR', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='가구소득-주택가격', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="만원") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

def draw_hai(city, hai_df, info_df):
    titles = dict(text= '('+city +') 분기 HAI 지수', x=0.5, y = 0.9) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(mode='lines', name = 'HAI', x =  hai_df.index, y= hai_df[city], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Bar(name = '전국중위월소득', x = info_df.index, y = info_df['중위월소득'], marker_color=  marker_colors[2], opacity=0.3), secondary_y = True)
    fig.add_trace(go.Scatter(x=[hai_df.index[-2]], y=[99.0], text=["100>무리없이구입가능"], mode="text"))
    fig.add_shape(type="line", x0=hai_df.index[0], y0=100.0, x1=hai_df.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    # fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='HAI', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='전국중위월소득', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="만원") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)
    
    titles = dict(text= '월별 주담대 금리', x=0.5, y = 0.9) 
    fig = go.Figure([go.Bar(x=info_df.index, y=info_df['주담대금리'])])
    # fig = px.bar(info_df, x=info_df.index, y="주담대금리")
    fig.add_hline(y=info_df['주담대금리'].mean(axis=0))
    fig.update_yaxes(title_text='금리', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', ticksuffix="%") #tickprefix="$", 
    st.plotly_chart(fig)

def draw_sentimental_index(selected_dosi, senti_dfs, df_as, df_bs, mdf_change):
    #매수우위지수
    js_index = senti_dfs[0].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_1 = df_as[0].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_2 = df_bs[0].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)

    titles = dict(text= '[<b>'+ selected_dosi + '</b>] 매수우위지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '매도자 많음', x =  js_1.index, y= js_1[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='매수자 많음', x =  js_2.index, y= js_2[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(x=[js_index.index[-2]], y=[99.0], text=["매수자많음>100"], mode="text"))
    fig.add_shape(type="line", x0=js_index.index[0], y0=100.0, x1=js_index.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.add_vrect(x0="2017-08-07", x1="2017-08-14", 
              annotation_text="8.2 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2018-09-17", x1="2018-10-01", 
              annotation_text="9.13 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2019-12-16", x1="2020-02-24", 
              annotation_text="12.16/2.24 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-06-22", x1="2020-07-13", 
              annotation_text="6.17/7.10 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-08-10", x1="2020-08-17", 
              annotation_text="8.4 대책", annotation_position="bottom left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2021-02-15", x1="2021-02-22", 
              annotation_text="8.4 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1),
            xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                    dict(count=10,
                        label="10y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True), type="date")      
    )
    st.plotly_chart(fig)

    #매수우위와 매매증감 
    x_data = mdf_change.index
    title = "[<b>"+selected_dosi+"</b>] 매수우위지수와 매매증감"
    titles = dict(text= title,  x=0.5, y = 0.9) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "매매증감", x = x_data, y =mdf_change[selected_dosi], 
                        text = mdf_change[selected_dosi], textposition = 'outside', 
                        marker_color= marker_colors[0]), secondary_y = True) 
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_hline(y=100.0, line_width=1, line_color="red", secondary_y = False)
    fig.add_hline(y=mdf_change[selected_dosi].mean(), line_width=2, line_dash="dot", line_color="blue",  annotation_text="평균상승률: "+str(round(mdf_change[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
    fig.update_yaxes(title_text="매수우위지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="매매증감", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1, xanchor="right",  x=0.95))
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

    #매매거래지수
    js_sell = senti_dfs[1].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_3 = df_as[1].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_4 = df_bs[1].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') 매매거래지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '활발함', x =  js_3.index, y= js_3[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='한산함', x =  js_4.index, y= js_4[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매매거래지수', x =  js_sell.index, y= js_sell[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(x=[js_sell.index[-2]], y=[99.0], text=["활발함>100"], mode="text"))
    fig.add_shape(type="line", x0=js_sell.index[0], y0=100.0, x1=js_sell.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.add_vrect(x0="2017-08-07", x1="2017-08-14", 
              annotation_text="8.2 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2018-09-17", x1="2018-10-01", 
              annotation_text="9.13 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2019-12-16", x1="2020-02-24", 
              annotation_text="12.16/2.24 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-06-22", x1="2020-07-13", 
              annotation_text="6.17/7.10 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-08-10", x1="2020-08-17", 
              annotation_text="8.4 대책", annotation_position="bottom left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2021-02-15", x1="2021-02-22", 
              annotation_text="8.4 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    st.plotly_chart(fig)

    #전세수급
    js_j = senti_dfs[2].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_5 = df_as[2].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_6 = df_bs[2].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') 전세수급지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '수요>공급', x =  js_5.index, y= js_5[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='수요<공급', x =  js_6.index, y= js_6[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='전세수급지수', x =  js_j.index, y= js_j[selected_dosi].round(2), marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(x=[js_j.index[-2]], y=[99.0], text=["공급부족>100"], mode="text"))
    fig.add_shape(type="line", x0=js_j.index[0], y0=100.0, x1=js_j.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.add_vrect(x0="2017-08-07", x1="2017-08-14", 
              annotation_text="8.2 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2018-09-17", x1="2018-10-01", 
              annotation_text="9.13 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2019-12-16", x1="2020-02-24", 
              annotation_text="12.16/2.24 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-06-22", x1="2020-07-13", 
              annotation_text="6.17/7.10 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-08-10", x1="2020-08-17", 
              annotation_text="8.4 대책", annotation_position="bottom left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2021-02-15", x1="2021-02-22", 
              annotation_text="8.4 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    st.plotly_chart(fig)

    #전세거래
    js_js = senti_dfs[3].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_7 = df_as[3].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_8 = df_bs[3].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') 전세거래지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '활발함', x =  js_7.index, y= js_7[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='한산함', x =  js_8.index, y= js_8[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='전세거래지수', x =  js_js.index, y= js_js[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(x=[js_js.index[-2]], y=[99.0], text=["활발함>100"], mode="text"))
    fig.add_shape(type="line", x0=js_js.index[0], y0=100.0, x1=js_js.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.add_vrect(x0="2017-08-07", x1="2017-08-14", 
              annotation_text="8.2 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2018-09-17", x1="2018-10-01", 
              annotation_text="9.13 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2019-12-16", x1="2020-02-24", 
              annotation_text="12.16/2.24 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-06-22", x1="2020-07-13", 
              annotation_text="6.17/7.10 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-08-10", x1="2020-08-17", 
              annotation_text="8.4 대책", annotation_position="bottom left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2021-02-15", x1="2021-02-22", 
              annotation_text="8.4 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    st.plotly_chart(fig)

    #KB부동산 매매가격 전망지수
    js_for = senti_dfs[4].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_9 = df_as[4].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_10 = df_bs[4].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') KB부동산 매매가격 전망지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '약간상승', x =  js_9.index, y= js_9[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='약간하락', x =  js_10.index, y= js_10[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매매가격 전망지수', x =  js_for.index, y= js_for[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(x=[js_for.index[-2]], y=[99.0], text=["상승비중높음>100"], mode="text"))
    fig.add_shape(type="line", x0=js_for.index[0], y0=100.0, x1=js_for.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.add_vrect(x0="2017-08-07", x1="2017-08-14", 
              annotation_text="8.2 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2018-09-17", x1="2018-10-01", 
              annotation_text="9.13 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2019-12-16", x1="2020-02-24", 
              annotation_text="12.16/2.24 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-06-22", x1="2020-07-13", 
              annotation_text="6.17/7.10 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-08-10", x1="2020-08-17", 
              annotation_text="8.4 대책", annotation_position="bottom left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2021-02-15", x1="2021-02-22", 
              annotation_text="8.4 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    st.plotly_chart(fig)

    #KB부동산 전세가격 전망지수
    js_for_j = senti_dfs[5].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_11 = df_as[5].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_12 = df_bs[5].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') KB부동산 전세가격 전망지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '약간상승', x =  js_11.index, y= js_11[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='약간하락', x =  js_12.index, y= js_12[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='전세가격 전망지수', x =  js_for_j.index, y= js_for_j[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(x=[js_for_j.index[-2]], y=[99.0], text=["상승비중높음>100"], mode="text"))
    fig.add_shape(type="line", x0=js_for_j.index[0], y0=100.0, x1=js_for_j.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.add_vrect(x0="2017-08-07", x1="2017-08-14", 
              annotation_text="8.2 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2018-09-17", x1="2018-10-01", 
              annotation_text="9.13 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2019-12-16", x1="2020-02-24", 
              annotation_text="12.16/2.24 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-06-22", x1="2020-07-13", 
              annotation_text="6.17/7.10 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-08-10", x1="2020-08-17", 
              annotation_text="8.4 대책", annotation_position="bottom left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2021-02-15", x1="2021-02-22", 
              annotation_text="8.4 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    st.plotly_chart(fig)

def run_buy_basic(b_df, org_df):
    df_total = b_df.xs('합계',axis=1, level=1)
    df_si = b_df.xs('관할시군구내',axis=1, level=1)
    df_do = b_df.xs('관할시도내',axis=1, level=1)
    df_seoul = b_df.xs('관할시도외_서울',axis=1, level=1)
    df_etc = b_df.xs('관할시도외_기타',axis=1, level=1)
    ## q증감률
    df_total_ch = df_total.pct_change()
    df_total_yoy = df_total.pct_change(12)

    df_si_ch = df_si.pct_change()
    df_si_yoy = df_si.pct_change(12)

    df_do_ch = df_do.pct_change()
    df_do_yoy = df_do.pct_change(12)

    df_seoul_ch = df_seoul.pct_change()
    df_seoul_yoy = df_seoul.pct_change(12)

    df_etc_ch = df_etc.pct_change()
    df_etc_yoy = df_etc.pct_change(12)

    ### 증감량
    df_total_amt = df_total - df_total.shift(1)
    df_si_amt = df_si - df_si.shift(1)
    df_do_amt = df_do - df_do.shift(1)
    df_seoul_amt = df_seoul - df_seoul.shift(1)
    df_etc_amt = df_etc - df_etc.shift(1)

    #투자자 합산
    df_outer = df_seoul.add(df_etc)
    df_outer_amt = df_outer.sub(df_outer.shift(1))
    df_outer_ch = df_outer.pct_change()
    df_outer_yoy = df_outer.pct_change(12)

    #dropping NaN,  infinite values 
    df_outer_ch.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_outer_ch.fillna(0,inplace=True)
    df_outer_yoy.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_outer_yoy.fillna(0,inplace=True)

    #mom, yoy 투자자 변화
    change_df = df_outer_ch.iloc[-1].T.to_frame()
    change_df['YoY'] = df_outer_yoy.iloc[-1].T.to_frame()
    change_df.columns = ['MoM', 'YoY']
    #평균이 10이하인 지역은 제외하자
    change_df['mean'] = df_outer.mean()
    change_df2 = round(change_df[change_df['mean'] > 10],1)

    #한달간 투자자 변동 순위
    last_df = df_seoul.iloc[-1].T.to_frame()
    last_df['기타지역'] = df_etc.iloc[-1].T.to_frame()
    last_df.columns = ['서울매수자', '기타지역매수자']
    last_df = last_df.astype(int)
    last_df['투자자'] = last_df['서울매수자'].add(last_df['기타지역매수자'])

     #챠트 기본 설정
    # colors 
    marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
    # marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
    #마지막 달
    last_month = pd.to_datetime(str(df_outer.index.values[-1])).strftime('%Y.%m')

    # box plot
    # fig = px.box(df_outer,y=df_outer.columns, notched=True, title= "각 지역 통계(2006.1월~" + last_month +"월)")
    # st.plotly_chart(fig)

    #최근 한달 동안 투자자 수가 가장 많이 유입된 곳 보기
    title = last_month + '월 <b>최근 한달 동안 투자자가 가장 많이 유입된 곳</b>'
    titles = dict(text= title, x=0.5, y = 0.9) 
    fig = px.bar(last_df, x= last_df.index, y= last_df.iloc[:,-1], color=last_df.iloc[:,-1], color_continuous_scale='Bluered', text=last_df.index)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_traces(texttemplate='%{label}', textposition='outside')
    fig.update_layout(uniformtext_minsize=6, uniformtext_mode='show', xaxis_tickformat = '%Y-%m')
    fig.update_yaxes(title_text='서울+기타지역 투자자 수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="명")
    # fig.add_hline(y=last_df.iloc[0,0], line_dash="dash", line_color="red", annotation_text=f"전국 증감률: {round(last_df.iloc[0,0],2)}", \
    #             annotation_position="bottom right")
    st.plotly_chart(fig)


    title = last_month +"월 <b>서울 - 기타지역 거주자 매수</b>"
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = px.scatter(last_df, x='서울매수자', y='기타지역매수자', color='기타지역매수자', color_continuous_scale='Bluered', size=last_df['서울매수자'], 
                        text= last_df.index, hover_name=last_df.index)
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickformat = '%Y-%m')
    fig.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="명")
    fig.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="명")
    st.plotly_chart(fig)

    #매매/전세 증감률 Bubble Chart
    title = last_month +"월 기준<b> 투자자 MoM-YoY 증감률</b>"
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = px.scatter(change_df2, x='MoM', y='YoY', color='MoM', size='mean', 
                        text= change_df2.index, hover_name=change_df2.index)
    fig.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickformat = '%Y-%m')
    st.plotly_chart(fig)


def run_buy_index(selected_dosi, org_df, mdf):
    buy_last_month = pd.to_datetime(str(org_df.index.values[-1])).strftime('%Y.%m')
    if selected_dosi == "제주서귀포":
        selected_dosi ="제주" 
    selected_df = org_df.xs(selected_dosi, axis=1, level=0)
    #마지막 달
    last_month = pd.to_datetime(str(selected_df.index.values[-1])).strftime('%Y.%m')
    #make %
    per_df = round(selected_df.div(selected_df['합계'], axis=0)*100,1)
    title = last_month + "월까지 ["+selected_dosi+"] 매입자별 전체 거래량"
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = px.bar(selected_df, x=selected_df.index, y=["관할시군구내", "관할시도내", "관할시도외_서울", "관할시도외_기타"])
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickformat = '%Y-%m')
    st.plotly_chart(fig)

    title = last_month + "월까지 ["+selected_dosi+"] 매입자별 비중"
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = px.bar(per_df, x=per_df.index, y=["관할시군구내", "관할시도내", "관할시도외_서울", "관할시도외_기타"])
    fig.update_yaxes(title= "매입자별 비중", zeroline=False, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickformat = '%Y-%m')
    st.plotly_chart(fig)

#감정원 주간 지수와 거래량 같이 그려보자. 2021-8-3 추가 444
     # colors 
    marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
    # marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
    if selected_dosi == "제주":
        selected_dosi ="제주서귀포"
    x_data = selected_df.index
    title = "["+selected_dosi+"] <b>KB 매매지수와 거래량</b>"
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "매매거래량", x = x_data, y =selected_df['합계'], 
                        text = selected_df['합계'], textposition = 'outside', 
                        marker_color= marker_colors[0]), secondary_y = False) 
    fig.add_trace(go.Scatter(mode='lines', 
                                    name = "매매지수", x =  mdf.index, y=mdf[selected_dosi],  
                                    text= mdf[selected_dosi], textposition = 'top center', marker_color = marker_colors[2]),
                                    secondary_y = True)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_hline(y=selected_df['합계'].mean(axis=0))
    fig.update_yaxes(title_text="매매 거래량", showticklabels= True, showgrid = True, zeroline=True, ticksuffix="건", secondary_y = False)
    fig.update_yaxes(title_text="매매지수", showticklabels= True, showgrid = False, zeroline=True, secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

    


def run_ratio_index(selected_dosi, sadf, sadf_ch, jadf, jadf_ch, jratio_df):

    marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
    # marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"

    x_data = sadf_ch.index
    title = "[<b>"+selected_dosi+"</b>] KB 평균 매매 평단가 변화"
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "평단가증감", x = x_data, y =sadf_ch[selected_dosi], 
                        text = sadf_ch[selected_dosi], textposition = 'outside', 
                        marker_color= marker_colors[0]), secondary_y = True) 
    fig.add_trace(go.Scatter(mode='lines', 
                                    name = "평단가", x =  sadf.index, y=sadf[selected_dosi],  
                                    text= sadf[selected_dosi], textposition = 'top center', marker_color = marker_colors[2]),
                                    secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_hline(y=sadf_ch[selected_dosi].mean(), line_width=2, line_dash="solid", line_color="blue",  annotation_text="평균상승률: "+str(round(sadf_ch[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
    fig.update_yaxes(title_text="평단가", showticklabels= True, showgrid = True, zeroline=True, ticksuffix="만원", secondary_y = False)
    fig.update_yaxes(title_text="평단가 증감%", showticklabels= True, showgrid = False, zeroline=True, secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

    x_data = jadf_ch.index
    title = "[<b>"+selected_dosi+"</b>] KB 평균 전세 평단가 변화"
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "평단가증감", x = x_data, y =jadf_ch[selected_dosi], 
                        text = jadf_ch[selected_dosi], textposition = 'outside', 
                        marker_color= marker_colors[0]), secondary_y = True) 
    fig.add_trace(go.Scatter(mode='lines', 
                                    name = "평단가", x =  jadf.index, y=jadf[selected_dosi],  
                                    text= jadf[selected_dosi], textposition = 'top center', marker_color = marker_colors[2]),
                                    secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_hline(y=jadf_ch[selected_dosi].mean(), line_width=2, line_dash="solid", line_color="blue",  annotation_text="평균상승률: "+str(round(jadf_ch[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
    fig.update_yaxes(title_text="평단가", showticklabels= True, showgrid = True, zeroline=True, ticksuffix="만원", secondary_y = False)
    fig.update_yaxes(title_text="평단가 증감%", showticklabels= True, showgrid = False, zeroline=True, secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

    title = "["+selected_dosi+"] KB 평균 가격 전세가율"
    if selected_dosi == "제주서귀포":
        selected_dosi ="제주" 
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = make_subplots(specs=[[{'secondary_y': False}]]) 
    # fig = px.line(jratio_df, x=jratio_df.index, y=selected_dosi)
    fig.add_trace(go.Scatter(mode='lines', 
                                    name = "전세가율", x =  jratio_df.index, y=jratio_df[selected_dosi],  
                                    text= jratio_df[selected_dosi], textposition = 'top center', marker_color = marker_colors[2]),
                                    secondary_y = False)
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide', template=template)
    fig.update_yaxes(title_text='전세가율', showticklabels= True, showgrid = True, ticksuffix="%")
    fig.add_hline(y=70.0, line_color="pink", annotation_text="70%", annotation_position="bottom right")
    st.plotly_chart(fig)

def run_local_analysis(mdf, mdf_change, selected_dosi, selected_dosi2, selected_dosi3, small_list):
    # 챠트 기본 설정 
    # marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(153,204,0)', \
                       'rgb(153,51,102)', 'rgb(255,0,0)', 'rgb(0,255,0)', 'rgb(0,0,255)', 'rgb(255,204,0)', \
                        'rgb(255,0,255)', 'rgb(0,255,255)', 'rgb(128,0,0)', 'rgb(0,128,0)', 'rgb(0,0,128)', \
                         'rgb(128,128,0)', 'rgb(128,0,128)', 'rgb(0,128,128)', 'rgb(192,192,192)', 'rgb(153,153,255)', \
                             'rgb(255,255,0)', 'rgb(255,255,204)', 'rgb(102,0,102)', 'rgb(255,128,128)', 'rgb(0,102,204)',\
                                 'rgb(255,102,0)', 'rgb(51,51,51)', 'rgb(51,153,102)', 'rgb(51,153,102', 'rgb(204,153,255)']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    #같이 그려보자
    do_list = ['강원', '충북', '충남', '전북', '전남', '경남', '경북', '제주서귀포']
    gu_city = ['부산', '대구', '인천', '광주', '대전', '울산', '수원', '성남', '안양', '용인', '고양', '안산', \
                 '천안', '청주', '전주', '포항', '창원']
    # gu_city_series = pd.Series(gu_city)
    column_list = mdf.columns.to_list()
    city_series = pd.Series(column_list)
    draw_list = []
    if selected_dosi in gu_city:
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()
        # draw_list = [selected_dosi]
    elif selected_dosi == '전국':
        draw_list = ['전국', '수도권', '기타지방']
    elif selected_dosi == '서울':
        draw_list = ['서울 강북', '서울 강남']
    elif selected_dosi == '수도권':
        draw_list = ['서울', '경기', '인천']
    elif selected_dosi == '6개광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산', '인천']
    elif selected_dosi == '5개광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산']
    elif selected_dosi == '경기':
        draw_list = ['경기', '수원', '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', \
             '용인', '시흥', '군포', '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기광주', '화성']
    elif selected_dosi in do_list:
        draw_list = small_list
    
    if selected_dosi3 in draw_list:
        draw_list = city_series[city_series.str.contains(selected_dosi3)].to_list()
    if selected_dosi3 in gu_city:
        draw_list = city_series[city_series.str.contains(selected_dosi3)].to_list()

    kb_last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
   
    title = "<b>KB 매매지수 변화 같이 보기</b>"
    titles = dict(text= title, x=0.5, y = 0.85) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Bar(x=mdf_change.index, y=mdf_change.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=True,
            )
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Scatter(x=mdf.index, y=mdf.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=False,
            )
    fig.update_yaxes(title_text="매매지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="매매지수 변화", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                    dict(count=10,
                        label="10y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
            )      
        )
    st.plotly_chart(fig)

def run_local_price(peong_df, peong_ch, peongj_df, peongj_ch, ratio_df, selected_dosi, selected_dosi2, selected_dosi3, small_list):
    #마지막 데이터만
    last_df = peong_df.iloc[-1].T.to_frame()
    last_df['평균전세가'] = peongj_df.iloc[-1].T.to_frame()
    last_df.columns = ['평균매매가', '평균전세가']
    last_df.dropna(inplace=True)
    last_df = last_df.round(decimals=2)
    #같이 그려보자
    gu_city = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '수원', '성남', '안양', '용인', '고양', '안산', \
                 '천안', '청주', '전주', '포항', '창원']
    do_list = ['강원', '충북', '충남', '전북', '전남', '경남', '경북', '제주서귀포']
    # gu_city_series = pd.Series(gu_city)
    column_list = peong_df.columns.to_list()
    city_series = pd.Series(column_list)
    draw_list = []
    if selected_dosi in gu_city:
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()
    elif selected_dosi == '전국':
        draw_list = ['전국', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '경기', '강원', '충북', '충남', '전북', '전남', \
                        '경남', '경북', '제주서귀포']
    elif selected_dosi == '수도권':
        draw_list = ['서울', '경기', '인천']
    elif selected_dosi == '6개광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산', '인천']
    elif selected_dosi == '5개광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산']
    elif selected_dosi == '경기':
        draw_list = ['경기', '수원', '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', \
             '용인', '시흥', '군포', '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기광주', '화성']
    elif selected_dosi in do_list:
        draw_list = small_list
    
    if selected_dosi3 in draw_list:
        draw_list = city_series[city_series.str.contains(selected_dosi3)].to_list()
    if selected_dosi3 in gu_city:
        draw_list = city_series[city_series.str.contains(selected_dosi3)].to_list()
    
    draw_df = last_df.loc[draw_list,:]

    # 사분면 그래프로 그려보자.
    #매매/전세 증감률 Bubble Chart
    title = dict(text='주요 시-구 월간 평균 매매/전세평단가', x=0.5, y = 0.9) 
    fig = px.scatter(draw_df, x='평균매매가', y='평균전세가', color='평균매매가', size=abs(draw_df['평균매매가']), 
                        text= draw_df.index, hover_name=draw_df.index, color_continuous_scale='Bluered')
    fig.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="만원")
    fig.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="만원")
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)