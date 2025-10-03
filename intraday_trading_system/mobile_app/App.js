/**
 * Main App Component for Intraday Trading Mobile App
 */

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, StatusBar, Alert } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import FlashMessage from 'react-native-flash-message';

// Import screens
import DashboardScreen from './src/screens/DashboardScreen';
import SignalsScreen from './src/screens/SignalsScreen';
import PerformanceScreen from './src/screens/PerformanceScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Import services
import { apiService } from './src/services/apiService';
import { socketService } from './src/services/socketService';
import { notificationService } from './src/services/notificationService';

const Tab = createBottomTabNavigator();

const App = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [botStatus, setBotStatus] = useState(null);

  useEffect(() => {
    // Initialize services
    initializeApp();

    return () => {
      // Cleanup
      socketService.disconnect();
    };
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize notifications
      await notificationService.initialize();

      // Initialize socket connection
      socketService.connect();

      // Set up socket event listeners
      socketService.on('connect', () => {
        setIsConnected(true);
        console.log('Connected to trading bot server');
      });

      socketService.on('disconnect', () => {
        setIsConnected(false);
        console.log('Disconnected from trading bot server');
      });

      socketService.on('bot_status', (status) => {
        setBotStatus(status);
      });

      socketService.on('new_signal', (signal) => {
        // Show push notification for new signal
        notificationService.showSignalNotification(signal);
      });

      // Test API connection
      const status = await apiService.getBotStatus();
      if (status) {
        setBotStatus(status);
      }

    } catch (error) {
      console.error('Failed to initialize app:', error);
      Alert.alert('Connection Error', 'Failed to connect to trading bot server.');
    }
  };

  const getTabBarIcon = (routeName, focused, color, size) => {
    let iconName;

    switch (routeName) {
      case 'Dashboard':
        iconName = 'dashboard';
        break;
      case 'Signals':
        iconName = 'trending-up';
        break;
      case 'Performance':
        iconName = 'analytics';
        break;
      case 'Settings':
        iconName = 'settings';
        break;
      default:
        iconName = 'dashboard';
    }

    return <Icon name={iconName} size={size} color={color} />;
  };

  return (
    <>
      <StatusBar barStyle="light-content" backgroundColor="#1a237e" />
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) =>
              getTabBarIcon(route.name, focused, color, size),
            tabBarActiveTintColor: '#1a237e',
            tabBarInactiveTintColor: 'gray',
            headerStyle: {
              backgroundColor: '#1a237e',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
            headerRight: () => (
              <View style={{ flexDirection: 'row', alignItems: 'center', marginRight: 15 }}>
                <View
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: isConnected ? '#4caf50' : '#f44336',
                    marginRight: 5,
                  }}
                />
                <Text style={{ color: '#fff', fontSize: 12 }}>
                  {isConnected ? 'Online' : 'Offline'}
                </Text>
              </View>
            ),
          })}
        >
          <Tab.Screen 
            name="Dashboard" 
            component={DashboardScreen}
            options={{ title: '📊 Dashboard' }}
          />
          <Tab.Screen 
            name="Signals" 
            component={SignalsScreen}
            options={{ title: '🎯 Signals' }}
          />
          <Tab.Screen 
            name="Performance" 
            component={PerformanceScreen}
            options={{ title: '📈 Performance' }}
          />
          <Tab.Screen 
            name="Settings" 
            component={SettingsScreen}
            options={{ title: '⚙️ Settings' }}
          />
        </Tab.Navigator>
      </NavigationContainer>
      <FlashMessage position="top" />
    </>
  );
};

export default App;