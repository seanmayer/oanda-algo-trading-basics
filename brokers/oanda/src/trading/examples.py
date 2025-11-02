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
    
    # 3. Historical Data Examples (EUR_USD)
    print("\n3. 📈 Historical Data Examples (EUR_USD)")
    print("-" * 30)
    
    # 3a. Daily Data
    print("\n📅 Daily Data:")
    try:
        daily_data = api.get_history('EUR_USD', granularity='D', count=10)
        print(f"Retrieved {len(daily_data)} daily candles for EUR_USD")
        print("\nLatest 3 daily candles:")
        print(daily_data.tail(3))
        
        print(f"\nDaily Price Statistics (Close prices):")
        print(f"  Current: {daily_data['c'].iloc[-1]:.5f}")
        print(f"  High:    {daily_data['c'].max():.5f}")
        print(f"  Low:     {daily_data['c'].min():.5f}")
        print(f"  Mean:    {daily_data['c'].mean():.5f}")
        
    except Exception as e:
        print(f"Error getting daily data: {e}")
    
    # 3b. Hourly Data
    print("\n⏰ Hourly Data:")
    try:
        hourly_data = api.get_history('EUR_USD', granularity='H1', count=10)
        print(f"Retrieved {len(hourly_data)} hourly candles for EUR_USD")
        print("\nLatest 3 hourly candles:")
        print(hourly_data.tail(3))
        
        # Show hourly volatility
        hourly_range = hourly_data['h'] - hourly_data['l']
        print(f"\nHourly Statistics:")
        print(f"  Average hourly range: {hourly_range.mean():.5f}")
        print(f"  Max hourly range:     {hourly_range.max():.5f}")
        print(f"  Latest close:         {hourly_data['c'].iloc[-1]:.5f}")
        
    except Exception as e:
        print(f"Error getting hourly data: {e}")
    
    # 3c. Weekly Data
    print("\n📊 Weekly Data:")
    try:
        weekly_data = api.get_history('EUR_USD', granularity='W', count=10)
        print(f"Retrieved {len(weekly_data)} weekly candles for EUR_USD")
        print("\nLatest 3 weekly candles:")
        print(weekly_data.tail(3))
        
        # Show weekly trend
        weekly_change = weekly_data['c'].pct_change() * 100
        print(f"\nWeekly Statistics:")
        print(f"  Average weekly change: {weekly_change.mean():.2f}%")
        print(f"  Latest weekly change:  {weekly_change.iloc[-1]:.2f}%")
        print(f"  Weekly volatility:     {weekly_change.std():.2f}%")
        
    except Exception as e:
        print(f"Error getting weekly data: {e}")
    
    # 3d. Monthly/Long-term Analysis
    print("\n📈 Monthly Data (longer-term trend):")
    
    # First try to get actual monthly data
    monthly_success = False
    try:
        monthly_data = api.get_history('EUR_USD', granularity='M', count=10)
        print(f"Retrieved {len(monthly_data)} monthly candles for EUR_USD")
        
        # Check for data quality issues
        if not monthly_data.empty:
            # Clean the data - remove any rows with missing values
            clean_monthly = monthly_data.dropna()
            
            if not clean_monthly.empty and len(clean_monthly) > 1:
                print("\nLatest 3 monthly candles:")
                print(clean_monthly.tail(3))
                
                monthly_change = clean_monthly['c'].pct_change() * 100
                print(f"\nMonthly Statistics:")
                print(f"  Average monthly change: {monthly_change.mean():.2f}%")
                print(f"  Latest monthly change:  {monthly_change.iloc[-1]:.2f}%")
                print(f"  Monthly volatility:     {monthly_change.std():.2f}%")
                
                if len(clean_monthly) >= 6:
                    six_month_trend = ((clean_monthly['c'].iloc[-1] / clean_monthly['c'].iloc[-6]) - 1) * 100
                    print(f"  6-month trend:          {six_month_trend:.2f}%")
                
                monthly_success = True
        
    except Exception as e:
        pass  # We'll handle this with the fallback below
    
    # If monthly data failed, use daily data to create monthly analysis
    if not monthly_success:
        print("⚠️  Native monthly data not available in practice account")
        print("📊 Using daily data for monthly analysis (alternative approach):")
        
        try:
            # Get more daily data for monthly analysis
            extended_daily = api.get_history('EUR_USD', granularity='D', count=100)
            
            if not extended_daily.empty and len(extended_daily) > 20:
                # Resample daily data to approximate monthly periods (every ~22 trading days)
                extended_daily.index = extended_daily.index
                monthly_approx = extended_daily.iloc[::22]  # Every 22 days ≈ 1 month
                
                print(f"\nApproximate monthly periods from daily data ({len(monthly_approx)} periods):")
                print(monthly_approx[['o', 'h', 'l', 'c']].tail(3))
                
                if len(monthly_approx) > 1:
                    monthly_changes = monthly_approx['c'].pct_change() * 100
                    print(f"\nMonthly-Period Statistics (from daily data):")
                    print(f"  Average period change:  {monthly_changes.mean():.2f}%")
                    print(f"  Latest period change:   {monthly_changes.iloc[-1]:.2f}%")
                    print(f"  Period volatility:      {monthly_changes.std():.2f}%")
                    
                    # Long-term trend analysis
                    if len(monthly_approx) >= 3:
                        three_month_trend = ((monthly_approx['c'].iloc[-1] / monthly_approx['c'].iloc[-3]) - 1) * 100
                        print(f"  3-period trend:         {three_month_trend:.2f}%")
            else:
                print("Insufficient daily data for monthly analysis")
                
        except Exception as e:
            print(f"Error creating monthly analysis from daily data: {e}")
            print("💡 Note: OANDA practice accounts have limited historical data access")
    
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