import requests
import json
import time
import datetime
import sendemail as se
from config import (
					SPREAD_THRESHOLD,
					TARGET_PRICE_BITCOIN,
					TARGET_PRICE_EMAIL_INTERVAL,
					EMAIL_INTERVAL_DEFAULT
					)

SUPPORTED_EXCHANGES = [
	'Quadriga',
	'Bittrex',
	'Kraken',
	'Poloniex',
	'Binance',
	'Gemini'
]

class Exchange:
	def __init__(self, name, quoteURL, quoteBook):
		self.name = name
		self.quoteURL = quoteURL
		self.quoteBook = quoteBook
		self.parsed_json = getJSON(self.quoteURL)

class QuadrigaExchange(Exchange):
	#https://www.quadrigacx.com/api_info
	def __init__(self):
		super(QuadrigaExchange, self).__init__("Quadriga", "https://api.quadrigacx.com/v2/ticker?book=btc_usd", None)
		
	def getAsk(self):
		return float(self.parsed_json['ask'])
		
	def getBid(self):
		return float(self.parsed_json['bid'])

class BittrexExchange(Exchange):
	#https://bittrex.com/home/api
	#https://bittrex.com/api/v1.1/public/getmarkets #gets you the market parameter values
	#https://bittrex.com/api/v1.1/public/getcurrencies #gets you the currencies, including fee
	#	USDT - tether?
	def __init__(self):
		super(BittrexExchange, self).__init__("Bittrex", "https://bittrex.com/api/v1.1/public/getticker?market=usdt-btc", None)
		
	def getAsk(self):
		return float(self.parsed_json['result']['Ask'])
		
	def getBid(self):
		return float(self.parsed_json['result']['Bid'])

class KrakenExchange(Exchange):
	#https://www.kraken.com/help/api
	#https://api.kraken.com/0/public/AssetPairs #gets you the pair parameter values and the fees
	# <pair_name> = pair name
 	#    a = ask array(<price>, <whole lot volume>, <lot volume>),
 	#    b = bid array(<price>, <whole lot volume>, <lot volume>),
 	#    c = last trade closed array(<price>, <lot volume>),
 	#    v = volume array(<today>, <last 24 hours>),
 	#    p = volume weighted average price array(<today>, <last 24 hours>),
 	#    t = number of trades array(<today>, <last 24 hours>),
 	#    l = low array(<today>, <last 24 hours>),
 	#    h = high array(<today>, <last 24 hours>),
 	#    o = today's opening price
	def __init__(self):
		super(KrakenExchange, self).__init__("Kraken", "https://api.kraken.com/0/public/Ticker?pair=XBTUSD", None)
		
	def getAsk(self):
		return float(self.parsed_json['result']['XXBTZUSD']['a'][0])
		
	def getBid(self):
		return float(self.parsed_json['result']['XXBTZUSD']['b'][0])

class PoloniexExchange(Exchange):
	#https://poloniex.com/support/api/
	#returnTicker returns all asset pairs, will need to parse
	def __init__(self):
		super(PoloniexExchange, self).__init__("Poloniex", "https://poloniex.com/public?command=returnTicker", None)
		
	def getAsk(self):
		return float(self.parsed_json['USDT_BTC']['lowestAsk'])
		
	def getBid(self):
		return float(self.parsed_json['USDT_BTC']['highestBid'])

class BinanceExchange(Exchange):
	#https://support.binance.com/hc/en-us/articles/115000840592-Binance-API-Beta
	def __init__(self):
		super(BinanceExchange, self).__init__("Binance", "https://api.binance.com/api/v1/depth?symbol=BTCUSDT", None)
		
	def getAsk(self):
		return float(self.parsed_json['asks'][0][0])
		
	def getBid(self):
		return float(self.parsed_json['bids'][0][0])

class GeminiExchange(Exchange):
	#https://docs.gemini.com/rest-api/
	def __init__(self):
		super(GeminiExchange, self).__init__("Gemini", "https://api.gemini.com/v1/book/btcusd", None)
		
	def getAsk(self):
		return float(self.parsed_json['asks'][0]['price'])
		
	def getBid(self):
		return float(self.parsed_json['bids'][0]['price'])


#coinSquare's out for now because their API is too annoying to work with. Specifically, their USD/BTC ask/bids are often empty
	#https://classic.coinsquare.io/?method=img&tag=RESZFAQ
	#https://coinsquare.io/api/v1/data/quotes

#returns the JSON of the data at url
def getJSON(url):
	json_string = ''
	pased_json = None
	try:
		request = requests.get(url)
		json_string = request.text
		#print(json_string)
		pased_json = json.loads(json_string)
	except:
		print('Did not receive a response from '+url)
	return pased_json


#add seconds to a time
def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()


