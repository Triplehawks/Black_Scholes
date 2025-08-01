# 📊 Black-Scholes Option Pricing Model

This repository offers a Python-based implementation of the Black-Scholes Model to price European call and put options, along with tools to explore the behavior of options across various market conditions. It features **interactive P&L heatmaps**, dynamic visualizations and a simulation-based analysis of **account equity** using geometric Brownian motion to predict trades.

https://blackscholestradingmodel.streamlit.app/

---

## ✨ Features

- Calculate theoretical prices for European call and put options  
- Generate **interactive heatmaps** showing option P&L across spot price and volatility ranges  
- Simulate **account equity outcomes** using multiple permutations of market movements and option strategies  
- Explore how volatility, strike price, and time to maturity influence risk and reward  
- Clean, modular Python code ready for analysis or integration  

---

## 📌 Key Components

### 🔥 Interactive Heatmaps
Explore how profit or loss changes based on different spot prices and implied volatilities. The heatmaps provide a visual way to understand option behavior, making it easier to analyze the impact of volatility shifts or directional moves in the underlying asset.

### 💼 Account Equity Simulation
Simulate many market scenarios using randomized permutations of asset price paths. Analyze the resulting distribution of account equity to evaluate potential outcomes of option positions, helping with risk management and strategy testing.

---

## 🧠 Assumptions

- The underlying asset follows **geometric Brownian motion**  
- Volatility and the risk-free rate are **constant**  
- Options are **European-style** (only exercised at expiry)  
- No dividends are paid during the option’s life  

---

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/black-scholes-model.git
   cd black-scholes-model
