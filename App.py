import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm
from numpy import exp
import matplotlib.pyplot as plt
import seaborn as sns
import qfin as qf

# Page config
st.set_page_config(
    page_title="The Black Scholes Option Pricing Model",
    layout="wide",
    initial_sidebar_state="expanded")


# CSS for the call and put containers
st.markdown("""
<style>

.top-right-container {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 999; /* Ensure it's above other elements */
}

.container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px; /* Height of container */
    width: auto;
    margin: 0 auto; /* Center the container */
}

.call {
    background-color: #27A567; /* Light green */
    color: black; /* Font color */
    border-radius: 10px;
}

.put {
    background-color: #FF474C; /* Light red */
    color: black; /* Font color */
    border-radius: 10px;
}


/* Style for the text */
.h2 {
    font-size: 1.5rem; 
    font-weight: bold;
    margin: 0;
}

</style>
""", unsafe_allow_html=True)

class BlackScholes:
    def __init__(
        self,
        time_to_maturity: float,
        strike: float,
        current_price: float,
        volatility: float,
        risk_free_rate: float,
    ):
        self.time_to_maturity = time_to_maturity
        self.strike = strike
        self.current_price = current_price
        self.volatility = volatility
        self.risk_free_rate = risk_free_rate
        
    # Calculate the call and put prices    
    
    def calculate_prices(self):
        t = self.time_to_maturity
        K = self.strike
        S = self.current_price
        sigma = self.volatility
        r = self.risk_free_rate
        
        d1 = (np.log(S/K) + (r + ((sigma**2)/2))*t) / (sigma * np.sqrt(t))
        d2 = d1 - (sigma * np.sqrt(t))

        call_price = S * norm.cdf(d1) - (strike * exp(-(r * t)) * norm.cdf(d2))
        put_price = (strike * exp(-(r * t)) * norm.cdf(-d2)) - S * norm.cdf(-d1)

        self.call_price = call_price
        self.put_price = put_price

        return call_price, put_price


# Sidebar for User Inputs
with st.sidebar:
    st.title("Black Scholes Model")

    current_price = st.number_input("Current Asset Price", value=100.0, step=1.0)
    strike = st.number_input("Strike Price", value=100.0, step=1.0)
    time_to_maturity = st.number_input("Time to Maturity (Years)", value=1.0)
    volatility = st.number_input("Volatility", value=0.3)
    risk_free_rate = st.number_input("Risk-Free Interest Rate", value=0.05)

    st.markdown("---")
    st.markdown("")
    
    calculate_btn1 = st.button('Calculate Heatmap')
    min_spot = st.number_input('Min Spot Price', min_value=0.1, value=current_price*0.8, step=1.0)
    max_spot = st.number_input('Max Spot Price', min_value=0.1, value=current_price*1.2, step=1.0)
    min_vol = st.slider('Min Volatility for Heatmap', min_value=0.01, max_value=1.0, value=volatility*0.5, step=0.01)
    max_vol = st.slider('Max Volatility for Heatmap', min_value=0.01, max_value=1.0, value=volatility*1.5, step=0.01)
    
    spot_range = np.linspace(min_spot, max_spot, 10)
    vol_range = np.linspace(min_vol, max_vol, 10)
    
    market_call_quote = st.number_input('Market call quote', min_value=0.1, value=14.1, step=0.1)
    market_put_quote = st.number_input('Market put quote', min_value=0.1, value=9.2, step=0.1)
    

    st.markdown("---")
    st.markdown("")
    
    calculate_btn2 = st.button('Calculate Account Equity')
    num_iterations = st.number_input('Number of Trades (Max 25000)', min_value=5, value=8500, step=100 , max_value=25000)
    amount_brought = st.number_input('Amount of options', min_value=1, value=100, step=10)
    time_steps = st.number_input('Time Steps', min_value=1, value=252, step=20)


# Plot profit and loss heatmaps
def plot_heatmap(bs_model, spot_range, vol_range, strike):
    
    call_prices = np.zeros((len(vol_range), len(spot_range)))
    put_prices = np.zeros((len(vol_range), len(spot_range)))
    
    for i, vol in enumerate(vol_range):
        for j, spot in enumerate(spot_range):
            bs_temp = BlackScholes(
                time_to_maturity=bs_model.time_to_maturity,
                strike=strike,
                current_price=spot,
                volatility=vol,
                risk_free_rate=bs_model.risk_free_rate
            )
            bs_temp.calculate_prices()
            call_prices[i, j] = bs_temp.call_price - market_call_quote
            put_prices[i, j] = bs_temp.put_price - market_put_quote

    # Plotting Call Price PNL Heatmap
    plt.style.use('dark_background')
    fig_call, ax_call = plt.subplots(figsize=(10, 8))
    sns.heatmap(call_prices, xticklabels=np.round(spot_range, 2), 
                yticklabels=np.round(vol_range, 2), annot=True, fmt=".2f",
                cmap="RdYlGn", ax=ax_call)
    ax_call.set_title('CALL P&L')
    ax_call.set_xlabel('Spot Price')
    ax_call.set_ylabel('Volatility')
    
    # Plotting Put Price PNL Heatmap
    fig_put, ax_put = plt.subplots(figsize=(10, 8))
    sns.heatmap(put_prices, xticklabels=np.round(spot_range, 2), 
                yticklabels=np.round(vol_range, 2), annot=True, fmt=".2f",
                cmap="RdYlGn", ax=ax_put)
    ax_put.set_title('PUT P&L')
    ax_put.set_xlabel('Spot Price')
    ax_put.set_ylabel('Volatility')
    
    return fig_call, fig_put

