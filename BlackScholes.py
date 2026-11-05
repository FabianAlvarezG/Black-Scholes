# We will simulate a strategy following from the Black-Scholes model

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.stats import lognorm



class BlackScholes:
    def __init__(self, S0, K, T, r, sigma, mu, num_steps=1000):
        self.S0 = S0  # Initial stock price
        self.K = K    # Strike price
        self.T = T    # Time to maturity (in years)
        self.r = r    # Risk-free interest rate
        self.sigma = sigma  # Volatility of the underlying asset
        self.num_steps = num_steps  # Number of time steps for simulation
        self.mu= mu  # Drift of the underlying asset

    def simulate_stock_price(self):
        # We solve the following stochastic differential equation for the price of an asset in the Ito sense:
        # dS = r * S * dt + sigma * S * dW
        # We define Y = ln(S), then we have dY = (r - 0.5 * sigma^2) * dt + sigma * dW (Using Ito's lemma)
        # We can simulate the process using the Euler-Maruyama method
        #Y_(t) = Y_(-1) + (r - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * Z, where Z ~ N(0,1)
        #The price of the asset at time t is then given by S_t = exp(Y_t)

        n = self.num_steps
        dt = self.T / n

        # Exact log-Euler scheme for GBM: n steps of size dt, so the last point is S_T
        z = np.random.standard_normal(n)
        increments = (self.mu - 0.5 * self.sigma ** 2) * dt + self.sigma * np.sqrt(dt) * z
        asset_prices = np.empty(n + 1)
        asset_prices[0] = self.S0
        asset_prices[1:] = self.S0 * np.exp(np.cumsum(increments))

        # Option values use the remaining time to maturity tau = T - t at each step.
        # At t = T (tau = 0) the formula is undefined, so we use the payoff instead.
        tau = self.T - dt * np.arange(n)
        call_prices = np.empty(n + 1)
        put_prices = np.empty(n + 1)
        call_prices[:n] = self.call_price(asset_prices[:n], tau)
        put_prices[:n] = self.put_price(asset_prices[:n], tau)
        call_prices[n] = max(asset_prices[n] - self.K, 0)
        put_prices[n] = max(self.K - asset_prices[n], 0)

        self.call_prices = call_prices
        self.put_prices = put_prices
        self.asset_prices = asset_prices   

    def d1(self, S=None, tau=None):
        if S is None:
            S = self.S0
        if tau is None:
            tau = self.T  # time to maturity
        return (np.log(S / self.K) + (self.r + 0.5 * self.sigma ** 2) * tau) / (self.sigma * np.sqrt(tau))

    def d2(self, S=None, tau=None):
        if tau is None:
            tau = self.T
        return self.d1(S, tau) - self.sigma * np.sqrt(tau)

    def call_price(self, S=None, tau=None):
        if S is None:
            S = self.S0
        if tau is None:
            tau = self.T
        d1 = self.d1(S, tau)
        d2 = self.d2(S, tau)
        return (S * norm.cdf(d1) - self.K * np.exp(-self.r * tau) * norm.cdf(d2))

    def put_price(self, S=None, tau=None):
        if S is None:
            S = self.S0
        if tau is None:
            tau = self.T
        d1 = self.d1(S, tau)
        d2 = self.d2(S, tau)
        return (self.K * np.exp(-self.r * tau) * norm.cdf(-d2) - S * norm.cdf(-d1))
    
class monteCarloOptionPricing(BlackScholes):
    # This class will simulate num_simulations of the stock price and option prices using the Black-Scholes model
    def __init__(self, S0, K, T, r, sigma, mu, num_simulations=100, num_steps=1000):
        super().__init__(S0, K, T, r, sigma, mu, num_steps)
        self.num_simulations = num_simulations

    def monte_carlo_option_price(self):
        # Returns a tuple of (asset_prices, call_prices, put_prices) where each is a 2D array of shape (num_simulations, num_steps)
        call_prices = np.zeros((self.num_simulations, self.num_steps + 1))
        put_prices = np.zeros((self.num_simulations, self.num_steps + 1))
        asset_prices = np.zeros((self.num_simulations, self.num_steps + 1))
        for i in range(self.num_simulations):
            self.simulate_stock_price()
            call_prices[i] = self.call_prices
            put_prices[i] = self.put_prices
            asset_prices[i] = self.asset_prices

        self.call_prices = call_prices.mean(axis=0)
        self.put_prices = put_prices.mean(axis=0)
        self.std_call_prices = call_prices.std(axis=0)
        self.std_put_prices = put_prices.std(axis=0)
        return asset_prices, call_prices, put_prices
    


if __name__ == "__main__":
    S0 = 100  # Initial stock price
    K = 100   # Strike price
    T = 1     # Time to maturity (1 year)
    r = 0.05  # Risk-free interest rate (5%)
    sigma = 0.2  # Volatility (20%)
    mu = 2*r  # Drift is the same as the risk-free rate for risk-neutral pricing
   
    s = np.linspace(1e-6, 3*S0, 1000)
    x0 = np.log(S0) + (mu - 0.5 * sigma ** 2) * T
    scale = sigma * np.sqrt(T)
    expected_distribution = lognorm.pdf(s, s=scale, scale=np.exp(x0))

    bs = monteCarloOptionPricing(S0, K, T, r, sigma, mu, num_simulations=10000, num_steps=1000)
    asset_prices, call_prices, put_prices = bs.monte_carlo_option_price()


    plt.figure(figsize=(12, 6))
    plt.hist(asset_prices[:, -1], bins=30, alpha=0.7, color='blue', label='Stock Price Distribution', density=True)
    plt.plot(s, expected_distribution, color='red', label='Expected Lognormal Distribution')
    plt.title('Distribution of Stock Prices at Maturity')
    plt.xlabel('Stock Price')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid()
    plt.show()
  
