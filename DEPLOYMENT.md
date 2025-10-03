# FnO Trading Platform Deployment Guide

## System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- Stable internet connection
- Windows/Linux/MacOS

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/your-repo/fno-trading-platform.git
cd fno-trading-platform
```

2. Create a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API Keys:
```bash
cp config_template.py config/secure/api_credentials.py
# Edit api_credentials.py with your API keys
```

Required API Keys:
- Zerodha Kite API Key and Secret
- Telegram Bot Token and Chat ID
- Razorpay API Key (for premium features)

5. Initialize databases:
```bash
python setup.py init_db
```

6. Start the platform:
```bash
# Windows
START_PLATFORM.bat
# Linux/MacOS
./start_platform.sh
```

## Configuration

### Telegram Bot Setup
1. Create a new bot via @BotFather on Telegram
2. Get the bot token and chat ID
3. Update config/secure/api_credentials.py with these values

### Zerodha Kite Setup
1. Create a Zerodha developer account
2. Generate API keys from developer console
3. Update config/secure/api_credentials.py with API key and secret

### Premium Features Setup
1. Create a Razorpay account
2. Get API keys from Razorpay dashboard
3. Update config/secure/api_credentials.py with Razorpay credentials

## Environment Variables
Create a .env file with:
```
KITE_API_KEY=your_key
KITE_API_SECRET=your_secret
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
RAZORPAY_KEY=your_key
RAZORPAY_SECRET=your_secret
```

## Directory Structure
```
├── app_premium.py       # Premium features Flask app
├── live_signal_engine.py # Signal generation engine
├── market_data_provider.py # Market data integration
├── telegram_bot.py      # Telegram notifications
├── data/               # Database files
├── logs/               # Application logs
├── templates/          # Web templates
└── static/            # Static assets
```

## Monitoring & Maintenance

### Logs
- Main log: logs/trading_platform.log
- Signal log: logs/signal_engine.log
- Error log: logs/error.log

### Health Checks
1. Dashboard: http://localhost:5500/health
2. API: http://localhost:5500/api/status
3. Telegram Bot: Send /status to your bot

### Common Issues

1. Connection Issues
```
Error: Could not connect to Kite API
Solution: Check API keys and internet connection
```

2. Database Errors
```
Error: SQLite database is locked
Solution: Restart platform, check file permissions
```

3. Memory Issues
```
Error: MemoryError in data processing
Solution: Increase available RAM, reduce concurrent operations
```

## Security Notes

1. API Key Protection
- Never commit api_credentials.py
- Use environment variables in production
- Rotate API keys regularly

2. Access Control
- Set strong admin passwords
- Enable 2FA where possible
- Restrict dashboard access by IP

3. Data Protection
- Regular database backups
- Encrypt sensitive data
- Monitor access logs

## Production Deployment

### Using Systemd (Linux)
1. Copy systemd service file:
```bash
sudo cp deployment/trading-platform.service /etc/systemd/system/
```

2. Enable and start service:
```bash
sudo systemctl enable trading-platform
sudo systemctl start trading-platform
```

### Using Docker
1. Build image:
```bash
docker build -t fno-trading-platform .
```

2. Run container:
```bash
docker run -d -p 5500:5500 fno-trading-platform
```

## Support
- Documentation: /docs
- Issues: Create GitHub issue
- Support: support@yourplatform.com

## License
MIT License - See LICENSE file for details