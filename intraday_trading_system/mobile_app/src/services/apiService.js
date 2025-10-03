/**
 * API Service for communicating with the trading bot backend
 */

import axios from 'axios';
import { Alert } from 'react-native';

const BASE_URL = 'http://localhost:5000/api'; // Change this to your server URL

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        return response.data;
      },
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        
        if (error.response?.status === 500) {
          Alert.alert('Server Error', 'Something went wrong on the server.');
        } else if (!error.response) {
          Alert.alert('Network Error', 'Unable to connect to the trading bot server.');
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Bot Status
  async getBotStatus() {
    try {
      const response = await this.client.get('/status');
      return response;
    } catch (error) {
      console.error('Failed to get bot status:', error);
      return null;
    }
  }

  // Trading Signals
  async getSignals(limit = 50, status = null) {
    try {
      const params = { limit };
      if (status) {
        params.status = status;
      }
      
      const response = await this.client.get('/signals', { params });
      return response.signals || [];
    } catch (error) {
      console.error('Failed to get signals:', error);
      return [];
    }
  }

  // Market Data
  async getMarketData() {
    try {
      const response = await this.client.get('/market-data');
      return response.data || {};
    } catch (error) {
      console.error('Failed to get market data:', error);
      return {};
    }
  }

  // Performance Data
  async getPerformance(days = 30) {
    try {
      const response = await this.client.get('/performance', { params: { days } });
      return response.performance || {};
    } catch (error) {
      console.error('Failed to get performance data:', error);
      return {};
    }
  }

  // Send Test Message
  async sendTestMessage() {
    try {
      const response = await this.client.post('/send-test-message');
      return response.success;
    } catch (error) {
      console.error('Failed to send test message:', error);
      return false;
    }
  }

  // Bot Control
  async startBot() {
    try {
      const response = await this.client.post('/bot/start');
      return response.success;
    } catch (error) {
      console.error('Failed to start bot:', error);
      return false;
    }
  }

  async stopBot() {
    try {
      const response = await this.client.post('/bot/stop');
      return response.success;
    } catch (error) {
      console.error('Failed to stop bot:', error);
      return false;
    }
  }

  // Update server URL (for settings)
  updateBaseURL(newURL) {
    this.client.defaults.baseURL = newURL;
  }
}

export const apiService = new ApiService();