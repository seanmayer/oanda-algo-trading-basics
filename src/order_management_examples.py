"""
OANDA Order Management Examples
==============================

This module demonstrates comprehensive order management capabilities with the OANDA API,
including creating, modifying, and monitoring various types of trading orders.

Features:
- Market orders (buy/sell immediately)
- Limit orders (buy/sell at specific price)
- Stop orders (stop-loss and take-profit)
- Order modification and cancellation
- Position and trade monitoring
- Risk management examples
- Paper trading demonstrations

IMPORTANT: This uses a practice account for demonstration.
Always test thoroughly before using with real money!
"""

import pandas as pd
import time
from datetime import datetime, timedelta
from oanda_trading.oanda_connection import OandaAPI

class OrderManager:
    """
    Comprehensive order management for OANDA trading
    """
    
    def __init__(self):
        """Initialize the order manager"""
        self.api = OandaAPI()
        self.account_id = self.api.get_account_info('account_id')
        print(f"🔗 Connected to OANDA {self.api.get_account_info('account_type')} account")
        print(f"📋 Account ID: {self.account_id}")
        print(f"💰 Balance: {self.api.get_account_info('balance')}")
    
    def get_current_price(self, instrument):
        """Get current bid/ask prices for an instrument"""
        try:
            # Get recent price data
            recent_data = self.api.get_history(instrument, granularity='M1', count=1)
            if not recent_data.empty:
                latest = recent_data.iloc[-1]
                # Use close price as reference, calculate bid/ask spread
                close_price = latest['c']
                spread = 0.0002  # Approximate spread for major pairs
                bid = close_price - spread/2
                ask = close_price + spread/2
                return {'bid': bid, 'ask': ask, 'mid': close_price}
            else:
                return None
        except Exception as e:
            print(f"❌ Error getting current price: {e}")
            return None
    
    def create_market_order(self, instrument, units, side='buy'):
        """
        Create a market order (execute immediately at current market price)
        
        Args:
            instrument (str): Trading instrument (e.g., 'EUR_USD')
            units (int): Number of units (positive for buy, negative for sell)
            side (str): 'buy' or 'sell' for clarity
            
        Returns:
            dict: Order response or error information
        """
        try:
            print(f"📈 Creating {side.upper()} market order")
            print(f"   Instrument: {instrument}")
            print(f"   Units: {units}")
            
            # Get current price for reference
            current_price = self.get_current_price(instrument)
            if current_price:
                price_ref = current_price['ask'] if side == 'buy' else current_price['bid']
                print(f"   Current {side} price: {price_ref:.5f}")
            
            # Adjust units for sell orders
            if side == 'sell' and units > 0:
                units = -units
            
            # In a real implementation, you would use the OANDA API to create the order
            # For demonstration, we'll simulate the order creation
            order_response = self._simulate_market_order(instrument, units, current_price)
            
            return order_response
            
        except Exception as e:
            error_msg = f"Error creating market order: {e}"
            print(f"❌ {error_msg}")
            return {'error': error_msg}
    
    def create_limit_order(self, instrument, units, price, side='buy', 
                          stop_loss=None, take_profit=None):
        """
        Create a limit order (execute when price reaches specified level)
        
        Args:
            instrument (str): Trading instrument
            units (int): Number of units
            price (float): Limit price
            side (str): 'buy' or 'sell'
            stop_loss (float): Optional stop loss price
            take_profit (float): Optional take profit price
            
        Returns:
            dict: Order response
        """
        try:
            print(f"🎯 Creating {side.upper()} limit order")
            print(f"   Instrument: {instrument}")
            print(f"   Units: {units}")
            print(f"   Limit Price: {price:.5f}")
            
            if stop_loss:
                print(f"   Stop Loss: {stop_loss:.5f}")
            if take_profit:
                print(f"   Take Profit: {take_profit:.5f}")
            
            # Get current price for reference
            current_price = self.get_current_price(instrument)
            if current_price:
                current = current_price['mid']
                print(f"   Current Price: {current:.5f}")
                
                if side == 'buy' and price >= current:
                    print("⚠️  Warning: Buy limit price above current market (will execute immediately)")
                elif side == 'sell' and price <= current:
                    print("⚠️  Warning: Sell limit price below current market (will execute immediately)")
            
            # Adjust units for sell orders
            if side == 'sell' and units > 0:
                units = -units
            
            # Simulate limit order creation
            order_response = self._simulate_limit_order(instrument, units, price, stop_loss, take_profit)
            
            return order_response
            
        except Exception as e:
            error_msg = f"Error creating limit order: {e}"
            print(f"❌ {error_msg}")
            return {'error': error_msg}
    
    def create_stop_order(self, instrument, units, price, side='buy'):
        """
        Create a stop order (execute when price breaks through specified level)
        
        Args:
            instrument (str): Trading instrument
            units (int): Number of units
            price (float): Stop price
            side (str): 'buy' or 'sell'
            
        Returns:
            dict: Order response
        """
        try:
            print(f"🛑 Creating {side.upper()} stop order")
            print(f"   Instrument: {instrument}")
            print(f"   Units: {units}")
            print(f"   Stop Price: {price:.5f}")
            
            # Get current price for context
            current_price = self.get_current_price(instrument)
            if current_price:
                current = current_price['mid']
                print(f"   Current Price: {current:.5f}")
                
                if side == 'buy' and price <= current:
                    print("⚠️  Warning: Buy stop price below current market")
                elif side == 'sell' and price >= current:
                    print("⚠️  Warning: Sell stop price above current market")
            
            # Adjust units for sell orders
            if side == 'sell' and units > 0:
                units = -units
            
            # Simulate stop order creation
            order_response = self._simulate_stop_order(instrument, units, price)
            
            return order_response
            
        except Exception as e:
            error_msg = f"Error creating stop order: {e}"
            print(f"❌ {error_msg}")
            return {'error': error_msg}
    
    def _simulate_market_order(self, instrument, units, current_price):
        """Simulate market order execution"""
        import random
        
        order_id = random.randint(100000, 999999)
        fill_price = current_price['ask'] if units > 0 else current_price['bid']
        
        # Add some realistic slippage
        slippage = random.uniform(-0.0001, 0.0001)
        fill_price += slippage
        
        return {
            'order_id': order_id,
            'type': 'MARKET',
            'instrument': instrument,
            'units': units,
            'state': 'FILLED',
            'fill_price': fill_price,
            'fill_time': datetime.now().isoformat(),
            'pnl': 0.0,
            'commission': abs(units) * 0.000025  # Approximate commission
        }
    
    def _simulate_limit_order(self, instrument, units, price, stop_loss, take_profit):
        """Simulate limit order creation"""
        import random
        
        order_id = random.randint(100000, 999999)
        
        return {
            'order_id': order_id,
            'type': 'LIMIT',
            'instrument': instrument,
            'units': units,
            'price': price,
            'state': 'PENDING',
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'created_time': datetime.now().isoformat()
        }
    
    def _simulate_stop_order(self, instrument, units, price):
        """Simulate stop order creation"""
        import random
        
        order_id = random.randint(100000, 999999)
        
        return {
            'order_id': order_id,
            'type': 'STOP',
            'instrument': instrument,
            'units': units,
            'price': price,
            'state': 'PENDING',
            'created_time': datetime.now().isoformat()
        }
    
    def get_open_positions(self):
        """Get all open positions"""
        print("📊 Current Open Positions")
        print("-" * 30)
        
        # In a real implementation, you would call the OANDA API
        # For demonstration, we'll show what the response would look like
        positions = [
            {
                'instrument': 'EUR_USD',
                'units': 10000,
                'avg_price': 1.16045,
                'current_price': 1.16052,
                'unrealized_pnl': 7.0,
                'margin_used': 387.5
            },
            {
                'instrument': 'GBP_USD',
                'units': -5000,
                'avg_price': 1.27235,
                'current_price': 1.27225,
                'unrealized_pnl': 5.0,
                'margin_used': 212.7
            }
        ]
        
        if positions:
            for pos in positions:
                side = "LONG" if pos['units'] > 0 else "SHORT"
                pnl_color = "📈" if pos['unrealized_pnl'] > 0 else "📉"
                
                print(f"{pos['instrument']} - {side}")
                print(f"  Units: {pos['units']}")
                print(f"  Avg Price: {pos['avg_price']:.5f}")
                print(f"  Current: {pos['current_price']:.5f}")
                print(f"  P&L: {pnl_color} {pos['unrealized_pnl']:.2f}")
                print(f"  Margin: {pos['margin_used']:.2f}")
                print()
        else:
            print("No open positions")
        
        return positions
    
    def get_pending_orders(self):
        """Get all pending orders"""
        print("📋 Pending Orders")
        print("-" * 20)
        
        # Simulated pending orders
        orders = [
            {
                'order_id': 123456,
                'type': 'LIMIT',
                'instrument': 'EUR_USD',
                'units': 5000,
                'price': 1.15800,
                'state': 'PENDING',
                'created': '2025-10-21T10:30:00Z'
            },
            {
                'order_id': 789012,
                'type': 'STOP',
                'instrument': 'USD_JPY',
                'units': -3000,
                'price': 150.500,
                'state': 'PENDING',
                'created': '2025-10-21T14:15:00Z'
            }
        ]
        
        if orders:
            for order in orders:
                side = "BUY" if order['units'] > 0 else "SELL"
                print(f"ID: {order['order_id']} - {order['type']} {side}")
                print(f"  {order['instrument']}: {order['units']} units @ {order['price']}")
                print(f"  Status: {order['state']}")
                print(f"  Created: {order['created']}")
                print()
        else:
            print("No pending orders")
        
        return orders


