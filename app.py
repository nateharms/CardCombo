from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from alpha_vantage.timeseries import TimeSeries
import matplotlib
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
import pandas as pd
import time, os
import pickle
from cardcombo.simulate import *
from cardcombo.plot import plot_num_of_cards, radar_plot
import pickle 

db = pickle.load(open('db.pkl', 'rb'))
#db = pd.read_csv('db.csv') # As an option for debugging 

app = Flask(__name__, static_folder='templates/')
Bootstrap(app)

YM_CONVERSION = {'monthly': 12, 'annual':1}


@app.route('/', methods=['GET', 'POST'])
def home():
    if (request.method == 'GET' and len(request.args) != 0):
        return(plots())
    return render_template('home.html', cards=list(sorted(db.index)))


@app.route('/results', methods=['GET', 'POST'])
def plots():
    # To read in the users expenses
    expenses = {}
    print('Reading inputs...')
    print('Flights...')
    expenses['flights'] = float(request.args['flights']) * \
        YM_CONVERSION[request.args['flights-freq']]
    print('Hotel...')
    expenses['hotel'] = float(request.args['hotel']) * \
        YM_CONVERSION[request.args['hotel-freq']]
    print('Grocery...')
    expenses['grocery'] = float(request.args['grocery']) * \
        YM_CONVERSION[request.args['grocery-freq']]
    print('Gas...')
    expenses['gas'] = float(request.args['gas']) * \
        YM_CONVERSION[request.args['gas-freq']]
    print('Dining...')
    expenses['dining'] = float(request.args['dining']) * \
        YM_CONVERSION[request.args['dining-freq']]
    print('Other...')
    expenses['other'] = float(request.args['other']) * \
        YM_CONVERSION[request.args['other-freq']]

    # To read in their existing cards
    print('Existing cards...')
    cards_to_consider = [
        request.args['card_1'], 
        request.args['card_2'], 
        request.args['card_3']
    ]
    cards_to_consider = [c for c in cards_to_consider if c != '']

    # To read in their provided credit score
    credit = request.args['credit_score']
    try: 
        credit = float(credit)
    except:
        credit = 850 # Assume that they have a good credit score
        
    # Simulating the test cases
    simulation_results = simulate_all(db, expenses, cards_to_consider, credit, 9-len(cards_to_consider))

    # Sorting results by the net rewards
    results = []
    for num_cards, r in simulation_results.items():
        if num_cards == 0:
            continue
        results.append((num_cards, sorted(r, key=lambda x: round(x[0],2), reverse=True)[:5]))

    # Plotting the trend of all credit cards in Plotly
    card_fig = plot_num_of_cards(simulation_results).to_html()

    # For best cases, create overlaid card profile
    radar_figs = []
    for cash_rewards, cards in pd.DataFrame(simulation_results).max():
        if not cards:
            continue
        to_plot = [db.loc[card] for card in cards]
        radar_fig, names = radar_plot(to_plot)
        links = list(db.loc[names]['review_link'])
        radar_figs.append((radar_fig.to_html(), zip(names, links)))

    return render_template('plots.html', results=results, card_fig=card_fig, radar_figs=radar_figs )


@app.route('/database')
def database():
    cards = []
    db_copy = db.copy()
    db_copy['sum_of'] = db[['flights', 'hotel', 'grocery', 'gas', 'dining', 'other']].sum(axis=1)
    #db_copy = db_copy.sort_values('sum_of', ascending=False)
    for name in db_copy.index:
        if name in ['Unknown', '']:
            continue
        series = db.loc[name]
        req_credit = series['req_credit']
        if req_credit is None:
            req_credit = 'Unknown'
        cards.append([
            name, 
            series['converted_name'], 
            req_credit, 
            series['annual_fee'], 
            series['annual_bonus'],
            series['rotating'], 
            series['review_link'],
            series['application_link']])

    return render_template('database.html',  cards = cards )


if __name__ == '__main__':app.run(port=8000, debug=True)