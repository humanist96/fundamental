import time
from datetime import datetime

import numpy as np
import pandas as pd

import requests
import json
from pandas.io.json import json_normalize

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
import FinanceDataReader as fdr

#choroplethViz
import mapboxgl
from mapboxgl.viz import *
from mapboxgl.utils import create_color_stops
from mapboxgl.utils import create_numeric_stops

# 챠트 기본 설정 
# marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

def run_pop_index(selected_city2, df, df_change, sdf, sdf_change):
    titles = dict(text= '('+selected_city2 +') 세대수 증감', x=0.5, y = 0.9) 
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 


    fig.add_trace(go.Scatter(mode='lines', name = '인구수', x =  df.index, y= df[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name = '세대수', x =  sdf.index, y= sdf[selected_city2], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Bar(name = '세대수 증감', x = sdf_change.index, y = sdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[3]), secondary_y = True)
    fig.add_trace(go.Bar(name = '인구수 증감', x = df_change.index, y = df_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)


    fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    # fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='인구세대수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='증감', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="%") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    # fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def run_price_index(selected_city2, mdf,jdf, mdf_change, jdf_change, bubble_df2, m_power) :
   
    titles = dict(text= '('+selected_city2 +') 주간 매매-전세 지수', x=0.5, y = 0.9) 

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
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
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

    
    fig.add_trace(go.Scatter(mode='lines', name = '버블지수', x =  bubble_df2.index, y= bubble_df2[selected_city2], marker_color = marker_colors[0]), secondary_y = True)
    fig.add_trace(go.Scatter(mode='lines', name ='전세파워', x =  m_power.index, y= m_power[selected_city2], marker_color = marker_colors[3]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='전세파워', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='red',  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='버블지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='blue', secondary_y = True) #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

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
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    titles = dict(text= ' 매수매도 우위 지수('+ selected_dosi + ')', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '매도자 많음', x =  js_1.index, y= js_1[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='매수자 많음', x =  js_2.index, y= js_2[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
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

def draw_basic(last_df,df, geo_data, last_pop):
    # 월간 인구수 세대수 증감
    title = dict(text='주요 시 구 월간 인구수-세대수 증감', x=0.5, y = 0.9) 
    fig1 = px.scatter(last_pop, x='인구증감', y='세대증감', color='세대증감', size=abs(last_pop['세대증감']), 
                        text= last_pop.index, hover_name=last_pop.index, color_continuous_scale='Bluered')
    fig1.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template="seaborn")
    fig1.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig1.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    st.plotly_chart(fig1)

    #choroplethmapbax
    token = 'pk.eyJ1Ijoic2l6aXB1c3gyIiwiYSI6ImNrbzExaHVvejA2YjMyb2xid3gzNmxxYmoifQ.oDEe7h9GxzzUUc3CdSXcoA'
    fig = go.Figure(go.Choroplethmapbox(geojson=geo_data, locations=df['SIG_CD'], z=df['매매증감'],
                                        colorscale="Reds", zmin=df['매매증감'].min(), zmax=df['매매증감'].max(), marker_line_width=0))
    fig.update_traces(hovertext=df['index'])
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token,
                    mapbox_zoom=6, mapbox_center = {"lat": 37.414, "lon": 127.177})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)

    title = dict(text='주요 시 구 주간 매매지수 증감',  x=0.5, y = 0.9) 
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
    fig = px.bar(last_df, x= last_df.index, y=last_df.iloc[:,0], color=last_df.iloc[:,0], color_continuous_scale='Bluered', \
                text=last_df.index)
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_traces(texttemplate='%{label}', textposition='outside')
    fig.update_layout(uniformtext_minsize=6, uniformtext_mode='show')
    fig.update_yaxes(title_text='주간 매매지수 증감률', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.add_hline(y=last_df.iloc[0,0], line_dash="dash", line_color="red", annotation_text=f"전국 증감률: {round(last_df.iloc[0,0],2)}", \
                annotation_position="bottom right")
    st.plotly_chart(fig)
    st.dataframe(last_df.T.style.highlight_max(axis=1))

    with st.beta_container():
        #매매/전세 증감률 Bubble Chart
        title = dict(text='주요 시 구 주간 매매/전세지수 증감', x=0.5, y = 0.9) 
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
    fig.add_trace(go.Bar(name = '가구소득', x = income_df.index, y = income_df[selected_city2], marker_color=  marker_colors[2]), secondary_y = True)
    fig.add_trace(go.Bar(name = '주택가격', x = price_df.index, y = price_df[selected_city2], marker_color=  marker_colors[1]), secondary_y = True)
    fig.update_layout(barmode='stack')
    
    # fig.add_trace(go.Scatter(mode='lines', name ='전세지수', x =  jdf.index, y= jdf[selected_city2], marker_color = marker_colors[3]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='PIR', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='가구소득-주택가격', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="만원") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)