import re
from flask import Flask, render_template, request, Response, url_for, redirect
import pattern as pt
import io
import time
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_finance import candlestick_ohlc
import numpy as np
import FinanceDataReader as fdr

matplotlib.use('Agg')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        code = request.form['code']
        startdate = request.form['startdate']
        enddate = request.form['enddate']
        if request.form['action'] == '패턴검색':
            return redirect(url_for('pattern', startdate=startdate, enddate=enddate, code=code))
        elif request.form['action'] == '차트확인':
            return render_template('index.html', startdate=startdate, enddate=enddate, code=code, chart=True)

@app.route('/plot.png', methods=['GET'])
def plot_png():
    code  = request.args.get('code', None)
    startdate  = request.args.get('startdate', None)
    enddate  = request.args.get('enddate', None)
    print(startdate)
    p = pt.PatternFinder()
    p.set_stock(code)
    result = p.search(startdate, enddate)
    print(result)
    if len(result) > 0:
        fig = p.plot_pattern(list(result.keys())[0])
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/plotchart.png', methods=['GET'])
def plot_chart():
    code  = request.args.get('code', None)
    startdate  = request.args.get('startdate', None)
    enddate  = request.args.get('enddate', None)
    
    fig = plt.figure()
    fig.set_facecolor('w')
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    axes = []
    axes.append(plt.subplot(gs[0]))
    axes.append(plt.subplot(gs[1], sharex=axes[0]))
    axes[0].get_xaxis().set_visible(False)

    print(code)
    data = fdr.DataReader(code)
    data_ = data[startdate:enddate]
    print(code, startdate, enddate)

    x = np.arange(len(data_.index))
    ohlc = data_[['Open', 'High', 'Low', 'Close']].values
    dohlc = np.hstack((np.reshape(x, (-1, 1)), ohlc))

    # 봉차트
    candlestick_ohlc(axes[0], dohlc, width=0.5, colorup='r', colordown='b')

    # 거래량 차트
    axes[1].bar(x, data_['Volume'], color='grey', width=0.6, align='center')
    axes[1].set_xticks(range(len(x)))
    axes[1].set_xticklabels(list(data_.index.strftime('%Y-%m-%d')), rotation=90)
    axes[1].get_yaxis().set_visible(False)

    plt.tight_layout()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(410)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html')

@app.route('/pattern', methods=['GET', 'POST'])
def pattern():
    if request.method == 'POST':
        code = request.form['code']
        startdate = request.form['startdate']
        enddate = request.form['enddate']
    else:
        code  = request.args.get('code', None)
        startdate  = request.args.get('startdate', None)
        enddate  = request.args.get('enddate', None)
    p = pt.PatternFinder()
    p.set_stock(code)
    result = p.search(startdate, enddate)
    N = 5
    preds = p.stat_prediction(result, period=N)

    if len(preds) > 0:
        avg_ = preds.mean() * 100
        min_ = preds.min() * 100
        max_ = preds.max() * 100
        size_ = len(preds)
        print(avg_, min_, max_, size_)
        return render_template('result.html', code=code, startdate=startdate, enddate=enddate, avg=round(avg_, 2), min=round(min_, 2), max=round(max_, 2), size=size_)
    else:
        return render_template('result.html', code=code, startdate=startdate, enddate=enddate, noresult=1)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
    # app.run(debug=True)
