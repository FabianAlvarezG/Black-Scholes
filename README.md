# Black-Scholes

Some years ago I attended the DPG Spring Meeting, where I went to a talk in which I was first exposed to the use of physics (or, more precisely, mathematics) in finance. The talk was terrible and I didn't really understand anything. The only thing I remember was the speaker ranting against the Black-Scholes equation. I had never heard of it before, so I googled it and found out about options trading. I had heard about options in the past, but to me they were an abstract financial instrument invented just for the sake of speculation, without any intrinsic value. I have since changed my opinion about them, and decided to write down my thoughts and what I have learned recently.

## Options

According to Wikipedia, an option is a contract between a buyer and a seller in which the buyer obtains the right, but not the obligation, to buy or sell a specific amount of an asset at a specific price (the strike price) at a specific time in the future. If the buyer has the right to buy, it is called a call option. If the buyer has the right to sell, it is called a put option. For this right, the buyer pays the seller a price today, the option premium.

What price an option should have? If I was a call option, I don't have an immediate intuitive answer. After thinking a little bit (and cheating by reading about it) a fair price should offer the buyer and expected return of 0 (They might still have the chance of winning or loosing what he payed when they do not execute the option). This was the idea of french mathematician Louis Bachelier more than a century ago. Now, following the same spirit we have the Black-Scholes equation, the expected return under risk neutral condition should be zero.

It took me a while to understand what that sentence actually means. Before proceeding lets introduce some concepts, let be $K$ be the agreed price on the option, i.e. the strike price, $T$ be the expiration date and $r$ the interest rate of some safe asset, like a government bond. Risk neutral condition is to assume that the drift the underlying asset, let's say bananas, is driven by the risk-free interest rate $r$. In other words, we assume the price of an asset follows the following stochastic differential equation

$d S_t = r S dt + \sigma S d W_t$ ,

where $dW_t\sim \mathcal{N}(0, dt)$ are the increments of a Wiener process. Now, the pdf of $S$ at time $T$ is given by

$p(S = s, T) = \frac{1}{s\sqrt{2\pi \sigma^2 T}}\exp\left[-\frac{\left(\log(s/S_0)  - \left(r - \tfrac{1}{2}\sigma^2\right) T\right)^2}{2\sigma^2 T}\right]$

Where $S_0$ is the initial price. At expiration date, an option is exactly worth is payoff. Let $C(S,t)$ be the price of the option. At $t =T$ we must have

$C(S,T) = \max(S-K, 0)$

The price $C_0$ I paid at $t =0$ is worth $C_0\exp(r T)$ by the expiration date. So, Black-Scholes model tell me that the price of an option with the price of the asset with drift $r$ should be such that the expected revenue should be $0$, namely

$E^Q[\max(S_T-K, 0)] -C_0\exp(r T) = 0$ 

Solving this equation gives the price today of the option. We can compute this expected value using the $p(S = s, T)$.

