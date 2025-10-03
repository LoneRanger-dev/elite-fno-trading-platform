# 🚀 Intraday Trading Bot System - Complete Setup Guide

This comprehensive guide will help you set up and deploy the complete Intraday Trading Bot System with web dashboard, mobile app, and Telegram automation.

## 📋 System Overview

The system consists of:
- **Trading Bot**: Core Python application with technical analysis
- **Web Dashboard**: Flask-based real-time monitoring interface
- **Mobile App**: React Native cross-platform application
- **Telegram Integration**: Automated signal broadcasting
- **Database**: SQLite for signal storage and analytics

## 🛠️ Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Git**: For version control
- **Internet Connection**: For market data and Telegram

### For Mobile Development (Optional)
- **Android Studio**: For Android app development
- **Xcode**: For iOS development (macOS only)
- **React Native CLI**: For mobile app building

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup
```powershell
# Navigate to your desired directory
cd C:\Users\Tns_Tech_Hub\Desktop\TESTWIN

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```powershell
# Copy and edit environment file
copy .env.example .env
# Edit .env file with your API keys (see Configuration section)
```

### 3. Start the System
```powershell
# Run the complete system
python main.py
```

### 4. Access Interfaces
- **Web Dashboard**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api
- **System Health**: http://localhost:5000/health

## 📖 Detailed Installation

### Step 1: Environment Setup

#### Python Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate environment (Windows)
.\venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt

# Verify installation
python test_setup.py
```

#### Dependencies Overview
```
Flask>=2.3.2              # Web framework
Flask-SocketIO>=5.3.4     # Real-time communication
python-telegram-bot>=20.3 # Telegram integration
yfinance>=0.2.18          # Market data
pandas>=2.0.3             # Data analysis
numpy>=1.24.3             # Numerical computing
scikit-learn>=1.3.0       # Machine learning
APScheduler>=3.10.1       # Task scheduling
requests>=2.31.0          # HTTP requests
python-dotenv>=1.0.0      # Environment management
```

### Step 2: Configuration

#### Environment Variables (.env)
```env
# Trading Bot Configuration
BOT_NAME=IntradayTradingBot
MARKET_START_TIME=09:15
MARKET_END_TIME=15:30
TIMEZONE=Asia/Kolkata

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_username
TELEGRAM_ENABLED=true

# Zerodha Kite Connect (Optional)
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
KITE_ACCESS_TOKEN=your_kite_access_token

# Web Dashboard
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=false
WEB_HOST=0.0.0.0
WEB_PORT=5000

# Database
DATABASE_URL=sqlite:///trading_bot.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/trading_bot.log
```

#### Getting API Keys