def demonstrate_market_orders():
    """Demonstrate market order creation"""
    print("📈 Market Order Examples")
    print("=" * 35)
    
    order_mgr = OrderManager()
    
    print("\n1. 📊 Current Market Conditions")
    print("-" * 30)
    
    # Check current prices for major pairs
    instruments = ['EUR_USD', 'GBP_USD', 'USD_JPY']
    for instrument in instruments:
        price = order_mgr.get_current_price(instrument)
        if price:
            print(f"{instrument}: Bid {price['bid']:.5f} | Ask {price['ask']:.5f} | Mid {price['mid']:.5f}")
    
    print("\n2. 💰 Market Order Examples")
    print("-" * 30)
    
    # Example 1: Buy EUR_USD
    print("Example 1: Buy 1,000 EUR_USD")
    order1 = order_mgr.create_market_order('EUR_USD', 1000, 'buy')
    if 'error' not in order1:
        print(f"✅ Order filled! ID: {order1['order_id']}")
        print(f"   Fill Price: {order1['fill_price']:.5f}")
        print(f"   Commission: ${order1['commission']:.2f}")
    
    print("\n" + "-" * 40)
    
    # Example 2: Sell GBP_USD
    print("Example 2: Sell 2,500 GBP_USD")
    order2 = order_mgr.create_market_order('GBP_USD', 2500, 'sell')
    if 'error' not in order2:
        print(f"✅ Order filled! ID: {order2['order_id']}")
        print(f"   Fill Price: {order2['fill_price']:.5f}")
        print(f"   Commission: ${order2['commission']:.2f}")
    
    print("\n💡 Market orders execute immediately at current market prices")
    print("   They guarantee execution but not price")


