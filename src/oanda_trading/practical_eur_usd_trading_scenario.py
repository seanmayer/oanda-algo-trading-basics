"""
Practical EUR/USD Trading Scenario with Automated Algorithm
==========================================================

This module implements a practical trading scenario that:
1. Focuses on EUR/USD currency pair
2. Runs a 5-minute trading session
3. Uses a moving average-based buy/sell algorithm
4. Analyzes trade performance and calculates P&L

Trading Algorithm:
- Calculate 5-minute moving average of prices
- BUY when current price is below the moving average (price is "down")
- SELL when current price is above the moving average (price is "up")
- Stop trading after 5 minutes
- Analyze all trades and calculate profit/loss

Author: Generated for practical OANDA trading demonstration
"""

import pandas as pd
import time
import threading
from datetime import datetime, timedelta
from collections import deque
from oanda_trading.oanda_connection import OandaAPI
import statistics
import json

class PracticalEURUSDTrader:
    """
    Practical EUR/USD trading implementation with automated algorithm
    """
    
    def __init__(self, initial_balance=10000, position_size=1000):
        """
        Initialize the trading scenario
        
        Args:
            initial_balance (float): Starting balance in account currency
            position_size (int): Size of each trade position in units
        """
        self.api = OandaAPI()
        self.instrument = 'EUR_USD'
        self.initial_balance = initial_balance
        self.position_size = position_size
        self.current_balance = initial_balance
        
        # Trading session configuration
        self.session_duration = 300  # 5 minutes in seconds
        self.moving_average_window = 20  # 20 price points for moving average
        
        # Data storage
        self.price_history = deque(maxlen=self.moving_average_window)
        self.trades = []
        self.current_position = None  # 'long', 'short', or None
        
        # Trading session tracking
        self.session_start = None
        self.session_end = None
        self.is_trading = False
        self.trade_count = 0
        
        # Performance metrics
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'average_trade_size': 0,
            'win_rate': 0
        }
        
        print(f"🚀 Practical EUR/USD Trader Initialized")
        print(f"📊 Initial Balance: ${self.initial_balance:,.2f}")
        print(f"📏 Position Size: {self.position_size:,} units")
        print(f"⏱️  Session Duration: {self.session_duration // 60} minutes")
        print(f"📈 Moving Average Window: {self.moving_average_window} price points")
    
    def get_current_price(self):
        """
        Get current market price for EUR/USD
        Returns both bid and ask prices, uses mid-price for algorithm
        """
        try:
            # Get the most recent historical data point as current price
            # In real implementation, this would be real-time streaming data
            recent_data = self.api.get_history(self.instrument, granularity='M1', count=1)
            if not recent_data.empty:
                latest_candle = recent_data.iloc[-1]
                bid = latest_candle['c'] - 0.00015  # Simulate bid-ask spread
                ask = latest_candle['c'] + 0.00015  # Simulate bid-ask spread
                mid_price = latest_candle['c']
                
                return {
                    'bid': bid,
                    'ask': ask,
                    'mid': mid_price,
                    'timestamp': datetime.now()
                }
            else:
                raise Exception("No recent price data available")
                
            
        except Exception as e:
            # Fallback to simulated price for demonstration
            print(f"⚠️ Using simulated price data: {e}")
            import random
            base_price = 1.1650  # Typical EUR/USD price
            spread = 0.0003
            mid_price = base_price + random.uniform(-0.005, 0.005)  # Small random movement
            
            return {
                'bid': mid_price - spread/2,
                'ask': mid_price + spread/2,
                'mid': mid_price,
                'timestamp': datetime.now()
            }
    
    def calculate_moving_average(self):
        """
        Calculate the moving average of recent prices
        """
        if len(self.price_history) < 2:
            return None
        
        prices = [price_data['mid'] for price_data in self.price_history]
        return statistics.mean(prices)
    
    def should_buy(self, current_price, moving_average):
        """
        Determine if we should buy (go long)
        Buy when price is below moving average (expecting price to rise)
        """
        if moving_average is None:
            return False
        
        return current_price < moving_average and self.current_position != 'long'
    
    def should_sell(self, current_price, moving_average):
        """
        Determine if we should sell (go short)
        Sell when price is above moving average (expecting price to fall)
        """
        if moving_average is None:
            return False
        
        return current_price > moving_average and self.current_position != 'short'
    
    def execute_trade(self, action, price_data):
        """
        Execute a trade (simulated for demonstration)
        
        Args:
            action (str): 'buy' or 'sell'
            price_data (dict): Current price information
        """
        self.trade_count += 1
        
        if action == 'buy':
            execution_price = price_data['ask']  # Buy at ask price
            self.current_position = 'long'
            trade_type = 'BUY'
        else:  # sell
            execution_price = price_data['bid']  # Sell at bid price
            self.current_position = 'short'
            trade_type = 'SELL'
        
        trade = {
            'trade_id': self.trade_count,
            'type': trade_type,
            'instrument': self.instrument,
            'units': self.position_size,
            'execution_price': execution_price,
            'timestamp': price_data['timestamp'],
            'moving_average': self.calculate_moving_average(),
            'profit_loss': None  # Will be calculated when position is closed
        }
        
        self.trades.append(trade)
        
        print(f"🔄 Trade #{self.trade_count}: {trade_type} {self.position_size:,} {self.instrument} @ {execution_price:.5f}")
        
        return trade
    
    def close_position(self, price_data, reason="end_of_session"):
        """
        Close the current position and calculate P&L
        """
        if self.current_position is None:
            return None
        
        # Find the last opening trade
        last_trade = self.trades[-1] if self.trades else None
        if last_trade is None:
            return None
        
        # Calculate P&L
        if self.current_position == 'long':
            # Long position: profit if price increased
            closing_price = price_data['bid']  # Close long at bid
            pnl = (closing_price - last_trade['execution_price']) * self.position_size
        else:  # short position
            # Short position: profit if price decreased
            closing_price = price_data['ask']  # Close short at ask
            pnl = (last_trade['execution_price'] - closing_price) * self.position_size
        
        # Update trade record with P&L
        last_trade['profit_loss'] = pnl
        last_trade['closing_price'] = closing_price
        last_trade['closing_reason'] = reason
        
        # Update balance
        self.current_balance += pnl
        
        # Reset position
        position_type = self.current_position
        self.current_position = None
        
        print(f"✅ Closed {position_type} position @ {closing_price:.5f} | P&L: ${pnl:.2f}")
        
        return pnl
    
    def run_trading_session(self):
        """
        Run the complete 5-minute trading session
        """
        print("\n" + "="*60)
        print("🎯 Starting 5-Minute EUR/USD Trading Session")
        print("="*60)
        
        self.session_start = datetime.now()
        self.session_end = self.session_start + timedelta(seconds=self.session_duration)
        self.is_trading = True
        
        print(f"📅 Session Start: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 Session End:   {self.session_end.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Algorithm: Buy when price < MA, Sell when price > MA")
        print(f"📊 Moving Average Window: {self.moving_average_window} points")
        print("\n🔄 Trading Activity:")
        print("-" * 50)
        
        iteration = 0
        
        try:
            while datetime.now() < self.session_end and self.is_trading:
                iteration += 1
                
                # Get current price
                price_data = self.get_current_price()
                current_price = price_data['mid']
                
                # Add to price history
                self.price_history.append(price_data)
                
                # Calculate moving average
                moving_average = self.calculate_moving_average()
                
                # Display current status every 5 iterations
                if iteration % 5 == 0:
                    ma_str = f"{moving_average:.5f}" if moving_average else "Calculating..."
                    print(f"[{price_data['timestamp'].strftime('%H:%M:%S')}] "
                          f"Price: {current_price:.5f} | MA: {ma_str} | "
                          f"Position: {self.current_position or 'None'}")
                
                # Trading logic
                if moving_average is not None:
                    # Check if we should make a trade
                    if self.should_buy(current_price, moving_average):
                        # Close existing short position if any
                        if self.current_position == 'short':
                            self.close_position(price_data, "strategy_reversal")
                        
                        # Open long position
                        self.execute_trade('buy', price_data)
                    
                    elif self.should_sell(current_price, moving_average):
                        # Close existing long position if any
                        if self.current_position == 'long':
                            self.close_position(price_data, "strategy_reversal")
                        
                        # Open short position
                        self.execute_trade('sell', price_data)
                
                # Simulate real-time delay (shorter for demonstration)
                time.sleep(1)  # 1 second between price checks
        
        except KeyboardInterrupt:
            print("\n⏹️ Trading session interrupted by user")
        
        finally:
            # End of session - close any open positions
            if self.current_position is not None:
                final_price = self.get_current_price()
                self.close_position(final_price, "end_of_session")
            
            self.is_trading = False
            
            print("\n" + "="*60)
            print("🏁 Trading Session Complete")
            print("="*60)
    
    def analyze_performance(self):
        """
        Analyze trading performance and calculate comprehensive metrics
        """
        print("\n📊 Trade Analysis & Performance Report")
        print("="*50)
        
        if not self.trades:
            print("❌ No trades executed during session")
            return
        
        # Calculate basic metrics
        total_trades = len(self.trades)
        trades_with_pnl = [t for t in self.trades if t['profit_loss'] is not None]
        
        if not trades_with_pnl:
            print("⚠️ No completed trades to analyze")
            return
        
        # P&L calculations
        total_pnl = sum(t['profit_loss'] for t in trades_with_pnl)
        winning_trades = [t for t in trades_with_pnl if t['profit_loss'] > 0]
        losing_trades = [t for t in trades_with_pnl if t['profit_loss'] < 0]
        
        self.metrics = {
            'total_trades': total_trades,
            'completed_trades': len(trades_with_pnl),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'total_profit_loss': total_pnl,
            'largest_win': max((t['profit_loss'] for t in winning_trades), default=0),
            'largest_loss': min((t['profit_loss'] for t in losing_trades), default=0),
            'average_trade_pnl': total_pnl / len(trades_with_pnl) if trades_with_pnl else 0,
            'win_rate': (len(winning_trades) / len(trades_with_pnl) * 100) if trades_with_pnl else 0,
            'profit_factor': (sum(t['profit_loss'] for t in winning_trades) / 
                             abs(sum(t['profit_loss'] for t in losing_trades))) if losing_trades else float('inf'),
            'final_balance': self.current_balance,
            'roi': (total_pnl / self.initial_balance * 100)
        }
        
        # Display results
        print(f"\n💼 Session Summary:")
        print(f"   Initial Balance:     ${self.initial_balance:,.2f}")
        print(f"   Final Balance:       ${self.metrics['final_balance']:,.2f}")
        print(f"   Total P&L:           ${self.metrics['total_profit_loss']:+.2f}")
        print(f"   ROI:                 {self.metrics['roi']:+.2f}%")
        
        print(f"\n📈 Trade Statistics:")
        print(f"   Total Trades:        {self.metrics['total_trades']}")
        print(f"   Completed Trades:    {self.metrics['completed_trades']}")
        print(f"   Winning Trades:      {self.metrics['winning_trades']}")
        print(f"   Losing Trades:       {self.metrics['losing_trades']}")
        print(f"   Win Rate:            {self.metrics['win_rate']:.1f}%")
        
        print(f"\n💰 P&L Analysis:")
        print(f"   Average Trade P&L:   ${self.metrics['average_trade_pnl']:+.2f}")
        print(f"   Largest Win:         ${self.metrics['largest_win']:+.2f}")
        print(f"   Largest Loss:        ${self.metrics['largest_loss']:+.2f}")
        if self.metrics['profit_factor'] != float('inf'):
            print(f"   Profit Factor:       {self.metrics['profit_factor']:.2f}")
        else:
            print(f"   Profit Factor:       ∞ (no losing trades)")
        
        # Detailed trade log
        print(f"\n📋 Detailed Trade Log:")
        print("-" * 80)
        print(f"{'ID':<3} {'Type':<4} {'Price':<8} {'P&L':<10} {'Timestamp':<19} {'Reason':<15}")
        print("-" * 80)
        
        for trade in self.trades:
            pnl_str = f"${trade['profit_loss']:+.2f}" if trade['profit_loss'] is not None else "Open"
            timestamp_str = trade['timestamp'].strftime('%H:%M:%S')
            reason = trade.get('closing_reason', 'N/A')[:14]
            
            print(f"{trade['trade_id']:<3} {trade['type']:<4} {trade['execution_price']:<8.5f} "
                  f"{pnl_str:<10} {timestamp_str:<19} {reason:<15}")
        
        # Trading algorithm performance
        print(f"\n🎯 Algorithm Performance:")
        if trades_with_pnl:
            avg_prices = [t['moving_average'] for t in self.trades if t['moving_average'] is not None]
            if avg_prices:
                print(f"   Avg Moving Average:  {statistics.mean(avg_prices):.5f}")
                print(f"   MA Range:            {min(avg_prices):.5f} - {max(avg_prices):.5f}")
        
        # Risk assessment
        if trades_with_pnl:
            pnl_values = [t['profit_loss'] for t in trades_with_pnl]
            volatility = statistics.stdev(pnl_values) if len(pnl_values) > 1 else 0
            
            print(f"\n⚠️ Risk Metrics:")
            print(f"   P&L Volatility:      ${volatility:.2f}")
            print(f"   Max Drawdown:        ${self.metrics['largest_loss']:+.2f}")
            
        return self.metrics
    
    def save_results(self, filename=None):
        """
        Save trading results to JSON file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"eur_usd_trading_results_{timestamp}.json"
        
        results = {
            'session_info': {
                'start_time': self.session_start.isoformat() if self.session_start else None,
                'end_time': self.session_end.isoformat() if self.session_end else None,
                'duration_seconds': self.session_duration,
                'instrument': self.instrument,
                'position_size': self.position_size,
                'initial_balance': self.initial_balance
            },
            'metrics': self.metrics,
            'trades': self.trades
        }
        
        # Convert datetime objects to strings for JSON serialization
        for trade in results['trades']:
            if 'timestamp' in trade and isinstance(trade['timestamp'], datetime):
                trade['timestamp'] = trade['timestamp'].isoformat()
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")


def main():
    """
    Main function to run the practical trading scenario
    """
    print("🎯 Practical EUR/USD Trading Scenario")
    print("=====================================")
    print()
    print("This scenario will:")
    print("✓ Trade EUR/USD for 5 minutes")
    print("✓ Use moving average algorithm (20-point MA)")
    print("✓ Buy when price < MA, Sell when price > MA")
    print("✓ Calculate and display P&L analysis")
    print()
    
    # Create trader instance
    trader = PracticalEURUSDTrader(
        initial_balance=10000,  # $10,000 starting balance
        position_size=1000      # 1,000 units per trade
    )
    
    # Run trading session
    trader.run_trading_session()
    
    # Analyze performance
    results = trader.analyze_performance()
    
    # Save results
    trader.save_results()
    
    # Final summary
    print(f"\n🎉 Trading Scenario Complete!")
    print(f"💡 Key Insights:")
    if results:
        if results['total_profit_loss'] > 0:
            print(f"   ✅ Profitable session: +${results['total_profit_loss']:.2f}")
        else:
            print(f"   ❌ Loss session: ${results['total_profit_loss']:.2f}")
        
        print(f"   📊 Win rate: {results['win_rate']:.1f}%")
        print(f"   📈 ROI: {results['roi']:+.2f}%")
    
    print(f"\n🔧 Next Steps:")
    print(f"   • Review the detailed trade log above")
    print(f"   • Analyze why certain trades were profitable/unprofitable")
    print(f"   • Consider adjusting the moving average window or position size")
    print(f"   • Test with different time frames or instruments")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Ensure your .env file has valid OANDA credentials")
        print("2. Check that you have sufficient API permissions")
        print("3. Verify your internet connection")