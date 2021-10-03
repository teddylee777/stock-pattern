from flask import Flask, render_template, request, Response
import pattern as pt

import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
import time


matplotlib.use('Agg')


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


def long_load(typeback):
    time.sleep(5) #just simulating the waiting period
    return "You typed: %s" % typeback


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

@app.route('/pattern', methods=['POST'])
def pattern():
    long_load('시간 걸리는중')
    code = request.form['code']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    p = pt.PatternFinder()
    p.set_stock(code)
    result = p.search(startdate, enddate)
    N = 5
    preds = p.stat_prediction(result, period=N)
    
    avg_ = preds.mean() * 100
    min_ = preds.min() * 100
    max_ = preds.max() * 100
    size_ = len(preds)
    print(avg_, min_, max_, size_)
    return render_template('result.html', code=code, startdate=startdate, enddate=enddate, avg=round(avg_, 2), min=round(min_, 2), max=round(max_, 2), size=size_)

if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host="0.0.0.0", port=port, debug=True)
    app.run(debug=True)