**Telegram Bot Setup:**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token to `.env`
4. Add bot to your channel as admin
5. Get channel ID using [@userinfobot](https://t.me/userinfobot)

**Zerodha Kite Connect (Optional):**
1. Visit [Kite Connect](https://kite.trade/)
2. Create developer account
3. Generate API credentials
4. Follow OAuth flow for access token

### Step 3: Database Setup

The system automatically creates the SQLite database:
```powershell
# Database will be created automatically on first run
# Location: ./trading_bot.db

# To reset database (if needed)
python -c "
import os
if os.path.exists('trading_bot.db'):
    os.remove('trading_bot.db')
    print('Database reset successfully')
"
```

### Step 4: System Startup

#### Manual Start
```powershell
# Start the complete system
python main.py
```

#### Windows Service (Optional)
```powershell
# Install as Windows service
python -m pip install pywin32
python service_installer.py install

# Start service
net start TradingBotService
```

#### Batch File Startup
```batch
@echo off
cd /d "C:\Users\Tns_Tech_Hub\Desktop\TESTWIN\intraday_trading_system"
call venv\Scripts\activate.bat
python main.py
pause
```

## 🌐 Web Dashboard Setup

### Features
- Real-time bot monitoring
- Live trading signals
- Performance analytics
- Manual bot controls
- System health monitoring

### Access Points
- **Main Dashboard**: http://localhost:5000
- **Signals Page**: http://localhost:5000/signals
- **Performance**: http://localhost:5000/performance
- **API Endpoints**: http://localhost:5000/api

### API Endpoints
```
GET  /api/bot/status           # Bot status
POST /api/bot/start            # Start bot
POST /api/bot/stop             # Stop bot
GET  /api/signals              # Trading signals
GET  /api/performance          # Performance metrics
GET  /api/health               # System health
```

## 📱 Mobile App Setup

### Prerequisites
```powershell
# Install Node.js and React Native CLI
npm install -g react-native-cli

# Navigate to mobile app directory
cd mobile_app

# Install dependencies
npm install
```

### Android Setup
```powershell
# Install Android dependencies
cd android
.\gradlew wrapper --gradle-version 7.4
cd ..

# Run on Android
npx react-native run-android
```

### iOS Setup (macOS only)
```bash
# Install iOS dependencies
cd ios && pod install && cd ..

# Run on iOS
npx react-native run-ios
```

### App Configuration
1. Open Settings in the mobile app
2. Update Server URL: `http://your-server-ip:5000`
3. Test connection
4. Enable notifications

## 📡 Telegram Integration

### Bot Setup
1. Create bot with [@BotFather](https://t.me/botfather)
2. Add bot to your channel as administrator
3. Configure in `.env` file

### Message Format
The bot sends rich HTML formatted messages:
```
🚀 BUY Signal - NIFTY
📊 Entry: ₹19,500
🎯 Target: ₹19,650 (+150)
🛡️ Stop Loss: ₹19,400 (-100)
📈 Confidence: 85%
⏰ Time: 10:30 AM IST
```

### Channel Management
- Signals are posted automatically
- Bot status updates
- Performance summaries
- Error notifications

## 🔍 Monitoring and Logging

### Log Files
```
logs/
├── trading_bot.log      # Main application logs
├── error.log           # Error logs
├── signals.log         # Trading signals log
└── performance.log     # Performance metrics
```

### Health Monitoring
```powershell
# Check system health
curl http://localhost:5000/health

# Monitor logs in real-time
Get-Content -Path "logs\trading_bot.log" -Wait
```

### System Metrics
- Bot uptime and status
- Signal generation rate
- API response times
- Database performance
- Memory and CPU usage

## 🛡️ Security Considerations

### API Keys
- Store all sensitive data in `.env` file
- Never commit `.env` to version control
- Use environment variables in production
- Rotate keys regularly

### Network Security
- Use HTTPS in production
- Implement rate limiting
- Add authentication for admin features
- Secure database access

### Data Protection
- Encrypt sensitive data
- Regular database backups
- Monitor access logs
- Implement data retention policies

## 🚀 Production Deployment

### Cloud Deployment Options

#### AWS EC2
```bash
# Launch EC2 instance (Ubuntu 20.04)
# Install Python and dependencies
sudo apt update && sudo apt install python3-pip python3-venv nginx

# Clone and setup application
git clone <your-repo>
cd intraday_trading_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/trading-bot

# Start application with supervisor
sudo apt install supervisor
sudo nano /etc/supervisor/conf.d/trading-bot.conf
```

#### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  trading-bot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

### Environment-Specific Configuration

#### Development
```env
FLASK_DEBUG=true
LOG_LEVEL=DEBUG
TELEGRAM_ENABLED=false
```

#### Production
```env
FLASK_DEBUG=false
LOG_LEVEL=INFO
TELEGRAM_ENABLED=true
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 📊 Performance Optimization

### Database Optimization
- Regular VACUUM operations
- Index optimization
- Query performance monitoring
- Connection pooling

### Memory Management
- Monitor memory usage
- Implement data cleanup
- Optimize pandas operations
- Cache frequently used data

### Network Optimization
- Implement caching
- Optimize API calls
- Use connection pooling
- Monitor response times

## 🐛 Troubleshooting

### Common Issues

#### Bot Won't Start
```powershell
# Check Python environment
python --version
pip list

# Verify configuration
python -c "from config.settings import Config; print(Config.validate_config())"

# Check logs
Get-Content logs\trading_bot.log -Tail 50
```

#### Telegram Not Working
```powershell
# Test bot token
python -c "
import requests
token = 'YOUR_BOT_TOKEN'
response = requests.get(f'https://api.telegram.org/bot{token}/getMe')
print(response.json())
"
```

#### Database Issues
```powershell
# Reset database
python -c "
import os
if os.path.exists('trading_bot.db'):
    os.remove('trading_bot.db')
    print('Database reset')
"
```

#### Web Dashboard Not Loading
```powershell
# Check if port is available
netstat -an | findstr :5000

# Test Flask app
curl http://localhost:5000/health
```

### Debug Mode
```powershell
# Enable debug mode
$env:FLASK_DEBUG="true"
python main.py
```

### System Diagnostics
```powershell
# Run system diagnostics
python test_setup.py

# Check all components
python -c "
from bot.main import TradingBot
from web_app.app import create_app
from bot.telegram_bot import TelegramBot
print('All components imported successfully')
"
```

## 📞 Support and Maintenance

### Regular Maintenance
- **Daily**: Check logs and bot status
- **Weekly**: Review performance metrics
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Database cleanup and optimization

### Backup Strategy
```powershell
# Backup database
copy trading_bot.db backups\trading_bot_$(Get-Date -Format "yyyy-MM-dd").db

# Backup configuration
copy .env backups\.env_$(Get-Date -Format "yyyy-MM-dd")

# Backup logs
Compress-Archive -Path logs\* -DestinationPath backups\logs_$(Get-Date -Format "yyyy-MM-dd").zip
```

### Update Process
```powershell
# Stop system
# Backup data
# Update code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Test system
python test_setup.py

# Restart system
python main.py
```

### Contact Information
- **Technical Support**: support@tradingbot.com
- **Documentation**: [GitHub Wiki](https://github.com/your-repo/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)

---

## 🎉 Success!

Your Intraday Trading Bot System is now fully configured and ready to use! 

### Quick Verification Checklist
- [ ] Trading bot starts without errors
- [ ] Web dashboard accessible at http://localhost:5000
- [ ] Telegram bot sends test messages
- [ ] Mobile app connects to server
- [ ] Database creates and stores signals
- [ ] Logs are being written
- [ ] Performance metrics are tracked

### Next Steps
1. **Customize Strategy**: Modify technical analysis parameters
2. **Add Instruments**: Configure additional trading symbols
3. **Set Alerts**: Configure custom notification rules
4. **Monitor Performance**: Track and optimize signal accuracy
5. **Scale System**: Deploy to cloud for 24/7 operation

**Happy Trading! 📈🚀**