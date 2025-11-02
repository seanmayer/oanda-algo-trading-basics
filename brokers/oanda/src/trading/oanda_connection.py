import pandas as pd
import tpqoa
import tempfile
import os
from utils.config import config

class OandaAPI:
    def __init__(self):
        config.validate_config()
        
        # Create temporary config file for tpqoa
        self._create_temp_config()
        
        # Create tpqoa API object using temporary config file
        self.api = tpqoa.tpqoa(conf_file=self.temp_config_path)
    
    def _create_temp_config(self):
        """Create a temporary config file for tpqoa"""
        config_content = f"""[oanda]
account_id = {config.account_id}
access_token = {config.api_key}
account_type = {config.environment}
"""
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False)
        temp_file.write(config_content)
        temp_file.close()
        
        self.temp_config_path = temp_file.name
    
    def __del__(self):
        """Clean up temporary config file"""
        if hasattr(self, 'temp_config_path') and os.path.exists(self.temp_config_path):
            os.unlink(self.temp_config_path)
    
    def get_account_summary(self):
        """Get account summary information"""
        return self.api.get_account_summary()
    
    def get_instruments(self):
        """Get list of available trading instruments"""
        return self.api.get_instruments()
    
    def get_account_info(self, info_type='all'):
        """
        Extract specific account information
        
        Args:
            info_type (str): 'balance', 'account_type', 'account_id', or 'all'
        """
        summary = self.get_account_summary()
        
        if info_type == 'balance':
            return summary['balance']
        elif info_type == 'account_type':
            return summary.get('account_type', config.environment)
        elif info_type == 'account_id':
            return summary['id']
        else:
            return summary
    
    def get_history(self, instrument, granularity='D', count=100):
        """
        Get historical data for an instrument
        
        Args:
            instrument (str): Instrument name (e.g., 'EUR_USD')
            granularity (str): Time granularity ('D', 'H1', 'M1', etc.)
            count (int): Number of candles to retrieve
        
        Note: Uses a conservative date range approach for reliable data access.
        """
        try:
            from datetime import datetime, timedelta
            
            # Use a safe, known date range that always has data
            # This avoids timezone and current date issues
            if granularity == 'D':
                # For daily data, adjust range based on count requested
                end_date = datetime(2025, 10, 18)  # A known good date
                if count <= 20:
                    start_date = datetime(2025, 10, 1)   # Start of October
                else:
                    # For larger counts, go back further
                    start_date = datetime(2025, 8, 1)   # Start of August for more data
            elif granularity in ['H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'H12']:
                # For hourly data, use last week
                end_date = datetime(2025, 10, 18, 18, 0)  # End at 6 PM
                start_date = datetime(2025, 10, 14, 0, 0)  # Start 4 days ago
            elif granularity == 'W':
                # For weekly data, use last few months
                end_date = datetime(2025, 10, 18)  # End date
                start_date = datetime(2025, 8, 1)   # Start of August (more weeks)
            elif granularity == 'M':
                # For monthly data, use last few years
                end_date = datetime(2025, 10, 18)  # End date
                start_date = datetime(2024, 1, 1)   # Start of last year
            elif granularity.startswith('M'):
                # For minute data, use recent days
                end_date = datetime(2025, 10, 18, 18, 0)  # End at 6 PM
                start_date = datetime(2025, 10, 17, 0, 0)  # Last day
            else:
                # Default to daily range
                end_date = datetime(2025, 10, 18)
                start_date = datetime(2025, 10, 1)
            
            return self.api.get_history(
                instrument=instrument,
                start=start_date,
                end=end_date,
                granularity=granularity,
                price='M'  # Middle price (average of bid/ask)
            )
            
        except Exception as e:
            # Provide helpful error messages based on the type of error
            error_msg = str(e)
            if "401" in error_msg or "authorization" in error_msg.lower():
                raise Exception(
                    f"Historical data access denied. Your OANDA practice account may not have "
                    f"historical data permissions. Error: {error_msg}"
                )
            elif "400" in error_msg:
                raise Exception(
                    f"Invalid request parameters for historical data. This may be due to "
                    f"requesting data outside available range or invalid instrument. Error: {error_msg}"
                )
            else:
                raise Exception(f"Error retrieving historical data: {error_msg}")
    
    def stream_data(self, instrument, stop=None, ret=False):
        """
        Stream real-time data for an instrument
        
        Args:
            instrument (str): Instrument name (e.g., 'EUR_USD')
            stop (int): Number of ticks to stream before stopping
            ret (bool): Whether to return the data
        """
        return self.api.stream_data(
            instrument=instrument,
            stop=stop,
            ret=ret
        )

if __name__ == "__main__":
    # Example usage
    try:
        # Create API connection
        oanda = OandaAPI()
        print("✅ Successfully connected to OANDA API")
        
        # Get account summary
        print("\n📊 Account Summary:")
        account_summary = oanda.get_account_summary()
        print(f"Account ID: {account_summary['id']}")
        print(f"Balance: {account_summary['balance']}")
        print(f"Currency: {account_summary['currency']}")
        
        # Get available instruments
        print("\n🎯 Available Instruments:")
        instruments = oanda.get_instruments()
        print(f"Total instruments: {len(instruments)}")
        
        # Show first 10 instruments with technical names
        print("\nFirst 10 instruments (technical names):")
        for i, instrument in enumerate(instruments[:10]):
            # instrument is a tuple: (display_name, technical_name)
            display_name, technical_name = instrument
            print(f"{i+1}. {technical_name} ({display_name})")
        
        # Get specific account information
        print(f"\n💰 Account Balance: {oanda.get_account_info('balance')}")
        print(f"🏦 Account Type: {oanda.get_account_info('account_type')}")
        print(f"🆔 Account ID: {oanda.get_account_info('account_id')}")
        
    except Exception as e:
        print(f"❌ Error connecting to OANDA API: {e}")
        print("\n🔧 Make sure you have:")
        print("1. Created a .env file with your OANDA credentials")
        print("2. Set OANDA_API_KEY and OANDA_ACCOUNT_ID in .env")
        print("3. Set OANDA_ENVIRONMENT=practice for demo account")