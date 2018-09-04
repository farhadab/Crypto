# for email
SENDER_ADDRESS = 'username@gmail.com'
SENDER_PASSWORD = 'password'
SENDER_SMTP_HOST = 'smtp.gmail.com'
SENDER_SMTP_PORT = 587 # default 0
RECIPIENT_ADDRESS = 'email@address.com'

# the target threshold for determining whether or not a spread is attractive
SPREAD_THRESHOLD = 70.0
# If below, send email every TARGET_PRICE_INTERVAL seconds
TARGET_PRICE_BITCOIN = 8000
TARGET_PRICE_EMAIL_INTERVAL = 600 #seonds
# Or send email every TARGET_PRICE_DEFAULT seconds regardless of price
EMAIL_INTERVAL_DEFAULT = 10800