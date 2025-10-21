"""
OANDA API Examples using tpqoa wrapper
"""
import pandas as pd
from oanda_trading.oanda_connection import OandaAPI

def main():
    # Initialize API connection
    api = OandaAPI()
    
    print("=" * 60)
    print("OANDA API Examples")
    print("=" * 60)
    
    # 1. Account Summary
    print("\n1. 📊 Account Summary")
    print("-" * 30)
    account_summary = api.get_account_summary()
    for key, value in account_summary.items():
        print(f"{key}: {value}")
    
    # 2. Available Instruments
    print("\n2. 🎯 Available Instruments")
    print("-" * 30)
    instruments = api.get_instruments()
    print(f"Total available instruments: {len(instruments)}")
    
    print("\nMajor Currency Pairs (technical names):")
    major_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD', 'NZD_USD']
    
    for instrument in instruments:
        display_name, technical_name = instrument
        if technical_name in major_pairs:
            print(f"  {technical_name} - {display_name}")
    
    # 3. Historical Data Example
    print("\n3. 📈 Historical Data Example (EUR_USD)")
    print("-" * 30)
    try:
        # Get last 10 daily candles for EUR_USD
        hist_data = api.get_history('EUR_USD', granularity='D', count=10)
        print(f"Retrieved {len(hist_data)} daily candles for EUR_USD")
        print("\nLatest 5 candles:")
        print(hist_data.tail())
        
        # Basic statistics
        print(f"\nPrice Statistics (Close prices):")
        print(f"  Current: {hist_data['c'].iloc[-1]:.5f}")
        print(f"  High:    {hist_data['c'].max():.5f}")
        print(f"  Low:     {hist_data['c'].min():.5f}")
        print(f"  Mean:    {hist_data['c'].mean():.5f}")
        
    except Exception as e:
        print(f"Error getting historical data: {e}")
    
    # 4. Instrument Search Example
    print("\n4. 🔍 Instrument Search")
    print("-" * 30)
    search_term = "EUR"
    matching_instruments = []
    
    for instrument in instruments:
        display_name, technical_name = instrument
        if search_term in technical_name:
            matching_instruments.append((technical_name, display_name))
    
    print(f"Instruments containing '{search_term}':")
    for tech_name, disp_name in matching_instruments[:10]:  # Show first 10
        print(f"  {tech_name} - {disp_name}")
    
    # 5. Account Information Examples
    print("\n5. 🏦 Account Information")
    print("-" * 30)
    print(f"Balance: {api.get_account_info('balance')}")
    print(f"Account Type: {api.get_account_info('account_type')}")
    print(f"Account ID: {api.get_account_info('account_id')}")
    
    print("\n6. 📊 Market Data Access Pattern")
    print("-" * 30)
    print("Example code for accessing different timeframes:")
    print("""
    # Daily data
    daily_data = api.get_history('EUR_USD', 'D', 100)
    
    # Hourly data
    hourly_data = api.get_history('EUR_USD', 'H1', 100)
    
    # 5-minute data
    minute_data = api.get_history('EUR_USD', 'M5', 100)
    
    # Available granularities: S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30, H1, H2, H3, H4, H6, H8, H12, D, W, M
    """)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Copy .env.template to .env")
        print("2. Add your OANDA API credentials to .env")
        print("3. Make sure OANDA_ENVIRONMENT=practice for demo account")