# send email alert if ask of exchange is less than or equal to threshold
def ask_alert(exchange_name, threshold, send_email=False):
	exchange = get_exchange_from_name(exchange_name)
	exchange_ask = exchange.getAsk()
	message = exchange.name+' ask is '+str(exchange_ask)
	print('\n'+message)

	if exchange_ask <= threshold or send_email:
		print('Sending email')
		se.send_email(message, message)


# return exchange object from name
def get_exchange_from_name(exchange_name):
	exchange = None
	# todo: make this dynamic...
	if exchange_name == 'Quadriga':
		exchange = QuadrigaExchange()
	elif exchange_name == 'Bittrex':
		exchange = BittrexExchange()
	elif exchange_name == 'Kraken':
		exchange = KrakenExchange()
	elif exchange_name == 'Poloniex':
		exchange = PoloniexExchange()
	elif exchange_name == 'Binance':
		exchange = BinanceExchange()
	elif exchange_name == 'Gemini':
		exchange = GeminiExchange()
	return exchange


# compare our exchanges and print results
def compare_exchanges():
	print('\nCurrent Time: '+str(datetime.datetime.now())+'------------------------------------------')
	print('\nComparing exchange prices...')
	# initialize exchanges and put into a list
	exchanges = [get_exchange_from_name(exchange_name) for exchange_name in SUPPORTED_EXCHANGES]

	# dictionary to store spreads that meet the desired threshold SPREAD_THRESHOLD
	attractiveSpreads = {}
	# initialize the lowest/highest
	lowestAskExchange = exchanges[0]
	highestBidExchange = exchanges[0]

	# get spread for each exchange, and compare it's ask to the bid of every other exchange
	for exchange in exchanges:
		try:
			#print(str(exchange.parsed_json)) # view raw data for QA
			#want to maximize the spread between buying price (ask) and selling price (bid), i.e. buy low, sell high
			print('\n------------------------'+exchange.name+'------------------------')
			ask = exchange.getAsk()
			bid = exchange.getBid()
			print('Asking (buy) Price (USD for BTC): '+str(ask))
			print('Bid (sell) Price (USD for BTC): '+str(bid))
			spread = bid-ask
			print('\tBid-to-Ask (Bid - Ask) Spread (USD for BTC): '+str(spread))

			if(spread >= SPREAD_THRESHOLD):
				attractiveSpreads[exchange.name] = spread

			otherExchanges = list(exchanges)
			otherExchanges.remove(exchange)

			print('\n\tCompared to other exchanges:')
			for otherExchange in otherExchanges:
				try:
					otherBid = otherExchange.getBid()
					print('\t\t'+otherExchange.name+' Bid Price (USD for BTC): '+str(otherBid))
					comparativeSpread = otherBid-ask
					print('\t\t\t'+otherExchange.name+' Bid to '+exchange.name+' Ask Spread (USD for BTC): '+str(comparativeSpread))

					if(comparativeSpread >= SPREAD_THRESHOLD):
						attractiveSpreads[exchange.name+' (buy) '+'- '+otherExchange.name+' (sell)'] = comparativeSpread
				except:
					print('\t\tCould not retrieve data for '+otherExchange.name)

			# update lowest/highest
			if(ask < lowestAskExchange.getAsk()):
				lowestAskExchange = exchange
			if(bid > highestBidExchange.getBid()):
				highestBidExchange = exchange
		except:
			print('Could not retrieve data for '+exchange.name)

	# print our results
	if len(attractiveSpreads) == 0:
		print('\nNo spreads found to be attractive at threshold of '+str(SPREAD_THRESHOLD))
	else:
		print('\nThe following attractive spreads have been found given threshold of :'+str(SPREAD_THRESHOLD))
		for attractiveSpread in attractiveSpreads:
			print('    Exchange(s): '+attractiveSpread+' Spread: '+str(attractiveSpreads[attractiveSpread]))

	# regardless of threshold results, show best available
	print('\nThe lowest ask (best place to buy) is '+str(lowestAskExchange.getAsk())+' ('+lowestAskExchange.name+')')
	print('The highest bid (best place to sell) is '+str(highestBidExchange.getBid())+' ('+highestBidExchange.name+')')


# set up an ask alert for Bitcoin on Quadriga
def bitcoin_quadriga_ask_alert(target_price, interval, interval_default):
	print('\nCurrent Time: '+str(datetime.datetime.now())+'------------------------------------------')
	print('\nCreating alert for Bitcoin on Quadriga...')
	seconds = 0
	while True:
		# set alert for quadriga
		ask_alert('Quadriga', target_price)

		# send alert periodically
		if seconds == interval_default:
			ask_alert('Quadriga', target_price, True)
			seconds = 0
		else:
			seconds += interval

		print('Sleeping for '+str(seconds)+' seconds...')
		# repeat
		time.sleep(interval)


if __name__ == "__main__":
	compare_exchanges()
	bitcoin_quadriga_ask_alert(TARGET_PRICE_BITCOIN, 
								TARGET_PRICE_EMAIL_INTERVAL, 
								EMAIL_INTERVAL_DEFAULT)
