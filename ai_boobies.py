import ccxt
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Initialize the exchange
exchange = ccxt.coinbase()

# Specify the symbol to monitor
symbol = 'ETH/USD'

# List to store trades for the last 4 hours
recent_trades = []

# Function to fetch historical price data
def fetch_historical_data(symbol, timeframe='1m', limit=100):
    try:
        # Fetch historical data from the exchange
        since = exchange.parse8601((datetime.now() - timedelta(minutes=limit)).isoformat())
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        return pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    except Exception as e:
        print(f"An error occurred while fetching historical data: {e}")
        return pd.DataFrame()

# Function to train a predictive model
def train_model(df):
    # Prepare data for training
    df['price_change'] = df['close'].pct_change()
    df = df.dropna()
    
    # Features (X) and target (y)
    X = np.array(range(len(df))).reshape(-1, 1)  # Use index as feature
    y = df['close'].values

    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)
    return model

# Function to make predictions
def predict_next_price(model, current_price):
    current_index = len(recent_trades)  # Use current length as index for prediction
    predicted_price = model.predict(np.array([[current_index]]))
    return predicted_price[0]

# Function to fetch and display recent trades over a threshold
def fetch_large_trades(symbol, threshold=0):
    global recent_trades
    try:
        # Fetch recent trades
        trades = exchange.fetch_trades(symbol)
        # Filter and display trades over the threshold
        large_trades = [trade for trade in trades if trade['amount'] > threshold]
        # Sort trades by timestamp in descending order
        large_trades.sort(key=lambda x: x['timestamp'], reverse=False)
        for i, trade in enumerate(large_trades):
            # Convert timestamp to human-readable format
            trade_time = datetime.fromtimestamp(trade['timestamp'] / 1000).strftime('%I:%M %p')
            # Highlight buys in green and sells in red
            color_code = '\033[92m' if trade['side'] == 'buy' else '\033[91m'  # Green for buys, red for sells
            print(f"{color_code}Time: {trade_time}, Price: {trade['price']}, Amount: {trade['amount']}, Side: {trade['side']}\033[0m")
        recent_trades.extend(large_trades)  # Add the trades to the list
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to calculate the average number of buys and sells for the last 4 hours
def calculate_avg_trades():
    global recent_trades
    # Calculate the timestamp 4 hours ago
    start_time = datetime.now() - timedelta(hours=4)
    # Filter trades within the last 4 hours
    trades_within_4_hours = [
        trade for trade in recent_trades if datetime.fromtimestamp(trade['timestamp'] / 1000) >= start_time
    ]
    total_trades = len(trades_within_4_hours)
    # Calculate the number of buys and sells
    buy_count = len([trade for trade in trades_within_4_hours if trade['side'] == 'buy'])
    sell_count = len([trade for trade in trades_within_4_hours if trade['side'] == 'sell'])
    # Calculate the percentage of buys and sells
    avg_buy_percent = (buy_count / total_trades) * 100 if total_trades > 0 else 0
    avg_sell_percent = (sell_count / total_trades) * 100 if total_trades > 0 else 0
    print(f"BUYS: {avg_buy_percent:.2f}%, SELLS: {avg_sell_percent:.2f}%")
    # Determine sentiment based on the average buys and sells
    if avg_buy_percent > avg_sell_percent:
        print("Market sentiment: LONG")
    elif avg_buy_percent < avg_sell_percent:
        print("Market sentiment: SHORT")
    else:
        print("Market sentiment: NEUTRAL")

# Function to fetch and display the current price of the asset
def fetch_current_price(symbol):
    try:
        # Fetch ticker data for the symbol
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        print(f"Current price of {symbol}: {current_price}")
        
        # Predict the next price
        historical_data = fetch_historical_data(symbol)
        if not historical_data.empty:
            model = train_model(historical_data)
            predicted_price = predict_next_price(model, current_price)
            print(f"Predicted next price: {predicted_price:.2f}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main loop to fetch trades periodically
while True:
    fetch_large_trades(symbol)
    calculate_avg_trades()
    fetch_current_price(symbol)
    time.sleep(5)  # Fetch trades every 5 seconds
