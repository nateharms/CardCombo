from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from alpha_vantage.timeseries import TimeSeries
import matplotlib
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
import pandas as pd
import time, os
import pickle



cards =  pickle.load(open('rewards.pkl', 'rb'))

app = Flask(__name__, static_folder='templates/images')
Bootstrap(app)

app.vars = {}

@app.route('/', methods=['GET', 'POST'])
def home():
    if (request.method == 'GET' and len(request.args) != 0):
        return(plots())
    print(list(cards.index)[:5])

    return render_template('base.html', cards=list(cards.index))


@app.route('/loading', methods=['GET', 'POST'])
def loading():

    return redirect('/results')

@app.route('/results', methods=['GET', 'POST'])
def plots():
    print([i for i in request.args.items()])
    if (request.method == 'GET' and len(request.args) != 0):
        print(app.vars)
    print('Loading...')
    try:
        flights = request.args['flights']
        #flight_freq = 
    
    except:
        return redirect('/')
        
    return render_template('plots.html')

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


if __name__ == '__main__':app.run(port=8000)