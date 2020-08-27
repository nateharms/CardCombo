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

    return render_template('home.html', cards=list(db.index))


@app.route('/loading', methods=['GET', 'POST'])
def loading():

    return redirect('/results')

@app.route('/results', methods=['GET', 'POST'])
def plots():
    #try:
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
    print('Existing cards...')
    cards_to_consider = [
        request.args['card_1'], 
        request.args['card_2'], 
        request.args['card_3']
    ]
    print(expenses, cards_to_consider)
        
    _, simulation_results = simulate_all(db, expenses)
    print(simulation_results)

    results = []
    for num_cards, r in simulation_results.items():
        print(num_cards, r)
        if num_cards == 0:
            continue
        results.append((num_cards, sorted(r, key=lambda x: x[0], reverse=True)[:5]))
    fig = plot_num_of_cards(_)
    figs = []
    for cash_rewards, cards in pd.DataFrame(simulation_results).max():
        if not cards:
            continue
        to_plot = [db.loc[card] for card in cards]
        fig_ = radar_plot(to_plot)
        figs.append(fig_.to_html())

    return render_template('plots.html', results=results, plot=fig.to_html(), figs=figs )

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