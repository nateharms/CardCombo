from flask import Flask, render_template, request, redirect
from alpha_vantage.timeseries import TimeSeries
import matplotlib
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
import pandas as pd
import time


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if (request.method == 'GET'):
        print(request)
    return render_template('base.html')


@app.route('/loading', methods=['GET', 'POST'])
def loading():

    return redirect('/results')

@app.route('/results', methods=['GET', 'POST'])
def plots():
    render_template('loading.html')
    time.sleep(5)
    print('Loading...')
    return render_template('plots.html')

if __name__ == '__main__':app.run(port=8000)