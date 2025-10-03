# AI Agent Instructions for FnO Trading Platform

## Project Overview
This is a professional-grade FnO (Futures & Options) trading platform with premium features, paper trading, and real-time signals. The system integrates with Telegram for notifications and uses Flask for the web interface.

## Core Architecture

### Component Structure
- `app_premium.py` - Main Flask application with premium features
- `live_signal_engine.py` - Real-time trading signal generation
- `market_analysis_engine.py` - Market analysis and reporting
- `paper_trading_engine.py` - Virtual trading system
- `task_scheduler.py` - Scheduled tasks (pre/post market reports)

### Service Boundaries
1. Signal Generation (`live_signal_engine.py`):
   - Generates real-time trading signals
   - Interfaces with market data provider

2. Market Analysis (`market_analysis_engine.py`):
   - Pre-market and post-market reports
   - Technical analysis with multiple indicators

3. Paper Trading (`paper_trading_engine.py`):
   - Virtual portfolio management
   - P&L tracking and analytics

4. Premium Features (`subscription_manager.py`):
   - User authentication
   - Subscription management
   - Payment integration (Razorpay)

## Development Workflows

### Local Setup
```bash
# Start premium platform
python start_platform.py  # Runs on port 5500

# Start premium features only
python run_premium.py
```

### Testing
- Use `test_system.py` for comprehensive testing
- Routes are tested via `test_routes_simple.py`
- Each component has test functions in main block

### Error Handling Pattern
```python
try:
    # Operation
    logger.info("Operation description")
    result = risky_operation()
    logger.info(f"Operation success: {result}")
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # Provide fallback or error response
```

## Key Integration Points

### Market Data Provider
- Configure via `KITE_CONFIG` in `app_premium.py`
- Uses Zerodha's Kite Connect API
- Default test mode uses simulated data

### Telegram Integration
- Bot token configured in environment
- Handles signal broadcasting and user notifications
- Pre/post market reports sent automatically

### Payment Integration
- Razorpay integration in `payment_manager.py`
- Webhook handling in `/api/payment/webhook`
- Test keys provided for development

## Project Conventions

### Route Structure
- Premium routes require authentication
- Admin routes use `@admin_required` decorator
- API routes return JSON responses
- Error routes provide fallback templates

### Template Organization
- Base templates: `templates/base_*.html`
- Premium templates: `templates/*_premium.html`
- Dashboard: `templates/dashboard_ultra_modern.html`

### Logging
- Use `logger` instance from module
- Include operation context in messages
- Add `exc_info=True` for exceptions

## Common Tasks

### Adding New Routes
1. Add route to appropriate app (`app_premium.py` for premium features)
2. Create template in `templates/`
3. Add error handling with fallback
4. Update route map via `run_premium.py`

### Modifying Signal Engine
1. Update `LiveSignalEngine` in `live_signal_engine.py`
2. Test with `test_system.py`
3. Update relevant dashboard displays
4. Verify Telegram notifications

### Database Operations
- User data: `data/users.db`
- Trading signals: `data/trading_signals.db`
- Use context managers for connections