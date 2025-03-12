This repository contains a Python-based cryptocurrency trading analysis tool built with the CCXT library for Coinbase, targeting the ETH/USD pair. The script fetches recent trades, filters large transactions, and tracks them over a 4-hour window to calculate buy/sell percentages and infer market sentiment (LONG, SHORT, or NEUTRAL). It also retrieves historical OHLCV data to train a linear regression model for predicting the next price, displaying results alongside the current price. The program runs in a loop, refreshing every 5 seconds. Dependencies include pandas, numpy, and scikit-learn.
<img width="676" alt="Screenshot 2025-03-11 at 9 03 16 PM" src="https://github.com/user-attachments/assets/41827ddd-e627-4531-a786-396f52b799c9" />
<img width="676" alt="Screenshot 2025-03-11 at 9 03 16 PM" src="https://github.com/user-attachments/assets/63546a84-87f2-48f2-b2dc-abc4eef52de3" />


