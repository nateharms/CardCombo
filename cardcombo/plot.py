import os, pickle
import random
import textwrap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def radar_plot(series_list, save_name=None, save_svg=False, save_html=False, save_dir='.'):
    
    if not isinstance(series_list, list):
        series_list = [series_list]
    
    fig = go.Figure()
    for series in series_list:
        fig.add_trace(go.Scatterpolar(
            r = series[['flights', 'hotel', 'grocery', 'gas', 'dining', 'other']].values, 
            name=series.name, 
            theta=['Flights', 'Hotel', 'Grocery', 'Gas', 'Dining', 'Other'], 
            fill='toself', opacity=0.3))

    if len(series_list) == 1:
        name = series_list[0].name
        fig.update_layout(title_text=name, 
                  title_x=0.5, 
                  polar = dict(radialaxis = dict(range=[0, 6])))
    else:
        name = 'credit_rewards_profile'
        fig.update_layout(title_text='Credit Rewards Profile: {} Cards'.format(len(series_list)), 
                  title_x=0.5, 
                  polar = dict(radialaxis = dict(range=[0, 6])))
    if save_name:
        name = save_name
    if save_html:
        with open(f'{os.path.join(save_dir, name)}.html', 'w') as f:
            f.write(fig.to_html())

    if save_svg:
        with open(f'{os.path.join(save_dir, name)}.svg', 'wb') as f:
            f.write(fig.to_image('svg'))

    return fig



def plot_num_of_cards(results):
    
    df = pd.DataFrame(results)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df.columns, y=df.max(),
                   mode='lines',
                   name='Maximum Rewards'))
    fig.add_trace(
        go.Scatter(x=df.columns, y=df.median(),
                   mode='markers',
                   name='Median Rewards'))
    fig.add_trace(
        go.Scatter(x=df.columns, y=df.min(),
                   mode='lines', name='Minimum Rewards'))

    for col in df.columns:
        if col == 0:
            showlegend = True
            fig.add_trace(go.Violin(x=[col]*df[col].shape[0],
                                    y=df[col],
                                    opacity=0.5,
                                    fillcolor='black',
                                    line_color='black',
                                    hoverinfo='none',
                                    name='Distribution of Simulated Combinations',
                                    showlegend=True
                                    ))

        else:
            fig.add_trace(go.Violin(x=[col]*df[col].shape[0],
                                    y=df[col],
                                    opacity=0.5,
                                    fillcolor='black',
                                    line_color='black',
                                    hoverinfo='none',
                                    showlegend=False
                                    ))


    fig.update_layout(
        title="Custom Credit Card Profile",
        xaxis_title="Number of Credit Cards",
        yaxis_title="Annual Rewards Earned ($)",
        legend_title="Legend Title",
        hovermode='x'
    )


    return fig

