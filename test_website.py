"""
Test the website functionality for the FnO Trading Platform
"""
import unittest
from flask.testing import FlaskClient
from app_premium import app

class TestWebsite(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_homepage(self):
        """Test if the homepage loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_dashboard(self):
        """Test if the dashboard loads correctly"""
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
    def test_paper_trading(self):
        """Test if paper trading page loads correctly"""
        response = self.app.get('/paper-trading')
        self.assertEqual(response.status_code, 200)
        
    def test_premium_features(self):
        """Test if premium features are accessible"""
        response = self.app.get('/premium-features')
        self.assertEqual(response.status_code, 200)
        
    def test_signal_generation(self):
        """Test if signal generation is working"""
        response = self.app.get('/api/signals/latest')
        self.assertEqual(response.status_code, 200)
        
    def test_market_data(self):
        """Test if market data is available"""
        response = self.app.get('/api/market-data/status')
        self.assertEqual(response.status_code, 200)
        
if __name__ == '__main__':
    unittest.main()