#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_oanda_credentials():
    """Test OANDA API credentials step by step"""
    
    api_key = os.getenv('OANDA_API_KEY')
    account_id = os.getenv('OANDA_ACCOUNT_ID')
    environment = os.getenv('OANDA_ENVIRONMENT', 'practice')
    
    print("🔍 OANDA API Diagnostic Tool")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Environment Variables:")
    print(f"   API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"   Account ID: {'✅ Set' if account_id else '❌ Missing'}")
    print(f"   Environment: {environment}")
    
    if not api_key or not account_id:
        print("\n❌ Missing required environment variables!")
        return False
    
    # Set base URL based on environment
    if environment == 'practice':
        base_url = 'https://api-fxpractice.oanda.com'
    else:
        base_url = 'https://api-fxtrade.oanda.com'
    
    print(f"   Base URL: {base_url}")
    
    # Test 1: Basic API connection (get accounts)
    print("\n2. Testing API Key (GET /v3/accounts):")
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{base_url}/v3/accounts", headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('accounts', [])
            print(f"   ✅ API Key is valid!")
            print(f"   Found {len(accounts)} account(s):")
            
            for account in accounts:
                account_id_from_api = account.get('id')
                print(f"     - {account_id_from_api}")
                
                if account_id_from_api == account_id:
                    print(f"     ✅ Account ID {account_id} matches!")
                else:
                    print(f"     ⚠️  Account ID {account_id} doesn't match API")
            
            return True
            
        elif response.status_code == 401:
            print("   ❌ API Key is invalid or expired")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"   ❌ Unexpected error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

    # Test 2: Specific account access
    print(f"\n3. Testing Account Access (GET /v3/accounts/{account_id}):")
    try:
        response = requests.get(f"{base_url}/v3/accounts/{account_id}", headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Account access successful!")
            data = response.json()
            if 'account' in data:
                account_info = data['account']
                print(f"   Account ID: {account_info.get('id')}")
                print(f"   Currency: {account_info.get('currency')}")
                print(f"   Balance: {account_info.get('balance')}")
            return True
        else:
            print(f"   ❌ Account access failed")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error accessing account: {e}")
        return False

if __name__ == "__main__":
    success = test_oanda_credentials()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your OANDA connection should work.")
    else:
        print("❌ Issues found. Please fix the above problems.")
        print("\n💡 Common solutions:")
        print("1. Regenerate your API token in OANDA dashboard")
        print("2. Verify your account ID is correct")
        print("3. Make sure you're using the right environment (practice/live)")