# Plot account equity graph
def plot_account_equity(bs_model, num_iterations):
    pls = []
    expected_value, _ = bs_model.calculate_prices()
    premium = market_call_quote * amount_brought
    for i in range(num_iterations):
        path = qf.simulations.GeometricBrownianMotion(current_price, risk_free_rate, volatility, 1/time_steps, bs_model.time_to_maturity)
        pls.append(max(path.simulated_path[-1] - current_price, 0)*amount_brought - premium)
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(np.cumsum(pls), label="Account Equity", color="cyan")
    ax.set_title(f"Trading this Edge ({round(expected_value, 2)} - {round(market_call_quote, 2)}) Over Time")
    ax.set_xlabel("Number of Option Trades")
    ax.set_ylabel("Portfolio Value")
    ax.legend()

    return fig


st.write("`Created by:`")
linkedin_url = "https://www.linkedin.com/in/harrison-hawkins-395844328/"
st.markdown(f"""<a href="{linkedin_url}" target="_blank" style="text-decoration: 
none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" 
width="25" height="25" style="vertical-align: middle; margin-right: 10px;
position: absolute; top: 0px; left: 7vw; z-index: 999">`Harrison Hawkins`</a>""", 
unsafe_allow_html=True)

# Main Page for Output Display
st.title("The Black Scholes Pricing Model")
st.markdown("")
st.info("""The Black-Scholes Model is a well-known method for estimating the 
price of European options. It’s based on the idea that markets are efficient 
and that the price of an asset moves in a continuous, predictable way with 
constant volatility and interest rates. The model is widely used 
and is a helpful tool for hedging and understanding how options are priced. 
That said it does have its limitations. It assumes conditions that aren’t 
always realistic like constant volatility and doesn’t work well for American 
ptions or situations where early exercise is possible. It can also produce 
inaccurate results during times of market stress or when the underlying asset 
pays large dividends.""")

st.markdown("")
st.markdown("")

# Calculate Call and Put values
bs_model = BlackScholes(time_to_maturity, strike, current_price, volatility, risk_free_rate)
call_price, put_price = bs_model.calculate_prices()


# Display Call and Put Values in colored tabs.
tab1, tab2 = st.tabs(["📈 Call Option", "📉 Put Option"])
st.markdown("")
st.markdown("")

with tab1:
    st.markdown(f"""
        <div class="container call">
            <div>
                <div>CALL Value</div>
                <div class="h2">${call_price:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown(f"""
        <div class="container put">
            <div>
                <div>PUT Value</div>
                <div class="h2">${put_price:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
input_data = {
    "Current Asset Price": [current_price],
    "Strike Price": [strike],
    "Time to Maturity (Years)": [time_to_maturity],
    "Volatility (σ)": [volatility],
    "Risk-Free Interest Rate": [risk_free_rate],
}
input_df = pd.DataFrame(input_data)
st.dataframe(input_df)


st.markdown("")
st.title("Options Price - Heatmaps")
st.info("""These heatmaps display the Profit and Loss (P&L) call and put 
options across a range of spot prices and volatility levels at expiry. 
The horizontal axis represents the spot price of the underlying asset, while 
the vertical axis shows the volatility. Each point on the heatmap reflects the 
option’s payoff minus the premium paid, with the color intensity indicating the
magnitude of profit or loss. As spot prices and volatility shift, the value 
of the option changes, capturing how market movements and uncertainty impact 
option outcomes. """)
st.markdown("")

# Columns to store PNL Heatmaps side by side
col1, col2 = st.columns([1,1], gap="small")
with col1:
    st.subheader("Call Price Heatmap")
    heatmap_fig_call, _ = plot_heatmap(bs_model, spot_range, vol_range, strike)
    st.pyplot(heatmap_fig_call)

with col2:
    st.subheader("Put Price Heatmap")
    _, heatmap_fig_put = plot_heatmap(bs_model, spot_range, vol_range, strike)
    st.pyplot(heatmap_fig_put)


st.markdown("")
st.title("Account Equity - Interactive")
st.info("""Explore how trading this strategy with a theoretical trade edge 
(Black Scholes Call Value - Market Quote)  impacts long term account equity
this uses a geometric brownian motion to sample different possible positions a 
individual trade could end in, up this means each time you recalculate there
should be a different account equity even if the model parameters are the same. 
Try adjusting and recalculating with different edges also try with varying 
amounts of trades.""")
st.markdown("")

st.subheader("Account Equity")
account_equity_call = plot_account_equity(bs_model, num_iterations)
st.pyplot(account_equity_call)


    
