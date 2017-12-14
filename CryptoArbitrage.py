import requests
import json
import time
import datetime

# the target threshold for determining whether or not a spread is attractive
SPREAD_THRESHOLD = 1000.0

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

#returns the JSON of the data at url
def getJSON(url):
	request = requests.get(url)
	json_string = request.text
	#print(json_string)
	return json.loads(json_string)

#add seconds to a time
def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()

if __name__ == "__main__":
	## use the following code if we want to stop running after a certain point. Electricity/hydro concerns?
	#start = datetime.datetime.now().time()
	#end = addSecs(start, 10)
	#while datetime.datetime.now().time() < end:
	while True:
		print('\nCurrent Time: '+str(datetime.datetime.now())+'------------------------------------------')
		# initialize exchanges and put into a list
		quadriga = QuadrigaExchange()
		bittrex = BittrexExchange()
		kraken = KrakenExchange()
		poloniex = PoloniexExchange()

		exchanges = [quadriga,bittrex,kraken,poloniex]

		# dictionary to store spreads that meet the desired threshold SPREAD_THRESHOLD
		attractiveSpreads = {}

		# get spread for each exchange, and compare it's ask to the bid of every other exchange
		for exchange in exchanges:
			#print(str(exchange.parsed_json)) # view raw data for QA
			print('\n------------------------'+exchange.name+'------------------------')
			ask = exchange.getAsk()
			bid = exchange.getBid()
			print('Asking Price (USD for BTC): '+str(ask))
			print('Bid Price (USD for BTC): '+str(bid))
			spread = ask-bid
			print('    Bid-to-Ask (Ask - Bid) Spread (USD for BTC): '+str(spread))

			if(spread >= SPREAD_THRESHOLD):
				attractiveSpreads[exchange.name] = spread

			otherExchanges = list(exchanges)
			otherExchanges.remove(exchange)

			print('\n    Compared to other exchanges:')
			for otherExchange in otherExchanges:
				otherBid = otherExchange.getBid()
				print('        '+otherExchange.name+' Bid Price (USD for BTC): '+str(otherBid))
				comparativeSpread = ask-otherBid
				print('            '+exchange.name+' Ask to '+otherExchange.name+' Bid Spread (USD for BTC): '+str(comparativeSpread))

				if(comparativeSpread >= SPREAD_THRESHOLD):
					attractiveSpreads[exchange.name+'-'+otherExchange.name] = comparativeSpread

		print('\nThe following spreads have been deemed attractive:')
		for attractiveSpread in attractiveSpreads:
			print('    Exchange(s): '+attractiveSpread+' Spread: '+str(attractiveSpreads[attractiveSpread]))
		# repeat
		time.sleep(10)
