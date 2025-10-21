"""
High-Frequency Real-Time Data Streaming with OANDA API
=====================================================

This module demonstrates how to stream real-time market data from OANDA
for high-frequency trading applications, tick analysis, and live market monitoring.

Features:
- Real-time tick streaming
- Data processing and analysis
- Price movement detection
- Live volatility monitoring
- Streaming controls and error handling
"""

import pandas as pd
import time
import threading
import signal
import sys
from datetime import datetime, timedelta
from collections import deque
from oanda_trading.oanda_connection import OandaAPI

class RealTimeDataStreamer:
    """
    High-frequency real-time data streamer for OANDA API
    """
    
    def __init__(self, instruments=None):
        """
        Initialize the real-time data streamer
        
        Args:
            instruments (list): List of instruments to stream (default: ['EUR_USD'])
        """
        self.api = OandaAPI()
        self.instruments = instruments or ['EUR_USD']
        self.is_streaming = False
        self.tick_count = 0
        self.start_time = None
        
        # Data storage for analysis
        self.tick_buffer = deque(maxlen=1000)  # Store last 1000 ticks
        self.price_history = {}
        
        # Statistics tracking
        self.stats = {
            'total_ticks': 0,
            'start_time': None,
            'last_tick_time': None,
            'avg_ticks_per_second': 0,
            'price_changes': 0,
            'max_spread': 0,
            'min_spread': float('inf')
        }
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}. Stopping stream...")
        self.stop_stream()
        sys.exit(0)
    
    def _process_tick(self, tick_data):
        """
        Process incoming tick data
        
        Args:
            tick_data: Raw tick data from OANDA stream
        """
        try:
            # Extract tick information
            instrument = tick_data.get('instrument', 'UNKNOWN')
            bid = float(tick_data.get('bid', {}).get('o', 0))
            ask = float(tick_data.get('ask', {}).get('o', 0))
            timestamp = tick_data.get('time', datetime.now().isoformat())
            
            # Calculate spread
            spread = ask - bid
            mid_price = (bid + ask) / 2
            
            # Create tick record
            tick_record = {
                'timestamp': timestamp,
                'instrument': instrument,
                'bid': bid,
                'ask': ask,
                'spread': spread,
                'mid_price': mid_price,
                'tick_number': self.tick_count
            }
            
            # Store in buffer
            self.tick_buffer.append(tick_record)
            
            # Update statistics
            self._update_statistics(tick_record)
            
            # Process price movements
            self._analyze_price_movement(tick_record)
            
            # Display tick (every 10th tick to avoid spam)
            if self.tick_count % 10 == 0:
                self._display_tick(tick_record)
            
            self.tick_count += 1
            
        except Exception as e:
            print(f"❌ Error processing tick: {e}")
    
    def _update_statistics(self, tick_record):
        """Update streaming statistics"""
        now = datetime.now()
        
        if self.stats['start_time'] is None:
            self.stats['start_time'] = now
        
        self.stats['last_tick_time'] = now
        self.stats['total_ticks'] += 1
        
        # Calculate ticks per second
        elapsed = (now - self.stats['start_time']).total_seconds()
        if elapsed > 0:
            self.stats['avg_ticks_per_second'] = self.stats['total_ticks'] / elapsed
        
        # Update spread statistics
        spread = tick_record['spread']
        self.stats['max_spread'] = max(self.stats['max_spread'], spread)
        self.stats['min_spread'] = min(self.stats['min_spread'], spread)
    
    def _analyze_price_movement(self, tick_record):
        """Analyze price movements and detect significant changes"""
        instrument = tick_record['instrument']
        current_price = tick_record['mid_price']
        
        if instrument not in self.price_history:
            self.price_history[instrument] = {
                'last_price': current_price,
                'price_changes': 0,
                'significant_moves': 0,
                'volatility_buffer': deque(maxlen=100)
            }
            return
        
        last_price = self.price_history[instrument]['last_price']
        price_change = abs(current_price - last_price)
        
        # Store price change for volatility calculation
        if last_price > 0:
            pct_change = (current_price - last_price) / last_price * 100
            self.price_history[instrument]['volatility_buffer'].append(pct_change)
        
        # Detect significant price movements (threshold: 0.0005 for major pairs)
        threshold = 0.0005
        if price_change > threshold:
            self.price_history[instrument]['significant_moves'] += 1
            direction = "↗️ UP" if current_price > last_price else "↘️ DOWN"
            print(f"🔥 Significant move in {instrument}: {direction} "
                  f"{price_change:.5f} ({pct_change:.3f}%)")
        
        # Update price history
        self.price_history[instrument]['last_price'] = current_price
        if price_change > 0:
            self.price_history[instrument]['price_changes'] += 1
    
    def _display_tick(self, tick_record):
        """Display tick information"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {tick_record['instrument']} | "
              f"Bid: {tick_record['bid']:.5f} | "
              f"Ask: {tick_record['ask']:.5f} | "
              f"Spread: {tick_record['spread']:.5f} | "
              f"Tick #{tick_record['tick_number']}")
    
    def get_current_volatility(self, instrument):
        """Calculate current volatility for an instrument"""
        if instrument not in self.price_history:
            return 0
        
        changes = list(self.price_history[instrument]['volatility_buffer'])
        if len(changes) < 2:
            return 0
        
        return pd.Series(changes).std()
    
    def get_streaming_stats(self):
        """Get current streaming statistics"""
        elapsed = 0
        if self.stats['start_time']:
            elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'total_ticks': self.stats['total_ticks'],
            'elapsed_time': f"{elapsed:.1f}s",
            'avg_ticks_per_second': f"{self.stats['avg_ticks_per_second']:.2f}",
            'max_spread': f"{self.stats['max_spread']:.5f}",
            'min_spread': f"{self.stats['min_spread']:.5f}",
            'buffer_size': len(self.tick_buffer),
            'instruments_tracked': len(self.price_history)
        }
    
    def start_stream(self, duration=None, max_ticks=None):
        """
        Start real-time data streaming
        
        Args:
            duration (int): Maximum duration in seconds (None for infinite)
            max_ticks (int): Maximum number of ticks to process (None for infinite)
        """
        print("🚀 Starting Real-Time Data Stream")
        print("=" * 50)
        print(f"Instruments: {', '.join(self.instruments)}")
        if duration:
            print(f"Duration: {duration} seconds")
        if max_ticks:
            print(f"Max ticks: {max_ticks}")
        print("Press Ctrl+C to stop streaming\n")
        
        self.is_streaming = True
        self.start_time = datetime.now()
        self.stats['start_time'] = self.start_time
        
        try:
            for instrument in self.instruments:
                print(f"📡 Starting stream for {instrument}...")
                
                # Start streaming for each instrument
                # Note: In practice, you'd want to stream multiple instruments in separate threads
                self.api.stream_data(
                    instrument=instrument,
                    stop=max_ticks,  # Number of ticks before stopping
                    ret=False  # Don't return data, process in real-time
                )
                
        except KeyboardInterrupt:
            print("\n🛑 Stream interrupted by user")
        except Exception as e:
            print(f"❌ Streaming error: {e}")
        finally:
            self.stop_stream()
    
    def stop_stream(self):
        """Stop the data stream and display final statistics"""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        print("\n🏁 Streaming Session Complete")
        print("=" * 40)
        
        # Display final statistics
        stats = self.get_streaming_stats()
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Display instrument-specific statistics
        print("\n📊 Instrument Statistics:")
        for instrument, data in self.price_history.items():
            volatility = self.get_current_volatility(instrument)
            print(f"  {instrument}:")
            print(f"    Price Changes: {data['price_changes']}")
            print(f"    Significant Moves: {data['significant_moves']}")
            print(f"    Current Volatility: {volatility:.5f}")
        
        print(f"\n✅ Session ended. Total ticks processed: {self.tick_count}")


def demonstrate_basic_streaming():
    """Basic streaming demonstration"""
    print("📡 Basic Real-Time Streaming Demo")
    print("-" * 40)
    
    try:
        api = OandaAPI()
        
        print("Attempting to start EUR_USD stream...")
        print("⏰ Checking market status and streaming capabilities...")
        
        # Check if markets are likely open (rough check)
        now = datetime.now()
        is_weekend = now.weekday() >= 5  # Saturday or Sunday
        
        if is_weekend:
            print("⚠️  Weekend detected - Forex markets are likely closed")
            print("💡 Streaming typically works during:")
            print("   • Monday 00:00 UTC to Friday 22:00 UTC")
            print("   • When major forex sessions are active")
        
        print("\n🔄 Attempting stream connection...")
        
        # Try streaming with timeout handling
        try:
            # Stream for a very short time first to test connection
            api.stream_data(
                instrument='EUR_USD',
                stop=10,  # Stop after just 10 ticks for testing
                ret=False
            )
            print("✅ Streaming successful!")
            
        except Exception as stream_error:
            error_msg = str(stream_error).lower()
            
            if "timed out" in error_msg:
                print("❌ Connection timed out")
                print("🔍 Possible causes:")
                print("   • Markets are closed (weekend/holiday)")
                print("   • Network connectivity issues") 
                print("   • OANDA streaming servers unavailable")
                print("   • Practice account streaming limitations")
                
            elif "unauthorized" in error_msg or "forbidden" in error_msg:
                print("❌ Authorization error")
                print("🔍 Possible causes:")
                print("   • API key doesn't have streaming permissions")
                print("   • Practice accounts may have limited streaming access")
                print("   • Rate limits exceeded")
                
            elif "connection" in error_msg:
                print("❌ Connection error")
                print("🔍 Possible causes:")
                print("   • Internet connectivity issues")
                print("   • Firewall blocking streaming connection")
                print("   • OANDA servers maintenance")
                
            else:
                print(f"❌ Streaming error: {stream_error}")
            
            # Provide fallback demonstration
            print("\n📊 Fallback: Historical tick-like data simulation")
            demonstrate_simulated_streaming()
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        print("💡 Check your API credentials and network connection")


def demonstrate_simulated_streaming():
    """Demonstrate what streaming would look like with simulated data"""
    print("\n🎭 Simulated Streaming Demo (for demonstration)")
    print("-" * 50)
    print("This shows what real streaming output would look like:")
    
    import time
    import random
    
    # Simulate streaming with realistic EUR_USD prices
    base_bid = 1.16040
    base_ask = 1.16046
    
    print("Timestamp                    Bid      Ask     Spread")
    print("-" * 55)
    
    for i in range(20):
        # Simulate small price movements
        bid_change = random.uniform(-0.00005, 0.00005)
        ask_change = random.uniform(-0.00005, 0.00005)
        
        current_bid = base_bid + bid_change
        current_ask = base_ask + ask_change
        spread = current_ask - current_bid
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        print(f"{timestamp} {current_bid:.5f} {current_ask:.5f} {spread:.5f}")
        
        time.sleep(0.2)  # Simulate realistic tick frequency
        
        # Update base prices slightly
        base_bid += random.uniform(-0.00002, 0.00002)
        base_ask += random.uniform(-0.00002, 0.00002)
    
    print("\n💡 In live markets, this data would come directly from OANDA")
    print("   and update much more frequently (multiple times per second)")

def check_streaming_requirements():
    """Check if streaming requirements are met"""
    print("🔍 Streaming Requirements Check")
    print("-" * 35)
    
    # Check time
    now = datetime.now()
    is_weekend = now.weekday() >= 5
    hour = now.hour
    
    print(f"Current time: {now.strftime('%A, %Y-%m-%d %H:%M:%S UTC')}")
    print(f"Day of week: {now.strftime('%A')}")
    
    if is_weekend:
        print("❌ Weekend - Forex markets closed")
    else:
        print("✅ Weekday - Markets potentially open")
    
    # Check if it's likely market hours (rough estimate)
    if 0 <= hour <= 22:  # Forex markets roughly 24/5
        print("✅ Within typical forex trading hours")
    else:
        print("⚠️  Outside typical active trading hours")
    
    print("\n📋 For successful streaming you need:")
    print("  ✓ Active market hours (Mon-Fri)")
    print("  ✓ Valid OANDA API credentials")
    print("  ✓ Streaming permissions on your account")
    print("  ✓ Stable internet connection")
    print("  ✓ No rate limiting")
    
    return not is_weekend


def demonstrate_multi_instrument_monitoring():
    """Demonstrate monitoring multiple instruments"""
    print("📊 Multi-Instrument Real-Time Monitoring")
    print("-" * 45)
    
    # Create streamer for multiple major pairs
    instruments = ['EUR_USD', 'GBP_USD', 'USD_JPY']
    streamer = RealTimeDataStreamer(instruments)
    
    print("🎯 Monitoring major currency pairs for price movements...")
    print("This will track spreads, volatility, and significant price changes.")
    
    try:
        # Stream for a limited time
        streamer.start_stream(duration=60, max_ticks=100)
    except Exception as e:
        print(f"❌ Error: {e}")


def demonstrate_tick_analysis():
    """Demonstrate tick-by-tick analysis"""
    print("🔬 High-Frequency Tick Analysis")
    print("-" * 35)
    
    class TickAnalyzer(RealTimeDataStreamer):
        def __init__(self):
            super().__init__(['EUR_USD'])
            self.tick_intervals = []
            self.last_tick_time = None
        
        def _process_tick(self, tick_data):
            """Enhanced tick processing with timing analysis"""
            current_time = datetime.now()
            
            if self.last_tick_time:
                interval = (current_time - self.last_tick_time).total_seconds()
                self.tick_intervals.append(interval)
                
                # Calculate average tick frequency
                if len(self.tick_intervals) >= 10:
                    avg_interval = sum(self.tick_intervals[-10:]) / 10
                    freq = 1 / avg_interval if avg_interval > 0 else 0
                    
                    if self.tick_count % 20 == 0:
                        print(f"📈 Tick frequency: {freq:.2f} ticks/second")
            
            self.last_tick_time = current_time
            
            # Call parent processing
            super()._process_tick(tick_data)
    
    analyzer = TickAnalyzer()
    
    try:
        print("Analyzing tick timing and frequency patterns...")
        analyzer.start_stream(max_ticks=50)
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main demonstration function"""
    api = OandaAPI()
    
    print("🌊 OANDA High-Frequency Real-Time Data Streaming")
    print("=" * 55)
    print(f"Connected to: {api.get_account_info('account_type')} account")
    print(f"Account ID: {api.get_account_info('account_id')}")
    print()
    
    # Check streaming requirements first
    print("🔍 Checking Streaming Requirements...")
    print("-" * 40)
    markets_open = check_streaming_requirements()
    
    print("\n📋 Available Demonstrations:")
    demos = {
        '1': ('Basic Streaming Demo', demonstrate_basic_streaming),
        '2': ('Multi-Instrument Monitoring', demonstrate_multi_instrument_monitoring),
        '3': ('High-Frequency Tick Analysis', demonstrate_tick_analysis),
    }
    
    for key, (name, _) in demos.items():
        print(f"  {key}. {name}")
    
    if not markets_open:
        print("\n⚠️  Markets appear to be closed!")
        print("💡 Streaming will use simulated data for demonstration")
        print("   In live market hours, you would see real tick data")
    
    print("\n🔧 Technical Notes:")
    print("  • Practice accounts may have streaming limitations")
    print("  • Some OANDA endpoints require live account access")
    print("  • Network timeouts are common during market closures")
    
    # Run basic streaming demo
    print("\n" + "="*60)
    demonstrate_basic_streaming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Ensure your .env file has valid OANDA credentials")
        print("2. Make sure markets are open for live streaming")
        print("3. Check your internet connection")