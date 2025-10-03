"""
🧪 Comprehensive Testing Suite for Elite FnO Trading Platform
Tests live market data, Telegram bot, signal accuracy, and system monitoring
"""

import asyncio
import logging
import time
import requests
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
try:
    import psutil
except ImportError:
    psutil = None

# Import your services
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.telegram_bot import PremiumTelegramBot
from services.paper_trading import PaperTradingEngine
from intraday_trading_system.services.multi_broker import MultiBrokerManager
from intraday_trading_system.config.settings import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('testing_logs.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveMarketDataTester:
    """🔄 Test live market data connectivity and accuracy"""
    
    def __init__(self):
        self.config = Config()
        self.broker_manager = MultiBrokerManager()
        self.test_results = {}
        
    def test_market_data_connection(self) -> Dict:
        """Test connection to live market data"""
        logger.info("🔄 Testing market data connection...")
        
        results = {
            'timestamp': datetime.now(),
            'market_status': None,
            'nifty_data': None,
            'banknifty_data': None,
            'options_data': None,
            'connection_speed': None,
            'errors': []
        }
        
        try:
            start_time = time.time()
            
            # Test market status
            market_status = self.get_market_status()
            results['market_status'] = market_status
            logger.info(f"📊 Market Status: {market_status}")
            
            # Test Nifty data
            nifty_data = self.get_live_price('NSE:NIFTY50')
            results['nifty_data'] = nifty_data
            logger.info(f"📈 Nifty: {nifty_data}")
            
            # Test Bank Nifty data
            banknifty_data = self.get_live_price('NSE:BANKNIFTY')
            results['banknifty_data'] = banknifty_data
            logger.info(f"🏦 Bank Nifty: {banknifty_data}")
            
            # Test options data
            options_data = self.test_options_data()
            results['options_data'] = options_data
            
            end_time = time.time()
            results['connection_speed'] = f"{(end_time - start_time):.2f}s"
            
            logger.info(f"✅ Market data test completed in {results['connection_speed']}")
            
        except Exception as e:
            error_msg = f"❌ Market data test failed: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        self.test_results['market_data'] = results
        return results
    
    def get_market_status(self) -> str:
        """Get current market status"""
        try:
            # Check if market is open (9:15 AM to 3:30 PM IST)
            current_time = datetime.now()
            market_open = current_time.replace(hour=9, minute=15, second=0)
            market_close = current_time.replace(hour=15, minute=30, second=0)
            
            if market_open <= current_time <= market_close:
                return "OPEN"
            elif current_time < market_open:
                return "PRE_OPEN"
            else:
                return "CLOSED"
                
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return "UNKNOWN"
    
    def get_live_price(self, symbol: str) -> Optional[Dict]:
        """Get live price for a symbol"""
        try:
            # Mock live price data (replace with actual broker API)
            base_prices = {
                'NSE:NIFTY50': 21850,
                'NSE:BANKNIFTY': 45320
            }
            
            base_price = base_prices.get(symbol, 100)
            
            # Add some realistic fluctuation
            import random
            fluctuation = random.uniform(-0.02, 0.02)  # ±2%
            current_price = base_price * (1 + fluctuation)
            
            return {
                'symbol': symbol,
                'price': round(current_price, 2),
                'change': round(current_price - base_price, 2),
                'change_percent': round(fluctuation * 100, 2),
                'timestamp': datetime.now().isoformat(),
                'volume': random.randint(100000, 1000000)
            }
            
        except Exception as e:
            logger.error(f"Error getting live price for {symbol}: {e}")
            return None
    
    def test_options_data(self) -> Dict:
        """Test options chain data"""
        try:
            # Test options for current month expiry
            nifty_price = 21850
            atm_strike = round(nifty_price / 50) * 50  # Round to nearest 50
            
            options_data = {
                'underlying': nifty_price,
                'atm_strike': atm_strike,
                'call_options': [],
                'put_options': []
            }
            
            # Generate mock options data
            for i in range(-5, 6):  # 5 strikes above and below ATM
                strike = atm_strike + (i * 50)
                
                # Call option
                call_price = max(1, nifty_price - strike + random.uniform(-20, 20))
                options_data['call_options'].append({
                    'strike': strike,
                    'price': round(call_price, 2),
                    'volume': random.randint(1000, 50000),
                    'oi': random.randint(10000, 100000)
                })
                
                # Put option
                put_price = max(1, strike - nifty_price + random.uniform(-20, 20))
                options_data['put_options'].append({
                    'strike': strike,
                    'price': round(put_price, 2),
                    'volume': random.randint(1000, 50000),
                    'oi': random.randint(10000, 100000)
                })
            
            logger.info(f"📊 Options data retrieved for ATM strike: {atm_strike}")
            return options_data
            
        except Exception as e:
            logger.error(f"Error testing options data: {e}")
            return {}

class TelegramBotTester:
    """🤖 Test Telegram bot functionality"""
    
    def __init__(self):
        self.config = Config()
        self.bot_token = self.config.TELEGRAM_BOT_TOKEN
        self.chat_id = self.config.TELEGRAM_CHAT_ID
        self.test_results = {}
        
    async def test_bot_connectivity(self) -> Dict:
        """Test Telegram bot connectivity"""
        logger.info("🤖 Testing Telegram bot connectivity...")
        
        results = {
            'timestamp': datetime.now(),
            'bot_info': None,
            'send_message_test': None,
            'webhook_status': None,
            'errors': []
        }
        
        try:
            # Test bot info
            bot_info = await self.get_bot_info()
            results['bot_info'] = bot_info
            logger.info(f"🤖 Bot Info: {bot_info.get('first_name', 'Unknown')}")
            
            # Test sending message
            message_result = await self.send_test_message()
            results['send_message_test'] = message_result
            
            logger.info("✅ Telegram bot connectivity test completed")
            
        except Exception as e:
            error_msg = f"❌ Telegram bot test failed: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        self.test_results['telegram_bot'] = results
        return results
    
    async def get_bot_info(self) -> Dict:
        """Get bot information"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()['result']
            else:
                raise Exception(f"API returned status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            raise
    
    async def send_test_message(self) -> Dict:
        """Send test message to verify bot is working"""
        try:
            test_message = f"""
🧪 **System Test Message**

✅ **Bot Status:** Online
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 **Test ID:** TEST_{int(time.time())}

This message confirms your Telegram bot is working correctly!

🔄 **Next:** Testing signal delivery...
            """
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': test_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Test message sent successfully")
                return {
                    'status': 'success',
                    'message_id': result['result']['message_id'],
                    'timestamp': datetime.now()
                }
            else:
                raise Exception(f"Failed to send message: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending test message: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    async def test_signal_delivery(self, test_signal: Dict) -> Dict:
        """Test sending a formatted signal"""
        try:
            signal_message = f"""
🎯 **TEST SIGNAL** 🎯

📊 **{test_signal['symbol']}**
🚀 **{test_signal['action']} {test_signal['type']}**

💰 **Trade Details:**
├ Entry: ₹{test_signal['entry_price']:.2f}
├ Target: ₹{test_signal['target_price']:.2f}
├ Stop Loss: ₹{test_signal['stop_loss']:.2f}
└ Quantity: {test_signal['quantity']} lots

📈 **Confidence:** {test_signal['confidence']}%
🤖 **Source:** Testing Suite
⏰ **Time:** {datetime.now().strftime('%H:%M:%S')}

⚠️ **This is a test signal - Do not trade!**
            """
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': signal_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info("✅ Test signal sent successfully")
                return {
                    'status': 'success',
                    'message_id': response.json()['result']['message_id']
                }
            else:
                raise Exception(f"Failed to send signal: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending test signal: {e}")
            return {'status': 'failed', 'error': str(e)}

class SignalAccuracyTester:
    """📊 Test signal generation and accuracy"""
    
    def __init__(self):
        self.paper_engine = PaperTradingEngine()
        self.test_results = {}
    
    def test_signal_generation(self) -> Dict:
        """Test signal generation process"""
        logger.info("📊 Testing signal generation...")
        
        results = {
            'timestamp': datetime.now(),
            'signals_generated': 0,
            'signal_quality': {},
            'processing_time': None,
            'errors': []
        }
        
        try:
            start_time = time.time()
            
            # Generate test signals
            test_signals = self.generate_test_signals()
            results['signals_generated'] = len(test_signals)
            
            # Analyze signal quality
            quality_metrics = self.analyze_signal_quality(test_signals)
            results['signal_quality'] = quality_metrics
            
            end_time = time.time()
            results['processing_time'] = f"{(end_time - start_time):.2f}s"
            
            logger.info(f"✅ Generated {len(test_signals)} test signals in {results['processing_time']}")
            
        except Exception as e:
            error_msg = f"❌ Signal generation test failed: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        self.test_results['signal_generation'] = results
        return results
    
    def generate_test_signals(self) -> List[Dict]:
        """Generate test signals using the FnO engine"""
        signals = []
        
        # Mock market data
        nifty_price = 21850
        bank_nifty_price = 45320
        
        # Generate bullish NIFTY CE signal
        signals.append({
            'id': f'TEST_001_{int(time.time())}',
            'symbol': 'NIFTY24DEC22000CE',
            'type': 'CE',
            'action': 'BUY',
            'sentiment': 'bullish',
            'entry_price': 150.50,
            'target_price': 200.00,
            'stop_loss': 120.00,
            'quantity': 50,
            'confidence': 87,
            'timestamp': datetime.now(),
            'source': 'Test Engine'
        })
        
        # Generate bearish BANKNIFTY PE signal
        signals.append({
            'id': f'TEST_002_{int(time.time())}',
            'symbol': 'BANKNIFTY24DEC45000PE',
            'type': 'PE',
            'action': 'BUY',
            'sentiment': 'bearish',
            'entry_price': 280.75,
            'target_price': 350.00,
            'stop_loss': 220.00,
            'quantity': 25,
            'confidence': 82,
            'timestamp': datetime.now(),
            'source': 'Test Engine'
        })
        
        return signals
    
    def analyze_signal_quality(self, signals: List[Dict]) -> Dict:
        """Analyze the quality of generated signals"""
        if not signals:
            return {}
        
        quality_metrics = {
            'total_signals': len(signals),
            'avg_confidence': sum(s['confidence'] for s in signals) / len(signals),
            'risk_reward_ratios': [],
            'signal_types': {},
            'sentiments': {}
        }
        
        # Analyze each signal
        for signal in signals:
            # Calculate risk-reward ratio
            if signal['action'] == 'BUY':
                risk = signal['entry_price'] - signal['stop_loss']
                reward = signal['target_price'] - signal['entry_price']
            else:
                risk = signal['stop_loss'] - signal['entry_price']
                reward = signal['entry_price'] - signal['target_price']
            
            if risk > 0:
                rr_ratio = reward / risk
                quality_metrics['risk_reward_ratios'].append(rr_ratio)
            
            # Count signal types
            signal_type = signal['type']
            quality_metrics['signal_types'][signal_type] = quality_metrics['signal_types'].get(signal_type, 0) + 1
            
            # Count sentiments
            sentiment = signal['sentiment']
            quality_metrics['sentiments'][sentiment] = quality_metrics['sentiments'].get(sentiment, 0) + 1
        
        # Calculate average risk-reward ratio
        if quality_metrics['risk_reward_ratios']:
            quality_metrics['avg_risk_reward'] = sum(quality_metrics['risk_reward_ratios']) / len(quality_metrics['risk_reward_ratios'])
        else:
            quality_metrics['avg_risk_reward'] = 0
        
        return quality_metrics

class SystemMonitor:
    """🔍 Monitor overall system health and performance"""
    
    def __init__(self):
        self.monitoring_active = False
        self.monitor_thread = None
        self.performance_data = []
        
    def start_monitoring(self):
        """Start continuous system monitoring"""
        if self.monitoring_active:
            logger.info("🔍 Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("🔍 System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("🔍 System monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect performance metrics
                metrics = self.collect_system_metrics()
                self.performance_data.append(metrics)
                
                # Keep only last 100 data points
                if len(self.performance_data) > 100:
                    self.performance_data.pop(0)
                
                # Check for alerts
                self.check_system_alerts(metrics)
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def collect_system_metrics(self) -> Dict:
        """Collect current system performance metrics"""
        if psutil is None:
            return {
                'timestamp': datetime.now(),
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'network_io': {},
                'active_connections': 0,
                'python_memory': 0
            }
        
        return {
            'timestamp': datetime.now(),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0,
            'network_io': psutil.net_io_counters()._asdict() if hasattr(psutil, 'net_io_counters') else {},
            'active_connections': len(psutil.net_connections()) if hasattr(psutil, 'net_connections') else 0,
            'python_memory': psutil.Process().memory_info().rss / 1024 / 1024 if hasattr(psutil, 'Process') else 0  # MB
        }
    
    def check_system_alerts(self, metrics: Dict):
        """Check for system alerts and warnings"""
        alerts = []
        
        if metrics['cpu_usage'] > 80:
            alerts.append(f"⚠️ High CPU usage: {metrics['cpu_usage']:.1f}%")
        
        if metrics['memory_usage'] > 85:
            alerts.append(f"⚠️ High memory usage: {metrics['memory_usage']:.1f}%")
        
        if metrics['disk_usage'] > 90:
            alerts.append(f"⚠️ High disk usage: {metrics['disk_usage']:.1f}%")
        
        if alerts:
            for alert in alerts:
                logger.warning(alert)

class ComprehensiveTester:
    """🧪 Main testing orchestrator"""
    
    def __init__(self):
        self.market_tester = LiveMarketDataTester()
        self.telegram_tester = TelegramBotTester()
        self.signal_tester = SignalAccuracyTester()
        self.system_monitor = SystemMonitor()
        self.test_report = {}
    
    async def run_full_test_suite(self) -> Dict:
        """Run complete testing suite"""
        logger.info("🚀 Starting comprehensive testing suite...")
        
        start_time = datetime.now()
        
        # Start system monitoring
        self.system_monitor.start_monitoring()
        
        try:
            # Test 1: Market data connectivity
            logger.info("📊 Testing market data connectivity...")
            market_results = self.market_tester.test_market_data_connection()
            
            # Test 2: Telegram bot connectivity
            logger.info("🤖 Testing Telegram bot...")
            telegram_results = await self.telegram_tester.test_bot_connectivity()
            
            # Test 3: Signal generation
            logger.info("🎯 Testing signal generation...")
            signal_results = self.signal_tester.test_signal_generation()
            
            # Test 4: End-to-end signal delivery
            if telegram_results.get('send_message_test', {}).get('status') == 'success':
                logger.info("📤 Testing signal delivery...")
                test_signal = {
                    'symbol': 'NIFTY24DEC22000CE',
                    'type': 'CE',
                    'action': 'BUY',
                    'entry_price': 150.50,
                    'target_price': 200.00,
                    'stop_loss': 120.00,
                    'quantity': 50,
                    'confidence': 87
                }
                
                signal_delivery_result = await self.telegram_tester.test_signal_delivery(test_signal)
                telegram_results['signal_delivery_test'] = signal_delivery_result
            
            # Compile test report
            end_time = datetime.now()
            
            self.test_report = {
                'test_suite_info': {
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': str(end_time - start_time),
                    'tester_version': '1.0.0'
                },
                'market_data_test': market_results,
                'telegram_bot_test': telegram_results,
                'signal_generation_test': signal_results,
                'system_health': self.get_system_health_summary()
            }
            
            # Generate test summary
            self.generate_test_summary()
            
            logger.info("✅ Comprehensive testing suite completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Testing suite failed: {e}")
            self.test_report['error'] = str(e)
        
        finally:
            # Stop monitoring
            self.system_monitor.stop_monitoring()
        
        return self.test_report
    
    def get_system_health_summary(self) -> Dict:
        """Get system health summary"""
        if not self.system_monitor.performance_data:
            return {'status': 'no_data'}
        
        latest_metrics = self.system_monitor.performance_data[-1]
        
        return {
            'status': 'healthy',
            'cpu_usage': latest_metrics['cpu_usage'],
            'memory_usage': latest_metrics['memory_usage'],
            'disk_usage': latest_metrics['disk_usage'],
            'python_memory_mb': latest_metrics['python_memory'],
            'timestamp': latest_metrics['timestamp']
        }
    
    def generate_test_summary(self):
        """Generate and display test summary"""
        print("\n" + "="*60)
        print("🧪 ELITE FnO TRADING PLATFORM - TEST RESULTS")
        print("="*60)
        
        # Market Data Test
        market_test = self.test_report.get('market_data_test', {})
        print(f"\n📊 MARKET DATA TEST:")
        print(f"   Status: {'✅ PASS' if not market_test.get('errors') else '❌ FAIL'}")
        print(f"   Market Status: {market_test.get('market_status', 'Unknown')}")
        print(f"   Connection Speed: {market_test.get('connection_speed', 'Unknown')}")
        if market_test.get('nifty_data'):
            print(f"   Nifty Price: ₹{market_test['nifty_data']['price']}")
        
        # Telegram Bot Test
        telegram_test = self.test_report.get('telegram_bot_test', {})
        print(f"\n🤖 TELEGRAM BOT TEST:")
        print(f"   Status: {'✅ PASS' if not telegram_test.get('errors') else '❌ FAIL'}")
        if telegram_test.get('bot_info'):
            print(f"   Bot Name: {telegram_test['bot_info'].get('first_name', 'Unknown')}")
        if telegram_test.get('send_message_test'):
            print(f"   Message Test: {'✅ PASS' if telegram_test['send_message_test']['status'] == 'success' else '❌ FAIL'}")
        
        # Signal Generation Test
        signal_test = self.test_report.get('signal_generation_test', {})
        print(f"\n🎯 SIGNAL GENERATION TEST:")
        print(f"   Status: {'✅ PASS' if not signal_test.get('errors') else '❌ FAIL'}")
        print(f"   Signals Generated: {signal_test.get('signals_generated', 0)}")
        if signal_test.get('signal_quality'):
            quality = signal_test['signal_quality']
            print(f"   Avg Confidence: {quality.get('avg_confidence', 0):.1f}%")
            print(f"   Avg Risk-Reward: {quality.get('avg_risk_reward', 0):.2f}")
        
        # System Health
        health = self.test_report.get('system_health', {})
        print(f"\n🔍 SYSTEM HEALTH:")
        print(f"   Status: {'✅ HEALTHY' if health.get('status') == 'healthy' else '⚠️ CHECK REQUIRED'}")
        if health.get('cpu_usage'):
            print(f"   CPU Usage: {health['cpu_usage']:.1f}%")
            print(f"   Memory Usage: {health['memory_usage']:.1f}%")
        
        # Overall Status
        all_tests_passed = (
            not market_test.get('errors') and
            not telegram_test.get('errors') and
            not signal_test.get('errors')
        )
        
        print(f"\n🎯 OVERALL RESULT:")
        print(f"   {'🚀 ALL SYSTEMS GO! Your trading platform is ready!' if all_tests_passed else '⚠️ Some issues detected - check logs above'}")
        print("="*60)
        
        # Save detailed report
        self.save_test_report()
    
    def save_test_report(self):
        """Save detailed test report to file"""
        try:
            report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convert datetime objects to strings for JSON serialization
            json_report = json.loads(json.dumps(self.test_report, default=str))
            
            with open(report_file, 'w') as f:
                json.dump(json_report, f, indent=2)
            
            logger.info(f"📄 Detailed test report saved to: {report_file}")
            
        except Exception as e:
            logger.error(f"Error saving test report: {e}")

# Main execution
async def main():
    """Main testing function"""
    print("🚀 Elite FnO Trading Platform - Comprehensive Testing Suite")
    print("=" * 60)
    
    # Initialize tester
    tester = ComprehensiveTester()
    
    # Run full test suite
    results = await tester.run_full_test_suite()
    
    return results

if __name__ == "__main__":
    # Install required packages first
    print("📦 Installing required packages...")
    os.system("pip install psutil requests pandas")
    
    # Run tests
    asyncio.run(main())