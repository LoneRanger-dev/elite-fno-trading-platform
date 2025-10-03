# Mobile App - React Native Trading Bot Client

This mobile application provides real-time access to the Intraday Trading Bot System with live notifications, market data, and bot controls.

## Features

- **Real-time Dashboard**: Live market data and bot status monitoring
- **Trading Signals**: History with filtering and real-time notifications
- **Performance Analytics**: Charts, metrics, and P&L tracking
- **Bot Controls**: Start/stop trading bot remotely
- **Push Notifications**: Instant alerts for new trading signals
- **Settings**: Server configuration and notification preferences

## Prerequisites

- **Node.js**: v16.0 or higher
- **React Native CLI**: Install globally
- **Android Studio**: For Android development
- **Xcode**: For iOS development (macOS only)
- **Trading Bot Server**: Must be running and accessible

## Installation

### 1. Install React Native CLI
```bash
npm install -g react-native-cli
```

### 2. Install Dependencies
```bash
cd mobile_app
npm install
```

### 3. iOS Setup (macOS only)
```bash
cd ios && pod install && cd ..
```

### 4. Android Setup
- Ensure Android Studio is installed
- Create Android Virtual Device (AVD) or connect physical device
- Enable USB debugging on physical device

## Running the App

### Android
```bash
# Start Metro bundler
npx react-native start

# Run on Android (new terminal)
npx react-native run-android
```

### iOS (macOS only)
```bash
# Start Metro bundler
npx react-native start

# Run on iOS (new terminal)
npx react-native run-ios
```

## Configuration

### Server Connection
1. Open the app and navigate to **Settings**
2. Update **Server URL** to your trading bot server address
3. Tap **Update** and **Test** connection
4. Default: `http://localhost:5000`

### Notifications
- Enable/disable push notifications
- Configure sound and vibration preferences
- Test notifications to ensure proper setup

## App Structure

```
src/
├── screens/
│   ├── DashboardScreen.js     # Main overview with live data
│   ├── SignalsScreen.js       # Trading signals history
│   ├── PerformanceScreen.js   # Analytics and charts
│   └── SettingsScreen.js      # App configuration
├── services/
│   ├── apiService.js          # Backend API communication
│   ├── socketService.js       # Real-time WebSocket connection
│   └── notificationService.js # Push notifications and alerts
└── App.js                     # Main navigation and app setup
```

## Key Dependencies

- **React Navigation**: Screen navigation
- **React Native Vector Icons**: Icon set
- **AsyncStorage**: Local data storage
- **Socket.IO Client**: Real-time communication
- **Chart.js**: Performance charts and analytics
- **Flash Message**: In-app notifications

## API Integration

The app communicates with the Flask backend through:

### REST Endpoints
- `GET /api/bot/status` - Bot status and health
- `POST /api/bot/start` - Start trading bot
- `POST /api/bot/stop` - Stop trading bot
- `GET /api/signals` - Trading signals history
- `GET /api/performance` - Performance metrics

### WebSocket Events
- `bot_status` - Real-time bot status updates
- `new_signal` - Live trading signal broadcasts
- `market_update` - Live market data updates

## Push Notifications

The app receives push notifications for:
- **New Trading Signals**: Instant alerts with signal details
- **Bot Status Changes**: Start/stop notifications
- **Market Events**: Important market updates
- **System Alerts**: Errors or warnings

## Troubleshooting

### Common Issues

**Metro bundler fails to start:**
```bash
npx react-native start --reset-cache
```

**Build errors on Android:**
```bash
cd android && ./gradlew clean && cd ..
npx react-native run-android
```

**iOS build issues:**
```bash
cd ios && pod install && cd ..
npx react-native run-ios
```

**Connection issues:**
- Verify server URL in Settings
- Ensure trading bot server is running
- Check network connectivity
- Test connection in Settings screen

### Debug Mode

Enable debug mode for detailed logging:
1. Shake device or press Ctrl+M (Android) / Cmd+D (iOS)
2. Select "Debug" or "Start Remote JS Debugging"
3. Open Chrome DevTools for debugging

## Development

### Adding New Features

1. Create new screen in `src/screens/`
2. Add navigation route in `App.js`
3. Implement API calls in `src/services/apiService.js`
4. Add WebSocket events in `src/services/socketService.js`
5. Update notifications in `src/services/notificationService.js`

### Building for Production

#### Android
```bash
cd android
./gradlew assembleRelease
```
APK location: `android/app/build/outputs/apk/release/`

#### iOS
1. Open project in Xcode: `ios/TradingBotApp.xcworkspace`
2. Select "Generic iOS Device" or connected device
3. Product → Archive
4. Follow App Store submission process

## Support

For technical support or feature requests:
- Email: support@tradingbot.com
- Check server logs for backend issues
- Review React Native documentation for platform-specific issues

---

**Note**: Ensure the trading bot server is running and accessible before using the mobile app. The app requires real-time connection to provide live updates and notifications.