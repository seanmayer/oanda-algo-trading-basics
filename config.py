import os
from dotenv import load_dotenv

load_dotenv(override=True)  # Override existing environment variables

class OandaConfig:
    def __init__(self):
        self.api_key = os.getenv('OANDA_API_KEY')
        self.account_id = os.getenv('OANDA_ACCOUNT_ID')
        self.environment = os.getenv('OANDA_ENVIRONMENT', 'practice')
        
        if self.environment == 'practice':
            self.api_url = 'https://api-fxpractice.oanda.com'
            self.stream_url = 'https://stream-fxpractice.oanda.com'
        else:
            self.api_url = 'https://api-fxtrade.oanda.com'
            self.stream_url = 'https://stream-fxtrade.oanda.com'
    
    def validate_config(self):
        if not self.api_key:
            raise ValueError("OANDA_API_KEY not found in environment variables")
        if not self.account_id:
            raise ValueError("OANDA_ACCOUNT_ID not found in environment variables")
        return True
    
    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

config = OandaConfig()