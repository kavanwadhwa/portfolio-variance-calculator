import numpy as np
import yfinance as yf
import math

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
    tickers = list(portfolioBreakdown.keys())
    
    # get the market value of each ticker in the portfolio
    portfolioValues = np.array([get_current_price(ticker) * portfolioBreakdown[ticker] for ticker in tickers])
    portfolioSum = np.sum(portfolioValues)

    # calculate weights
    weights = np.array([value / portfolioSum for value in portfolioValues])

    return weights, tickers

def calculatePortfolioVariance(portfolioBreakdown, period, interval):
    print("weights and tickers")
    weights, tickers = getWeightsAndTickers(portfolioBreakdown)
    print("data from yfinance")
    # get historical data from yfinance (daily values for 1 year)
    data = yf.download(tickers = list(tickers), period=period, interval=interval, group_by = 'ticker', threads = True)
    data = data.dropna()

    # All variables hold percents, variances & covariances need to be divided by 100 when used
    returns = [[] for ticker in tickers]
    means = np.array([0.0 for ticker in tickers])
    variances = np.array([0.0 for ticker in tickers])

    for index, ticker in enumerate(tickers):
        # get ticker returns and mean ticker return using close and open columns
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