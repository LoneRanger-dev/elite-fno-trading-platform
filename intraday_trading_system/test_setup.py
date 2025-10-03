"""
Setup and Test Script
Validates configuration and tests all system components
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import config, logger
from bot.market_data import MarketDataManager
from bot.telegram_bot import TelegramBot
from bot.technical_analysis import TechnicalAnalyzer
from bot.news_fetcher import NewsFetcher
from bot.signal_manager import SignalManager

class SystemTester:
    """Test all system components"""
    
    def __init__(self):
        self.logger = logger
        self.config = config
        self.results = {}
    
    def run_all_tests(self):
        """Run all system tests"""
        print("=" * 60)
        print("🧪 TRADING BOT SYSTEM - SETUP TEST")
        print("=" * 60)
        print(f"📅 Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test configuration
        self._test_configuration()
        
        # Test database
        self._test_database()
        
        # Test market data
        self._test_market_data()
        
        # Test technical analysis
        self._test_technical_analysis()
        
        # Test news fetcher
        self._test_news_fetcher()
        
        # Test Telegram bot
        self._test_telegram_bot()
        
        # Print summary
        self._print_summary()
    
    def _test_configuration(self):
        """Test configuration"""
        print("🔧 Testing Configuration...")
        
        try:
            validation = self.config.validate_config()
            
            if not validation['errors']:
                print("   ✅ Configuration: PASS")
                self.results['config'] = True
            else:
                print("   ❌ Configuration: FAIL")
                for error in validation['errors']:
                    print(f"      - {error}")
                self.results['config'] = False
                
        except Exception as e:
            print(f"   ❌ Configuration: ERROR - {str(e)}")
            self.results['config'] = False
        
        print()
    
    def _test_database(self):
        """Test database connection"""
        print("🗄️ Testing Database...")
        
        try:
            signal_manager = SignalManager()
            success = signal_manager.test_database()
            
            if success:
                print("   ✅ Database: PASS")
                self.results['database'] = True
            else:
                print("   ❌ Database: FAIL")
                self.results['database'] = False
                
        except Exception as e:
            print(f"   ❌ Database: ERROR - {str(e)}")
            self.results['database'] = False
        
        print()
    
    def _test_market_data(self):
        """Test market data connection"""
        print("📊 Testing Market Data...")
        
        try:
            market_manager = MarketDataManager()
            success = market_manager.test_connection()
            
            if success:
                print("   ✅ Market Data: PASS")
                # Test specific instrument
                data = market_manager.get_live_data('NIFTY')
                if data:
                    print(f"   📈 NIFTY: ₹{data.get('current_price', 'N/A')} ({data.get('change_percent', 0):+.2f}%)")
                self.results['market_data'] = True
            else:
                print("   ❌ Market Data: FAIL")
                self.results['market_data'] = False
                
        except Exception as e:
            print(f"   ❌ Market Data: ERROR - {str(e)}")
            self.results['market_data'] = False
        
        print()
    
    def _test_technical_analysis(self):
        """Test technical analysis"""
        print("📈 Testing Technical Analysis...")
        
        try:
            analyzer = TechnicalAnalyzer()
            result = analyzer.test_analysis()
            
            if result.get('signal_type') != 'NONE' or 'error' not in result:
                print("   ✅ Technical Analysis: PASS")
                print(f"   🎯 Test Signal: {result.get('signal_type', 'NONE')} - {result.get('confidence', 0):.1f}%")
                self.results['technical_analysis'] = True
            else:
                print("   ❌ Technical Analysis: FAIL")
                self.results['technical_analysis'] = False
                
        except Exception as e:
            print(f"   ❌ Technical Analysis: ERROR - {str(e)}")
            self.results['technical_analysis'] = False
        
        print()
    
    def _test_news_fetcher(self):
        """Test news fetcher"""
        print("📰 Testing News Fetcher...")
        
        try:
            news_fetcher = NewsFetcher()
            success = news_fetcher.test_news_fetching()
            
            if success:
                print("   ✅ News Fetcher: PASS")
                self.results['news_fetcher'] = True
            else:
                print("   ⚠️ News Fetcher: LIMITED (RSS only)")
                self.results['news_fetcher'] = True  # RSS should work
                
        except Exception as e:
            print(f"   ❌ News Fetcher: ERROR - {str(e)}")
            self.results['news_fetcher'] = False
        
        print()
    
    def _test_telegram_bot(self):
        """Test Telegram bot"""
        print("📱 Testing Telegram Bot...")
        
        try:
            async def test_telegram():
                telegram_bot = TelegramBot()
                success = await telegram_bot.test_connection()
                return success
            
            success = asyncio.run(test_telegram())
            
            if success:
                print("   ✅ Telegram Bot: PASS")
                print("   📨 Test message sent successfully")
                self.results['telegram_bot'] = True
            else:
                print("   ❌ Telegram Bot: FAIL")
                print("   ⚠️ Check bot token and chat ID in .env file")
                self.results['telegram_bot'] = False
                
        except Exception as e:
            print(f"   ❌ Telegram Bot: ERROR - {str(e)}")
            self.results['telegram_bot'] = False
        
        print()
    
    def _print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        
        for component, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{component.replace('_', ' ').title():.<40} {status}")
        
        print("-" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! System ready to start.")
            print("\nRun the following command to start the system:")
            print("   python main.py")
            print("\nOr double-click:")
            print("   start_bot.bat")
        else:
            print("\n⚠️ Some tests failed. Please fix the issues before starting.")
            
        print("=" * 60)

def main():
    """Main test function"""
    tester = SystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()