from binance.client import Client
import talib
import os

# Config
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
client = Client(API_KEY, API_SECRET)

def execute_trade(tv_signal):
    symbol = tv_signal['symbol']  # Contoh: 'BTCUSDT'
    action = tv_signal['action']  # 'buy' atau 'sell'
    
    # Konfirmasi dengan indikator lokal
    df = get_data(symbol)
    if confirm_signal(df, action):
        place_order(symbol, action)

def get_data(symbol):
    klines = client.futures_klines(symbol=symbol, interval='1h', limit=100)
    df = pd.DataFrame(klines, columns=['timestamp','open','high','low','close','volume','close_time','quote_volume','trades','taker_buy_base','taker_buy_quote','ignore'])
    df['close'] = pd.to_numeric(df['close'])
    return df

def confirm_signal(df, action):
    # Konfirmasi dengan EMA dan RSI
    df['ema_50'] = talib.EMA(df['close'], timeperiod=50)
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    
    last_close = df['close'].iloc[-1]
    
    if action == 'buy':
        return (last_close > df['ema_50'].iloc[-1]) and (df['rsi'].iloc[-1] > 50)
    else:
        return (last_close < df['ema_50'].iloc[-1]) and (df['rsi'].iloc[-1] < 50)

def place_order(symbol, side):
    price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
    qty = calculate_position_size(price)
    
    client.futures_create_order(
        symbol=symbol,
        side=side.upper(),
        type='MARKET',
        quantity=qty
    )
