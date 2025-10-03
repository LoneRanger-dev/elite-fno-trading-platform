/**
 * Notification Service for push notifications and alerts
 */

import PushNotification from 'react-native-push-notification';
import { Platform, PermissionsAndroid } from 'react-native';
import { showMessage } from 'react-native-flash-message';

class NotificationService {
  constructor() {
    this.isInitialized = false;
  }

  async initialize() {
    if (this.isInitialized) {
      return;
    }

    // Configure push notifications
    PushNotification.configure({
      // Called when Token is generated (iOS and Android)
      onRegister: function (token) {
        console.log('Push notification token:', token);
      },

      // Called when a remote is received or opened, or local notification is opened
      onNotification: function (notification) {
        console.log('Notification received:', notification);
        
        // Process the notification here
        if (notification.userInteraction) {
          // User tapped on notification
          console.log('User tapped notification');
        }
      },

      // Should the initial notification be popped automatically
      popInitialNotification: true,

      // Permissions
      requestPermissions: Platform.OS === 'ios',
    });

    // Request permissions for Android
    if (Platform.OS === 'android') {
      await this.requestAndroidPermissions();
    }

    // Create notification channels (Android)
    if (Platform.OS === 'android') {
      this.createNotificationChannels();
    }

    this.isInitialized = true;
    console.log('Notification service initialized');
  }

  async requestAndroidPermissions() {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
        {
          title: 'Notification Permission',
          message: 'Trading Bot needs notification permission to send trading signals.',
          buttonNeutral: 'Ask Me Later',
          buttonNegative: 'Cancel',
          buttonPositive: 'OK',
        }
      );
      
      if (granted === PermissionsAndroid.RESULTS.GRANTED) {
        console.log('Notification permission granted');
      } else {
        console.log('Notification permission denied');
      }
    } catch (err) {
      console.warn('Permission request error:', err);
    }
  }

  createNotificationChannels() {
    // Create channel for trading signals
    PushNotification.createChannel(
      {
        channelId: 'trading-signals',
        channelName: 'Trading Signals',
        channelDescription: 'Notifications for new trading signals',
        playSound: true,
        soundName: 'default',
        importance: 4,
        vibrate: true,
      },
      (created) => console.log(`Trading signals channel created: ${created}`)
    );

    // Create channel for system alerts
    PushNotification.createChannel(
      {
        channelId: 'system-alerts',
        channelName: 'System Alerts',
        channelDescription: 'Notifications for system status and alerts',
        playSound: true,
        soundName: 'default',
        importance: 3,
        vibrate: false,
      },
      (created) => console.log(`System alerts channel created: ${created}`)
    );
  }

  // Show notification for new trading signal
  showSignalNotification(signal) {
    const signalType = signal.signal_type || 'SIGNAL';
    const instrument = signal.instrument || 'Unknown';
    const confidence = signal.confidence || 0;
    const entryPrice = signal.entry_price || 0;

    // Show push notification
    PushNotification.localNotification({
      channelId: 'trading-signals',
      title: `🎯 New ${signalType} Signal`,
      message: `${instrument} - ₹${entryPrice.toFixed(2)} (${confidence.toFixed(0)}% confidence)`,
      playSound: true,
      soundName: 'default',
      actions: ['View Details'],
      userInfo: { signal },
    });

    // Also show flash message for immediate visibility
    showMessage({
      message: `🎯 New ${signalType} Signal`,
      description: `${instrument} - ₹${entryPrice.toFixed(2)}`,
      type: signalType === 'BUY' ? 'success' : 'danger',
      duration: 5000,
      icon: 'auto',
    });
  }

  // Show system notification
  showSystemNotification(title, message, type = 'info') {
    PushNotification.localNotification({
      channelId: 'system-alerts',
      title: title,
      message: message,
      playSound: false,
      vibrate: false,
    });

    showMessage({
      message: title,
      description: message,
      type: type,
      duration: 3000,
    });
  }

  // Show bot status notification
  showBotStatusNotification(status) {
    const isOnline = status.running;
    const title = isOnline ? '🟢 Bot Online' : '🔴 Bot Offline';
    const message = isOnline ? 'Trading bot is running' : 'Trading bot has stopped';

    this.showSystemNotification(title, message, isOnline ? 'success' : 'warning');
  }

  // Show performance notification
  showPerformanceNotification(performance) {
    const winRate = performance.win_rate || 0;
    const totalPnL = performance.total_pnl || 0;
    
    const title = '📊 Daily Performance';
    const message = `Win Rate: ${winRate.toFixed(1)}% | P&L: ${totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)}%`;

    this.showSystemNotification(title, message, totalPnL >= 0 ? 'success' : 'warning');
  }

  // Show error notification
  showErrorNotification(error) {
    this.showSystemNotification('⚠️ System Error', error, 'danger');
  }

  // Clear all notifications
  clearAllNotifications() {
    PushNotification.cancelAllLocalNotifications();
  }

  // Cancel specific notification
  cancelNotification(id) {
    PushNotification.cancelLocalNotifications({ id });
  }

  // Check if notifications are enabled
  checkPermissions() {
    return new Promise((resolve) => {
      PushNotification.checkPermissions((permissions) => {
        resolve(permissions);
      });
    });
  }

  // Show flash message only (no push notification)
  showFlashMessage(message, description = '', type = 'info', duration = 3000) {
    showMessage({
      message,
      description,
      type,
      duration,
      icon: 'auto',
    });
  }
}

export const notificationService = new NotificationService();