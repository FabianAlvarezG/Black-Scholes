# We will simulate a strategy following from the Black-Scholes model

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.stats import lognorm



class BlackScholes:
    def __init__(self, S0, K, T, r, sigma):
        self.S0 = S0  # Initial stock price
        self.K = K    # Strike price
        self.T = T    # Time to maturity (in years)
        self.r = r    # Risk-free interest rate
        self.sigma = sigma  # Volatility of the underlying asset
        self.num_steps = 1000  # Number of time steps for simulation

    def simulate_stock_price(self):
        # We solve the following stochastic differential equation for the price of an asset in the Ito sense:
        # dS = r * S * dt + sigma * S * dW
        # We define Y = ln(S), then we have dY = (r - 0.5 * sigma^2) * dt + sigma * dW (Using Ito's lemma)
        # We can simulate the process using the Euler-Maruyama method
        #Y_(t) = Y_(-1) + (r - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * Z, where Z ~ N(0,1)
        #The price of the asset at time t is then given by S_t = exp(Y_t)

        dt = self.T / self.num_steps
        asset_prices = np.zeros(self.num_steps)
        call_prices = np.zeros(self.num_steps)
        put_prices = np.zeros(self.num_steps)

        asset_prices[0] = self.S0
        call_prices[0] = self.call_price(asset_prices[0])
        put_prices[0] = self.put_price(asset_prices[0])

        for t in range(1, self.num_steps):
            z = np.random.standard_normal() 
            asset_prices[t] = asset_prices[t - 1] * np.exp((self.r - 0.5 * self.sigma ** 2) * dt + self.sigma * np.sqrt(dt) * z)
            call_prices[t] = self.call_price(asset_prices[t])
            put_prices[t] = self.put_price(asset_prices[t])

        self.call_prices = call_prices
        self.put_prices = put_prices
        self.asset_prices = asset_prices   

    def d1(self, S=None):
        if S is None:
            S = self.S0
        return (np.log(S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))

    def d2(self, S=None):
        if S is None:
            S = self.S0
        return self.d1(S) - self.sigma * np.sqrt(self.T)

    def call_price(self, S=None):
        if S is None:
            S = self.S0
        d1 = self.d1(S)
        d2 = self.d2(S)
        return (S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2))

    def put_price(self, S=None):
        if S is None:
            S = self.S0
        d1 = self.d1(S)
        d2 = self.d2(S)
        return (self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - S * norm.cdf(-d1))
    
class monteCarloOptionPricing(BlackScholes):
    def __init__(self, S0, K, T, r, sigma):
        super().__init__(S0, K, T, r, sigma)
    
    def monte_carlo_option_price(self, num_simulations=100):
        call_prices = np.zeros((num_simulations, self.num_steps))
        put_prices = np.zeros((num_simulations, self.num_steps))
        asset_prices = np.zeros((num_simulations, self.num_steps))
        for i in range(num_simulations):
            print(f"Simulation {i + 1}/{num_simulations}")
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
    

    s = np.linspace(0, 2*S0, 1000)
    mu = np.log(S0) + (r - 0.5 * sigma ** 2) * T
    scale = sigma * np.sqrt(T)
    expected_distribution = lognorm.pdf(s, s=scale, scale=np.exp(mu))

    bs = monteCarloOptionPricing(S0, K, T, r, sigma)
    asset_prices, call_prices, put_prices = bs.monte_carlo_option_price(num_simulations=100)
    # We make a histogram of the last column of the asset prices to see the distribution of the stock price at maturity
    # this should be compatible with a lognormal distribution
    #P(S_t = s) = (1/(s * sigma * sqrt(2 * pi * t))) * exp(-(ln(s/S0) - (r - 0.5 * sigma^2) * t)^2 / (2 * sigma^2 * t)))

    plt.figure(figsize=(12, 6))
    plt.hist(call_prices[:, -1], bins=30, alpha=0.7, color='blue', label='Stock Price Distribution', density=True)
    #plt.plot(s, expected_distribution, color='red', label='Expected Lognormal Distribution')
    plt.title('Distribution of Stock Prices at Maturity')
    plt.xlabel('Stock Price')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid()
    plt.show()

    '''
    #we an histogram of the last price of the asset prices to see the distribution of the stock price at maturity
    plt.figure(figsize=(12, 6))
    plt.hist(bs.asset_prices[-100:], bins=30, alpha=0.7, color='blue', label='Stock Price Distribution')
    plt.title('Distribution of Stock Prices at Maturity')
    plt.xlabel('Stock Price')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid()
    plt.show()
    #plt.plot(bs.asset_prices, label='Stock Price', color='blue')
    plt.plot(bs.call_prices, label='Call Option Price', color='green')
    plt.plot(bs.put_prices, label='Put Option Price', color='red')
    # We plot the standard deviation as a shaded area around the mean price
    plt.fill_between(range(len(bs.call_prices)), bs.call_prices - bs.std_call_prices, bs.call_prices + bs.std_call_prices, color='green', alpha=0.2)
    #plt.fill_between(range(len(bs.put_prices)), bs.put_prices - bs.std_put_prices, bs.put_prices + bs.std_put_prices, color='red', alpha=0.2)
    plt.title('Option Prices Over Time')
    plt.xlabel('Time Steps')
    plt.ylabel('Option Price')

    plt.legend()
    plt.show()

    print(f"Call Option Price: {bs.call_price():.2f}")
    print(f"Put Option Price: {bs.put_price():.2f}")

    #bs.plot_stock_price(num_steps=1000)
    '''
