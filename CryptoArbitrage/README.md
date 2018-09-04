# Crypto Arbitrage

Used to compare the spread of Bitcoin on different crypto exchanges and present attractive ones (given `SPREAD_THRESHOLD`), along with the best spread available, regardless. 

Sends an email alert if the quadriga price is at or below a given `TARGET_PRICE_BITCOIN`. Keeps sending emails every `TARGET_PRICE_EMAIL_INTERVAL` seconds so long as the price remains at/below the threshold, or if it's not, it will still send every `EMAIL_INTERVAL_DEFAULT` seconds.

## Config
An example config, `config_example.py`, has been provided. Must update to your liking and rename to just `config.py`.