/**
 * Settings Screen - App configuration and preferences
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
  TextInput,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { apiService } from '../services/apiService';
import { notificationService } from '../services/notificationService';

const SettingsScreen = () => {
  const [serverURL, setServerURL] = useState('http://localhost:5000');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [vibrationEnabled, setVibrationEnabled] = useState(true);

  const renderSettingItem = (icon, title, subtitle, rightComponent) => (
    <View style={styles.settingItem}>
      <View style={styles.settingLeft}>
        <Icon name={icon} size={24} color="#666" style={styles.settingIcon} />
        <View style={styles.settingText}>
          <Text style={styles.settingTitle}>{title}</Text>
          {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
        </View>
      </View>
      {rightComponent}
    </View>
  );

  const renderSection = (title, children) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.sectionContent}>
        {children}
      </View>
    </View>
  );

  const updateServerURL = async () => {
    try {
      await AsyncStorage.setItem('serverURL', serverURL);
      apiService.updateBaseURL(`${serverURL}/api`);
      
      // Test connection
      const status = await apiService.getBotStatus();
      if (status) {
        notificationService.showFlashMessage('Server URL updated successfully', '', 'success');
      } else {
        notificationService.showFlashMessage('Failed to connect to new server', '', 'warning');
      }
    } catch (error) {
      console.error('Failed to update server URL:', error);
      notificationService.showFlashMessage('Failed to update server URL', '', 'danger');
    }
  };

  const testConnection = async () => {
    try {
      const status = await apiService.getBotStatus();
      if (status) {
        Alert.alert('Connection Test', 'Successfully connected to trading bot server!');
      } else {
        Alert.alert('Connection Test', 'Failed to connect to server. Please check the URL.');
      }
    } catch (error) {
      Alert.alert('Connection Test', 'Connection failed. Please check your network and server URL.');
    }
  };

  const sendTestNotification = () => {
    notificationService.showSignalNotification({
      signal_type: 'BUY',
      instrument: 'NIFTY',
      entry_price: 19500,
      confidence: 85,
    });
  };

  const clearCache = async () => {
    Alert.alert(
      'Clear Cache',
      'This will clear all cached data. Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.clear();
              notificationService.showFlashMessage('Cache cleared successfully', '', 'success');
            } catch (error) {
              console.error('Failed to clear cache:', error);
            }
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      {/* Server Configuration */}
      {renderSection('🌐 Server Configuration', (
        <>
          {renderSettingItem(
            'computer',
            'Server URL',
            'Trading bot server address',
            <View style={styles.urlContainer}>
              <TextInput
                style={styles.urlInput}
                value={serverURL}
                onChangeText={setServerURL}
                placeholder="http://localhost:5000"
                autoCapitalize="none"
                autoCorrect={false}
              />
              <TouchableOpacity
                style={styles.updateButton}
                onPress={updateServerURL}
              >
                <Text style={styles.updateButtonText}>Update</Text>
              </TouchableOpacity>
            </View>
          )}
          
          {renderSettingItem(
            'wifi',
            'Test Connection',
            'Verify connection to trading bot',
            <TouchableOpacity style={styles.testButton} onPress={testConnection}>
              <Text style={styles.testButtonText}>Test</Text>
            </TouchableOpacity>
          )}
        </>
      ))}

      {/* Notification Settings */}
      {renderSection('🔔 Notifications', (
        <>
          {renderSettingItem(
            'notifications',
            'Push Notifications',
            'Receive trading signal alerts',
            <Switch
              value={notificationsEnabled}
              onValueChange={setNotificationsEnabled}
              trackColor={{ false: '#767577', true: '#1a237e' }}
              thumbColor={notificationsEnabled ? '#fff' : '#f4f3f4'}
            />
          )}
          
          {renderSettingItem(
            'volume-up',
            'Sound',
            'Play sound for notifications',
            <Switch
              value={soundEnabled}
              onValueChange={setSoundEnabled}
              trackColor={{ false: '#767577', true: '#1a237e' }}
              thumbColor={soundEnabled ? '#fff' : '#f4f3f4'}
              disabled={!notificationsEnabled}
            />
          )}
          
          {renderSettingItem(
            'vibration',
            'Vibration',
            'Vibrate for notifications',
            <Switch
              value={vibrationEnabled}
              onValueChange={setVibrationEnabled}
              trackColor={{ false: '#767577', true: '#1a237e' }}
              thumbColor={vibrationEnabled ? '#fff' : '#f4f3f4'}
              disabled={!notificationsEnabled}
            />
          )}
          
          {renderSettingItem(
            'send',
            'Test Notification',
            'Send a test trading signal',
            <TouchableOpacity
              style={styles.testButton}
              onPress={sendTestNotification}
              disabled={!notificationsEnabled}
            >
              <Text style={[
                styles.testButtonText,
                !notificationsEnabled && { color: '#ccc' }
              ]}>
                Send
              </Text>
            </TouchableOpacity>
          )}
        </>
      ))}

      {/* App Settings */}
      {renderSection('⚙️ App Settings', (
        <>
          {renderSettingItem(
            'cached',
            'Clear Cache',
            'Remove all cached data',
            <TouchableOpacity style={styles.clearButton} onPress={clearCache}>
              <Text style={styles.clearButtonText}>Clear</Text>
            </TouchableOpacity>
          )}
          
          {renderSettingItem(
            'info',
            'App Version',
            'Version 1.0.0',
            null
          )}
        </>
      ))}

      {/* About */}
      {renderSection('ℹ️ About', (
        <>
          {renderSettingItem(
            'business',
            'Trading Bot System',
            'Intraday trading signals and automation',
            null
          )}
          
          {renderSettingItem(
            'code',
            'Developer',
            'Trading Bot Team',
            null
          )}
          
          {renderSettingItem(
            'help',
            'Support',
            'Contact for help and support',
            <TouchableOpacity
              onPress={() => Alert.alert('Support', 'Contact: support@tradingbot.com')}
            >
              <Icon name="chevron-right" size={24} color="#999" />
            </TouchableOpacity>
          )}
        </>
      ))}

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          © 2025 Intraday Trading Bot System
        </Text>
        <Text style={styles.footerText}>
          Made with ❤️ for traders
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#666',
    marginLeft: 15,
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  sectionContent: {
    backgroundColor: '#fff',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingIcon: {
    marginRight: 15,
  },
  settingText: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  settingSubtitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  urlContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginLeft: 10,
  },
  urlInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    paddingHorizontal: 8,
    paddingVertical: 6,
    fontSize: 12,
    marginRight: 8,
  },
  updateButton: {
    backgroundColor: '#1a237e',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  updateButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  testButton: {
    backgroundColor: '#2196f3',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 4,
  },
  testButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  clearButton: {
    backgroundColor: '#f44336',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 4,
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    marginBottom: 4,
  },
});

export default SettingsScreen;