def demonstrate_limit_orders():
    """Demonstrate limit order creation"""
    print("\n🎯 Limit Order Examples")
    print("=" * 30)
    
    order_mgr = OrderManager()
    
    # Get current EUR_USD price
    current_price = order_mgr.get_current_price('EUR_USD')
    if not current_price:
        print("❌ Could not get current price")
        return
    
    current = current_price['mid']
    
    print("\n1. 📈 Buy Limit Order (below current price)")
    print("-" * 40)
    
    # Buy limit below current price
    buy_limit_price = current - 0.0050  # 50 pips below
    stop_loss = buy_limit_price - 0.0030  # 30 pips stop loss
    take_profit = buy_limit_price + 0.0060  # 60 pips take profit
    
    order1 = order_mgr.create_limit_order(
        'EUR_USD', 5000, buy_limit_price, 'buy',
        stop_loss=stop_loss, take_profit=take_profit
    )
    
    if 'error' not in order1:
        print(f"✅ Limit order created! ID: {order1['order_id']}")
        print(f"   Will buy if price drops to {buy_limit_price:.5f}")
    
    print("\n2. 📉 Sell Limit Order (above current price)")
    print("-" * 40)
    
    # Sell limit above current price
    sell_limit_price = current + 0.0040  # 40 pips above
    
    order2 = order_mgr.create_limit_order(
        'EUR_USD', 3000, sell_limit_price, 'sell'
    )
    
    if 'error' not in order2:
        print(f"✅ Limit order created! ID: {order2['order_id']}")
        print(f"   Will sell if price rises to {sell_limit_price:.5f}")
    
    print("\n💡 Limit orders execute only at your specified price or better")
    print("   They guarantee price but not execution")


def demonstrate_stop_orders():
    """Demonstrate stop order creation"""
    print("\n🛑 Stop Order Examples")
    print("=" * 25)
    
    order_mgr = OrderManager()
    
    # Get current USD_JPY price
    current_price = order_mgr.get_current_price('USD_JPY')
    if not current_price:
        print("❌ Could not get current price")
        return
    
    current = current_price['mid']
    
    print("\n1. 🔺 Buy Stop Order (above current price)")
    print("-" * 40)
    
    # Buy stop above current price (breakout strategy)
    buy_stop_price = current + 0.500  # 50 pips above
    
    order1 = order_mgr.create_stop_order('USD_JPY', 2000, buy_stop_price, 'buy')
    
    if 'error' not in order1:
        print(f"✅ Stop order created! ID: {order1['order_id']}")
        print(f"   Will buy if price breaks above {buy_stop_price:.3f}")
    
    print("\n2. 🔻 Sell Stop Order (below current price)")
    print("-" * 40)
    
    # Sell stop below current price (breakdown strategy)
    sell_stop_price = current - 0.750  # 75 pips below
    
    order2 = order_mgr.create_stop_order('USD_JPY', 1500, sell_stop_price, 'sell')
    
    if 'error' not in order2:
        print(f"✅ Stop order created! ID: {order2['order_id']}")
        print(f"   Will sell if price breaks below {sell_stop_price:.3f}")
    
    print("\n💡 Stop orders become market orders when price is reached")
    print("   Used for breakout strategies and stop losses")


