import argparse
import json
import re
from flask import Flask, render_template, request, jsonify
import requests
import nltk
from nltk.tokenize import word_tokenize

app = Flask(__name__)

# Hardcoded crypto database
crypto_db = {
    'bitcoin': {
        'name': 'Bitcoin',
        'symbol': 'BTC',
        'price_trend': 'bullish',
        'market_cap': 'high',
        'energy_use': 'high',
        'sustainability_score': 2
    },
    'ethereum': {
        'name': 'Ethereum',
        'symbol': 'ETH', 
        'price_trend': 'bullish',
        'market_cap': 'high',
        'energy_use': 'medium',
        'sustainability_score': 6
    },
    'cardano': {
        'name': 'Cardano',
        'symbol': 'ADA',
        'price_trend': 'stable',
        'market_cap': 'medium',
        'energy_use': 'low',
        'sustainability_score': 9
    }
}

# Download NLTK data
try:
    nltk.download('punkt', quiet=True)
except:
    pass

def get_live_prices():
    """Fetch live prices from CoinGecko API"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,cardano',
            'vs_currencies': 'usd'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {}

def analyze_intent(query):
    """Simple NLP to analyze user intent"""
    try:
        tokens = word_tokenize(query.lower())
    except:
        tokens = query.lower().split()
    
    eco_keywords = ['eco', 'green', 'environment', 'sustainable', 'clean', 'friendly']
    growth_keywords = ['growth', 'gain', 'profit', 'long-term', 'invest', 'future']
    price_keywords = ['price', 'cost', 'value', 'expensive', 'cheap']
    
    if any(word in tokens for word in eco_keywords):
        return 'sustainability'
    elif any(word in tokens for word in growth_keywords):
        return 'growth' 
    elif any(word in tokens for word in price_keywords):
        return 'price'
    else:
        return 'general'

def get_recommendation(intent, live_prices):
    """Generate recommendation based on intent"""
    disclaimer = " ⚠️ Crypto is risky — always do your own research (DYOR)!"
    
    if intent == 'sustainability':
        crypto = crypto_db['cardano']
        price_info = ""
        if live_prices and 'cardano' in live_prices:
            price_info = f" (Current price: ${live_prices['cardano']['usd']:.4f})"
        return f"For eco-friendly crypto, I recommend {crypto['name']}! It has a high sustainability score of {crypto['sustainability_score']}/10 with low energy use.{price_info}{disclaimer}"
    
    elif intent == 'growth':
        crypto = crypto_db['cardano']
        price_info = ""
        if live_prices and 'cardano' in live_prices:
            price_info = f" (Current price: ${live_prices['cardano']['usd']:.4f})"
        return f"{crypto['name']} looks solid for long-term growth with its {crypto['price_trend']} trend and {crypto['market_cap']} market cap.{price_info}{disclaimer}"
    
    elif intent == 'price':
        prices = []
        for coin_id, coin_data in crypto_db.items():
            price_info = "Price unavailable"
            if live_prices and coin_id in live_prices:
                price_info = f"${live_prices[coin_id]['usd']:.4f}"
            prices.append(f"{coin_data['name']}: {price_info}")
        return f"Current prices: {', '.join(prices)}.{disclaimer}"
    
    else:
        return f"I can help you find green and growing cryptos! Try asking about eco-friendly coins, growth potential, or current prices.{disclaimer}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('message', '')
    if not user_query:
        return jsonify({'response': f"Please ask me something about crypto!⚠️ Crypto is risky — always do your own research (DYOR)!"})
    
    live_prices = get_live_prices()
    intent = analyze_intent(user_query)
    response = get_recommendation(intent, live_prices)
    
    return jsonify({'response': response})

def cli_mode():
    """CLI fallback mode"""
    print("🌱🚀 CryptoBuddy CLI Mode - Hey there! Let's find you a green and growing crypto! 🌱🚀")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Thanks for using CryptoBuddy! 👋")
            break
        
        if user_input:
            live_prices = get_live_prices()
            intent = analyze_intent(user_input)
            response = get_recommendation(intent, live_prices)
            print(f"CryptoBuddy: {response}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CryptoBuddy - Your friendly crypto helper')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    args = parser.parse_args()
    
    if args.cli:
        cli_mode()
    else:
        print("🌱🚀 Starting CryptoBuddy web server...")
        app.run(debug=True, port=5000)
