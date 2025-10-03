# Elite FnO Trading Platform

A professional-grade Futures & Options trading platform with premium features, paper trading, and real-time signals.

## Features

- Real-time market data with multiple provider fallback
- Advanced technical analysis with multiple indicators
- Paper trading system with virtual portfolio
- Premium subscription management
- Telegram integration for alerts
- Auto-recovery and health monitoring

## Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/fno-trading-platform.git
cd fno-trading-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings:
   - Copy `config/settings.example.py` to `config/settings.py`
   - Add your API keys and credentials

4. Start the platform:
```bash
python run_premium.py
```

## Environment Variables

Required environment variables:
- `KITE_API_KEY`: Your Zerodha Kite API key
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `RAZORPAY_KEY_ID`: Your Razorpay key ID

## Development

The platform consists of several components:
- Signal Generation Engine
- Market Analysis Engine
- Paper Trading System
- Premium Features Manager
- Task Scheduler

## Deployment

For production deployment:
1. Set up a proper WSGI server (e.g., Gunicorn)
2. Configure a reverse proxy (e.g., Nginx)
3. Set up SSL certificates
4. Configure environment variables

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.