import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import FinanceDataReader as fdr

import streamlit as st
from datetime import datetime

#챠트 기본 설정
# colors 
marker_colors1 = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
#marker_colors1 = ['rgb(27,38,81)', 'rgb(22,108,150)', 'rgb(205,32,40)', 'rgb(255,69,0)', 'rgb(237,234,255)']
marker_colors2 = ['rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)', 'rgb(27,38,81)', 'rgb(205,32,40)']
template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
pio.templates["myID"] = go.layout.Template(
    layout_annotations=[
        dict(
            name="draft watermark",
            text="Graph by 기하급수적",
            textangle=0,
            opacity=0.5,
            font=dict(color="black", size=10),
            xref="paper",
            yref="paper",
            x=0.9,
            y=0.2,
            showarrow=False,
        )
    ]
)

def ecos_monthly_chart(input_ticker, df1, df2):
    df3 = df1.pct_change(periods=12)*100
    df3 = df3.fillna(0)
    df3 = df3.round(decimals=2)
    item_list = df1.columns.values.tolist()
    item_list2 = df2.columns.values.tolist()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label=item_list[0], value = df1.iloc[-1,0], delta=df1.iloc[-2,0])
    col2.metric(label=item_list2[0]+"YOY", value =df3.iloc[-1,0], delta=df2.iloc[-2,0])
    col3.metric(label=item_list[1], value =df1.iloc[-1,1], delta=df1.iloc[-2,1])
    col4.metric(label=item_list2[1]+"YOY", value =df3.iloc[-1,1], delta=df2.iloc[-2,1])
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            #st.subheader(input_ticker)
            x_data = df1.index
            titles = dict(text= input_ticker, x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = []
            y_data_line = []
            for item in item_list:
                y_data_bar.append(item)
                y_data_line.append(item)

            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df2.loc[:,y_data], 
                                            text= df2[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}')
            if input_ticker == '가계신용': 
                fig.update_yaxes(title_text='대출금액(조원)', range=[0, max(df1.loc[:,y_data_bar[0]])*1.2], zeroline=True, ticksuffix="조원", secondary_y = False)
            else:
                fig.update_yaxes(title_text=input_ticker, range=[0, max(df1.loc[:,y_data_bar[0]])*1.2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='전월대비증감', range=[-max(df2.loc[:,y_data_line[0]]), max(df2.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            x_data = df1.index
            titles = dict(text= input_ticker, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = []
            y_data_line = []
            for item in item_list:
                y_data_bar.append(item)
                y_data_line.append(item)

            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df3.loc[:,y_data], 
                                            text= df3[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            if input_ticker == '가계신용': 
                fig.update_yaxes(title_text='대출금액(조원)', range=[0, max(df1.loc[:,y_data_bar[0]])*1.2], zeroline=True, ticksuffix="조원", secondary_y = False)
            else:
                fig.update_yaxes(title_text=input_ticker, range=[0, max(df1.loc[:,y_data_bar[0]])*1.2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='전년대비증감', range=[-max(df3.loc[:,y_data_line[0]]), max(df3.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            # fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="조원", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)


def fred_monthly_chart(ticker, kor_exp, df):
    mom_df = df.pct_change()*100
    mom_df = mom_df.fillna(0)
    mom_df = mom_df.round(decimals=2)
    yoy_df = df.pct_change(periods=12)*100
    yoy_df = yoy_df.fillna(0)
    yoy_df = yoy_df.round(decimals=2)
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            st.subheader(kor_exp)
            x_data = df.index
            title = kor_exp
            titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [mom_df.columns[0]]
            y_data_line= [df.columns[0]]

            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = mom_df.loc[:,y_data], 
                                            text= mom_df[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df.loc[:,y_data],
                                            marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text=ticker, range=[0, max(df.loc[:,y_data_bar[0]])*1.2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='MOM', range=[-max(mom_df.loc[:,y_data_line[0]]), max(mom_df.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="Billions of Dollars", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            st.subheader(kor_exp)
            x_data = df.index
            title = kor_exp
            titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [yoy_df.columns[0]]
            y_data_line= [df.columns[0]]

            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = yoy_df.loc[:,y_data], 
                                            text= yoy_df[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df.loc[:,y_data],
                                            marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text=ticker, range=[0, max(df.loc[:,y_data_bar[0]])*1.2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='YOY', range=[-max(yoy_df.loc[:,y_data_line[0]]), max(yoy_df.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="Billions of Dollars", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)

def ecos_spread_chart(input_ticker, df1):
    item_list = df1.columns.values.tolist()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label=item_list[0], value = df1.iloc[-1,0], delta=df1.iloc[-1,3])
    col2.metric(label=item_list[1], value =df1.iloc[-1,1], delta=df1.iloc[-1,3])
    col3.metric(label=item_list[2], value =df1.iloc[-1,2])
    col4.metric(label=item_list[3], value =df1.iloc[-1,3])
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            #st.subheader(input_ticker)
            x_data = df1.index
            titles = dict(text= input_ticker, x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df1.columns[3]]
            y_data_line = [df1.columns[0], df1.columns[1]]
            y_data_color = [df1.columns[4]]

            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df1.loc[:,y_data], 
                                            text= df1[y_data], textposition = 'inside', marker_color= df1.loc[:,color]), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}')
            fig.update_yaxes(title_text=input_ticker, range=[-max(df1.loc[:,y_data_line[1]]), max(df1.loc[:,y_data_line[1]])* 1.5], secondary_y = True)
            fig.update_yaxes(title_text=df1.columns[3], secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True,  zerolinecolor='pink', ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            x_data = df1.index
            titles = dict(text= input_ticker, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df1.columns[3]]
            y_data_line = [df1.columns[0], df1.columns[1], df1.columns[2]]
            y_data_color = [df1.columns[4]]
            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df1.loc[:,y_data], 
                                            text= df1[y_data], textposition = 'inside', marker_color= df1.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            fig.update_yaxes(title_text=input_ticker, range=[-max(df1.loc[:,y_data_line[0]]), max(df1.loc[:,y_data_line[0]])* 1.5], showgrid = True, zeroline=True, zerolinecolor='pink', ticksuffix="%", secondary_y = False)
            fig.update_yaxes(title_text=df1.columns[3], showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)


def fred_spread_chart(df1, df2):
    df2 = df2.dropna()
    last_df = df1.iloc[-1].to_frame()
    last_df.columns = [last_df.columns[0].strftime('%Y.%m.%d')]
    last_df.loc[:,"기준금리차"] = last_df.iloc[:,0] - df2.iloc[-1,0]
    last_df.loc[:,'color'] = np.where(last_df['기준금리차']<0, '#FFB8B1', '#E2F0CB')
    df2.loc[:,'10Y2Ycolor'] = np.where(df2['금리차10Y2Y']<0, '#FFB8B1', '#E2F0CB')
    df2.loc[:,'10Y3Mcolor'] = np.where(df2['금리차10Y3M']<0, '#FFB8B1', '#E2F0CB')
    item_list = df1.columns.values.tolist()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label=df2.columns[0], value = df2.iloc[-1,0])#기준 금리
    col2.metric(label=item_list[2], value =df1.iloc[-1,2], delta=df1.iloc[-1,2]-df2.iloc[-1,0])  #3개월 금리
    col3.metric(label=item_list[6], value =df1.iloc[-1,6], delta=df1.iloc[-1,6]-df2.iloc[-1,0]) #2년 금리
    col4.metric(label=item_list[10], value =df1.iloc[-1,10], delta=df1.iloc[-1,10]-df2.iloc[-1,0]) # 10년 금리
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            #st.subheader(input_ticker)
            x_data = last_df.index
            titles = dict(text= "US Bond Yield Curve", x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [last_df.columns[1]]
            y_data_line = [last_df.columns[0]]
            y_data_color = [last_df.columns[2]]

            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = last_df.loc[:,y_data]*100, 
                                            text= round(last_df[y_data]*100,0), textposition = 'inside', marker_color= last_df.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= last_df.loc[:,y_data],
                                            text= last_df[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}')
            fig.update_yaxes(title_text='금리', secondary_y = False)
            fig.update_yaxes(title_text='금리차', secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True,  zerolinecolor='pink', ticksuffix="bps", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
            fig.add_hline(y=df2.iloc[-1,0], line_width=2, line_dash='dot', line_color="red", annotation_text=f"Federal Funds Effective Rate: {df2.iloc[-1,0]}%", annotation_position="bottom right")
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            x_data = df2.index
            titles = dict(text= "주요금리", x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df2.columns[0]] #기준금리
            y_data_line = [df2.columns[1], df2.columns[2], df2.columns[3]] #각 금리
            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df2.loc[:,y_data], 
                                            text= df2[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df2.loc[:,y_data],
                                            text= df2[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            fig.update_yaxes(title_text="금리", range=[-max(df2.loc[:,y_data_line[0]]), max(df2.loc[:,y_data_line[0]])* 1.5], showgrid = True, zeroline=True, zerolinecolor='pink', ticksuffix="%", secondary_y = False)
            fig.update_yaxes(title_text="기준금리", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            x_data = df2.index
            titles = dict(text= "장단기금리차(10Y2Y)", x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df2.columns[4]]
            y_data_line = [df2.columns[1], df2.columns[2]]
            y_data_color = [df2.columns[6]]
            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df2.loc[:,y_data], 
                                            text= df2[y_data], textposition = 'inside', marker_color= df2.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df2.loc[:,y_data],
                                            text= df2[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            fig.update_yaxes(title_text="금리", range=[-max(df2.loc[:,y_data_line[0]]), max(df2.loc[:,y_data_line[0]])* 1.5], showgrid = False, zeroline=True, zerolinecolor='pink', ticksuffix="%", secondary_y = False)
            fig.update_yaxes(title_text="금리차", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="bp", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
            st.write("")
        with col3: 
            x_data = df2.index
            titles = dict(text= "장단기금리차(10Y3M)", x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df2.columns[5]]
            y_data_line = [df2.columns[1], df2.columns[3]]
            y_data_color = [df2.columns[7]]
            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df2.loc[:,y_data], 
                                            text= df2[y_data], textposition = 'inside', marker_color= df2.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df2.loc[:,y_data],
                                            text= df2[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            fig.update_yaxes(title_text="금리", range=[-max(df2.loc[:,y_data_line[0]]), max(df2.loc[:,y_data_line[0]])* 1.5], showgrid = False, zeroline=True, zerolinecolor='pink', ticksuffix="%", secondary_y = False)
            fig.update_yaxes(title_text="금리차", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="bp", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        

