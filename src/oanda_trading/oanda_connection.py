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
        """
        from datetime import datetime, timedelta
        
        # Calculate start and end dates based on count
        # Use a past date that definitely has data (last Friday if weekend)
        end_date = datetime.now()
        if end_date.weekday() >= 5:  # Saturday or Sunday
            days_back = end_date.weekday() - 4  # Go back to Friday
            end_date = end_date - timedelta(days=days_back)
        
        # For practice accounts, use a more conservative date range
        # Estimate start date based on granularity and count with buffer
        if granularity == 'D':
            start_date = end_date - timedelta(days=count * 2)  # Add buffer for weekends
        elif granularity in ['H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'H12']:
            hours = int(granularity[1:]) if len(granularity) > 2 else 1
            start_date = end_date - timedelta(hours=count * hours * 2)  # Add buffer
        elif granularity.startswith('M'):
            minutes = int(granularity[1:])
            start_date = end_date - timedelta(minutes=count * minutes)
        elif granularity.startswith('S'):
            seconds = int(granularity[1:])
            start_date = end_date - timedelta(seconds=count * seconds)
        else:
            # Default to daily
            start_date = end_date - timedelta(days=count * 2)
        
        return self.api.get_history(
            instrument=instrument,
            start=start_date,
            end=end_date,
            granularity=granularity,
            price='M'  # Middle price (average of bid/ask)
        )
    
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