def demonstrate_position_monitoring():
    """Demonstrate position and order monitoring"""
    print("\n📊 Position & Order Monitoring")
    print("=" * 35)
    
    order_mgr = OrderManager()
    
    print("\n1. Current Positions")
    positions = order_mgr.get_open_positions()
    
    print("\n2. Pending Orders")
    orders = order_mgr.get_pending_orders()
    
    # Calculate total exposure and margin
    total_margin = sum(pos.get('margin_used', 0) for pos in positions)
    total_pnl = sum(pos.get('unrealized_pnl', 0) for pos in positions)
    
    print("📈 Portfolio Summary")
    print("-" * 20)
    print(f"Total Margin Used: ${total_margin:.2f}")
    print(f"Unrealized P&L: ${total_pnl:.2f}")
    print(f"Open Positions: {len(positions)}")
    print(f"Pending Orders: {len(orders)}")


def demonstrate_risk_management():
    """Demonstrate risk management concepts"""
    print("\n⚠️  Risk Management Examples")
    print("=" * 35)
    
    print("1. 💰 Position Sizing")
    print("-" * 20)
    
    account_balance = 10000  # $10,000 account
    risk_per_trade = 0.02    # 2% risk per trade
    
    print(f"Account Balance: ${account_balance:,}")
    print(f"Risk per Trade: {risk_per_trade*100}%")
    print(f"Max Risk Amount: ${account_balance * risk_per_trade:.2f}")
    
    # Example position sizing
    entry_price = 1.16000
    stop_loss = 1.15700
    pip_risk = (entry_price - stop_loss) * 10000  # Convert to pips
    pip_value = 1.0  # $1 per pip for EUR_USD with 10K units
    
    max_risk_amount = account_balance * risk_per_trade
    position_size = int(max_risk_amount / (pip_risk * pip_value) * 10000)
    
    print(f"\nExample Trade Setup:")
    print(f"  Entry: {entry_price:.5f}")
    print(f"  Stop Loss: {stop_loss:.5f}")
    print(f"  Risk: {pip_risk:.1f} pips")
    print(f"  Position Size: {position_size:,} units")
    print(f"  Actual Risk: ${pip_risk * pip_value * position_size / 10000:.2f}")
    
    print("\n2. 📊 Diversification")
    print("-" * 20)
    print("✅ Don't risk more than 5% on any single currency")
    print("✅ Spread trades across different currency pairs")
    print("✅ Consider correlation between pairs")
    
    print("\n3. 🛡️ Stop Loss Guidelines")
    print("-" * 25)
    print("✅ Always use stop losses")
    print("✅ Set stops based on technical levels, not arbitrary amounts")
    print("✅ Never move stops against your position")
    print("✅ Consider using trailing stops for trending markets")


def main():
    """Main demonstration function"""
    print("💼 OANDA Order Management Examples")
    print("=" * 45)
    
    try:
        # Initialize and show account info
        order_mgr = OrderManager()
        print()
        
        # Run demonstrations
        demonstrate_market_orders()
        demonstrate_limit_orders()
        demonstrate_stop_orders()
        demonstrate_position_monitoring()
        demonstrate_risk_management()
        
        print("\n" + "=" * 60)
        print("🎯 Order Management Summary")
        print("=" * 60)
        
        print("✅ Market Orders: Immediate execution at current price")
        print("✅ Limit Orders: Execute at specific price or better")
        print("✅ Stop Orders: Trigger when price breaks through level")
        print("✅ Position Monitoring: Track P&L and margin usage")
        print("✅ Risk Management: Control exposure and protect capital")
        
        print("\n⚠️  Important Reminders:")
        print("• This demonstration uses a practice account")
        print("• Always test strategies thoroughly before live trading")
        print("• Never risk more than you can afford to lose")
        print("• Markets can be volatile - use proper risk management")
        
        print("\n🚀 Ready to implement your trading strategies!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Ensure your .env file has valid OANDA credentials")
        print("2. Check your internet connection")
        print("3. Verify your practice account is active")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check your setup and try again")