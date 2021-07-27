from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from flask.helpers import send_from_directory
import numpy as np
import yfinance as yf
import math

app = Flask(__name__, static_url_path='', static_folder='frontend/build')

@app.route('/')
@app.route('/index')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/manifest.json')
def manifest():
    return send_from_directory(app.static_folder, 'manifest.json')

# cors = CORS(app)
api = Api(app)

variance_post_args = reqparse.RequestParser()
variance_post_args.add_argument("portfolio", type=dict, location="json", help="Portfolio is required in dictionary format", required=True)
variance_post_args.add_argument("period", type=str, choices=('1y', '2y', '5y'), default="1y", required=False)
variance_post_args.add_argument("interval", type=str, choices=('1h', '1d', '1wk', '1mo'),  default="1d", required=False)

class Variance(Resource):
    def post(self):
        print("Received POST request")
        args = variance_post_args.parse_args()
        variance, sd = calculatePortfolioVariance(args['portfolio'], args['period'], args['interval'])
        return {"variance": variance, "sd": sd}

api.add_resource(Variance, "/variance")


if __name__ == '__main__':
    app.run()

# Helper functions
def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]

def calculateVariance(returns, mean):
    variations = [(((r - mean) ** 2)) for r in returns]
    variance = (np.sum(variations) / (len(returns) - 1))
    return variance

def calculateCovarianceMatrix(returns, means):
    matrix = np.array([[0.0 for i in range(len(returns))] for j in range(len(returns))])
    for i in range(len(returns)):
        for j in range(len(returns)):
            numerator = np.sum((returns[i] - means[i]) * (returns[j] - means[j]))
            denominator = len(returns[0]) - 1
            matrix[i][j] = numerator / denominator
    return matrix

def getWeightsAndTickers(portfolioBreakdown):
    # get tickers
    tickers = [k.upper() for k in portfolioBreakdown.keys()]
    
    # get the market value of each ticker in the portfolio
    portfolioValues = np.array([get_current_price(ticker) * portfolioBreakdown[ticker] for ticker in tickers])
    portfolioSum = np.sum(portfolioValues)

    # calculate weights
    weights = np.array([value / portfolioSum for value in portfolioValues])

    return weights, tickers

def calculatePortfolioVariance(portfolioBreakdown, period, interval):
    sanitizedPortfolio = {key.upper(): portfolioBreakdown[key] for key in portfolioBreakdown.keys()}
    weights, tickers = getWeightsAndTickers(sanitizedPortfolio)
    
    # get historical data from yfinance (daily values for 1 year)
    data = yf.download(tickers = list(tickers), period=period, interval=interval, group_by = 'ticker', threads = True)
    data = data.dropna()

    # All variables hold percents, variances & covariances need to be divided by 100 when used
    returns = [[] for ticker in tickers]
    means = np.array([0.0 for ticker in tickers])
    variances = np.array([0.0 for ticker in tickers])

    for index, ticker in enumerate(tickers):
        # get ticker returns and mean ticker return using close and open columns
        if len(tickers) == 1:
            tickerReturns = list((data['Close'] - data['Open']) / data['Open'] * 100)
        else:
            tickerReturns = list((data[ticker]['Close'] - data[ticker]['Open']) / data[ticker]['Open'] * 100)
        
        meanTickerReturn = np.average(tickerReturns)

        # calculate variance
        variances[index] = calculateVariance(tickerReturns, meanTickerReturn)

        # store returns and mean for future covariance matrix calculation
        returns[index] = tickerReturns
        means[index] = meanTickerReturn

    # calculate covariance matrix
    covariances = calculateCovarianceMatrix(returns, means)

    portfolio_variance = 0

    # first add all weight * variances for each asset
    for weight, variance in zip(weights, variances):
        portfolio_variance += (weight ** 2) * (variance / 100)

    # then add terms involving covariance of assets
    for i in range(len(tickers)):
        for j in range(i + 1, len(tickers)):
            term = 2 * (covariances[i][j] / 100) * weights[i] * weights[j]
            portfolio_variance += term

    return portfolio_variance, math.sqrt(portfolio_variance)