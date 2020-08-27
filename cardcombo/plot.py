import os, pickle
import random
import textwrap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def radar_plot(series_list, save_name=None, save_svg=False, save_html=False, save_dir='.'):
    """
    A function to create the radar plots that are used in the results page of CardCombo
    
    Inputs: 
    - series_list, a list of pandas Series objects for our plots
    - save_name, str: the name of the save file if needed
    - save_svg / save_html, bool: would you like to save an svg or html file of the plot
    - save_dir, str: where you'd like to save the figure

    Returns:
    - fig, plotly figure: a figure containing the overlaid rewards profile
    - names, list of str: a list contining the names of each of the cards
    """
    if not isinstance(series_list, list):
        series_list = [series_list]
    
    fig = go.Figure()
    names = []
    for series in series_list:
        names.append(series.name)

        if series.rotating == True:
            fig.add_trace(go.Scatterpolar(
                r = series[['flights', 'hotel', 'grocery', 'gas', 'dining', 'other']].values, 
                name='<br>'.join(textwrap.wrap(series.name, 30)), 
                theta=['Flights', 'Hotel', 'Grocery', 'Gas', 'Dining', 'Other'], 
                fill='toself', opacity=0.3, line=dict(dash='dash')))
        else:
            fig.add_trace(go.Scatterpolar(
                r = series[['flights', 'hotel', 'grocery', 'gas', 'dining', 'other']].values, 
                name='<br>'.join(textwrap.wrap(series.name, 30)), 
                theta=['Flights', 'Hotel', 'Grocery', 'Gas', 'Dining', 'Other'], 
                fill='toself', opacity=0.3))

    if save_name:
        name = save_name
    elif len(series_list) == 1:
        name = series_list[0].name #the save name if one wasn't provided
    else:
        name = 'credit_rewards_profile'

    
    fig.update_layout(
                title_text='Credit Rewards Profile: {} Cards'.format(len(series_list)), 
                title_x=0.5, 
                polar = dict(radialaxis=dict(range=[0, 6])),
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=0.7)
                )

    if save_html:
        with open(f'{os.path.join(save_dir, name)}.html', 'w') as f:
            f.write(fig.to_html())

    if save_svg:
        with open(f'{os.path.join(save_dir, name)}.svg', 'wb') as f:
            f.write(fig.to_image('svg'))

    return fig, names



def plot_num_of_cards(results):
    """
    A method to create the main plot of the results page containing the net rewards for each of the simulations

    Inputs:
    - results, dict: the output of the cardcombo.simulate.simulate_all function

    Outputs:
    - fig, Plotly figure: the figure of interest
    """

    # Creating a df that will be used for the plots from the results dictionary
    df_results = []
    for num_cards, num_results in results.items():
        for num_result in num_results:
            text = 'Number of New Cards: {}<br>Net Rewards: $ {}<br>Cards:<br>- {}'.format(
                str(num_cards), str(round(num_result[0],2)), str("<br>- ".join(sorted(num_result[1])))
            )
            df_results.append([num_cards, text] + list(num_result))
    df = pd.DataFrame(df_results, columns=['num_cards', 'text','net_rewards', 'cards'])
    df.cards = df.cards.map(lambda x: ',\n'.join(x)[:-3])
    df['rand_x'] = df.num_cards.map(lambda x: x + random.gauss(0, 0.1))

    # edit this bit if we want to make subplots with click actions
    fig = go.FigureWidget(
        make_subplots(rows=1, cols=1, # Change rows=2
        #specs=[[{"type": "scatter"}], [{'type': 'scatterpolar'}]] # Take out this comment
        )
        )

    fig.add_trace(
        go.Scatter(
            name='Aggrigate Net Rewards',
            x=df['rand_x'], 
            y=df['net_rewards'], 
            mode='markers', 
            text=df['text'],
            hovertemplate='%{text}',
            marker=dict(
                color='mintcream',
                size=5,
                opacity=0.4, 
                line=dict(
                    color='Black',
                    width=0.5
                ))
        ),
        row=1, col=1
    )

    scatter = fig.data[0]

    text = None

    def update_point(trace, points, selector):
        """
        Our click action for creating our subplot
        """
        # Removing any existing scatterpolar plots if they exist
        new_data = []
        for d in fig.data:
            if d._plotly_name == 'scatterpolar':
                continue
            new_data.append(d)
        fig.data = new_data

        # Setting all points to the proper color, size and opacity  
        c = np.full_like(trace.text, 'mintcream')
        s = np.full_like(trace.text, 5)
        o = np.full_like(trace.text, 0.4)

        # Setting the clicked point
        i = points.point_inds[0]
        c[i] = 'gold'
        s[i] = 15
        o[i] = 1

        # Updating the clicked point with the proper color, size and opacity  
        with fig.batch_update():
            scatter.marker.color = list(c)
            scatter.marker.size = list(s)
            scatter.marker.opacity = list(o)

        # Creating the radar plots to add to the subplot
        text = trace.text[i]
        cards = text.split('Cards:<br>- ')[-1].split('<br>- ')
        series = []
        for card in cards:
            series.append(db.loc[card])

        radar = radar_plot(series)
        for t in radar.data:
            fig.add_trace(t, row=2, col=1)

    # Creating the min, max and median plots on the figure
    fig.add_trace(
        go.Scatter(x=df.num_cards.unique(), 
                   y=df.groupby('num_cards').max()['net_rewards'],
                   mode='lines',
                   name='Maximum Rewards', 
                   line=dict(color='#46039f')), 
                   row=1, col=1)
    fig.add_trace(
        go.Scatter(x=df.num_cards.unique(), 
                   y=df.groupby('num_cards').median()['net_rewards'],
                   mode='markers',
                   name='Median Rewards', 
                   marker=dict(color='#bd3786', size=8, line=dict(color='black', width=0.5))),
                   row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.num_cards.unique(), 
                   y=df.groupby('num_cards').min()['net_rewards'],
                   mode='lines', 
                   name='Minimum Rewards', 
                   line=dict(color='#ed7953')), 
                   row=1, col=1)

    #scatter.on_click(update_point) # Remove this comment to add the click function 

    # Final adjustment 
    fig.update_layout(
        title="Custom Credit Card Profile",
        xaxis_title="Number of New Credit Cards",
        yaxis_title="Annual Net Rewards Earned ($)",
        legend_title="Legend Title",
        width=1000, height=800
    )
    return fig

