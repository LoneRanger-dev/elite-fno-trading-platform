/**
 * Dashboard Screen - Main overview of trading bot status and quick stats
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { LineChart } from 'react-native-chart-kit';

import { apiService } from '../services/apiService';
import { socketService } from '../services/socketService';
import { notificationService } from '../services/notificationService';

const { width: screenWidth } = Dimensions.get('window');

const DashboardScreen = () => {
  const [botStatus, setBotStatus] = useState(null);
  const [marketData, setMarketData] = useState({});
  const [todayStats, setTodayStats] = useState({});
  const [recentSignals, setRecentSignals] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    setupSocketListeners();

    return () => {
      // Cleanup socket listeners
      socketService.off('bot_status');
      socketService.off('market_update');
      socketService.off('new_signal');
    };
  }, []);

  const setupSocketListeners = () => {
    socketService.on('bot_status', (status) => {
      setBotStatus(status);
    });

    socketService.on('market_update', (data) => {
      setMarketData(data);
    });

    socketService.on('new_signal', (signal) => {
      // Add new signal to the beginning of the list
      setRecentSignals(prev => [signal, ...prev.slice(0, 4)]);
    });
  };

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);

      // Load all dashboard data in parallel
      const [status, market, signals, performance] = await Promise.all([
        apiService.getBotStatus(),
        apiService.getMarketData(),
        apiService.getSignals(5), // Get recent 5 signals
        apiService.getPerformance(1), // Today's performance
      ]);

      setBotStatus(status);
      setMarketData(market);
      setRecentSignals(signals);
      setTodayStats(performance);

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      notificationService.showErrorNotification('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  }, [loadDashboardData]);

  const handleBotControl = async (action) => {
    try {
      const confirmMessage = action === 'start' 
        ? 'Are you sure you want to start the trading bot?'
        : 'Are you sure you want to stop the trading bot?';

      Alert.alert(
        'Confirm Action',
        confirmMessage,
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Confirm',
            onPress: async () => {
              const success = action === 'start' 
                ? await apiService.startBot()
                : await apiService.stopBot();

              if (success) {
                notificationService.showFlashMessage(
                  `Bot ${action === 'start' ? 'Started' : 'Stopped'}`,
                  '',
                  'success'
                );
                loadDashboardData(); // Refresh data
              } else {
                notificationService.showFlashMessage(
                  `Failed to ${action} bot`,
                  '',
                  'danger'
                );
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error(`Failed to ${action} bot:`, error);
    }
  };

  const sendTestMessage = async () => {
    try {
      const success = await apiService.sendTestMessage();
      if (success) {
        notificationService.showFlashMessage('Test message sent!', '', 'success');
      } else {
        notificationService.showFlashMessage('Failed to send test message', '', 'danger');
      }
    } catch (error) {
      console.error('Failed to send test message:', error);
    }
  };

  const renderStatCard = (title, value, color, icon) => (
    <View style={[styles.statCard, { borderLeftColor: color }]}>
      <View style={styles.statCardContent}>
        <View style={styles.statCardLeft}>
          <Text style={styles.statValue}>{value}</Text>
          <Text style={styles.statTitle}>{title}</Text>
        </View>
        <Icon name={icon} size={24} color={color} />
      </View>
    </View>
  );

  const renderMarketData = () => (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>📈 Live Market Data</Text>
      {Object.entries(marketData).map(([instrument, data]) => (
        <View key={instrument} style={styles.marketRow}>
          <Text style={styles.instrumentName}>{instrument}</Text>
          <View style={styles.priceContainer}>
            <Text style={styles.price}>₹{data.price?.toFixed(2) || 'N/A'}</Text>
            <Text style={[
              styles.change,
              { color: (data.change || 0) >= 0 ? '#4caf50' : '#f44336' }
            ]}>
              {(data.change || 0) >= 0 ? '+' : ''}{data.change?.toFixed(2) || '0.00'}%
            </Text>
          </View>
        </View>
      ))}
    </View>
  );

  const renderBotControl = () => (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>🤖 Bot Control</Text>
      <View style={styles.controlButtons}>
        <TouchableOpacity
          style={[styles.controlButton, styles.startButton]}
          onPress={() => handleBotControl('start')}
          disabled={botStatus?.running}
        >
          <Icon name="play-arrow" size={20} color="#fff" />
          <Text style={styles.controlButtonText}>Start</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.controlButton, styles.stopButton]}
          onPress={() => handleBotControl('stop')}
          disabled={!botStatus?.running}
        >
          <Icon name="stop" size={20} color="#fff" />
          <Text style={styles.controlButtonText}>Stop</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.controlButton, styles.testButton]}
          onPress={sendTestMessage}
        >
          <Icon name="send" size={20} color="#fff" />
          <Text style={styles.controlButtonText}>Test</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Status:</Text>
        <Text style={[
          styles.statusValue,
          { color: botStatus?.running ? '#4caf50' : '#f44336' }
        ]}>
          {botStatus?.running ? 'Running' : 'Stopped'}
        </Text>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Statistics Cards */}
      <View style={styles.statsContainer}>
        {renderStatCard(
          'Signals Today',
          todayStats.total_signals || 0,
          '#2196f3',
          'trending-up'
        )}
        {renderStatCard(
          'Win Rate',
          `${(todayStats.win_rate || 0).toFixed(1)}%`,
          '#4caf50',
          'check-circle'
        )}
        {renderStatCard(
          'Total P&L',
          `${(todayStats.total_pnl || 0) >= 0 ? '+' : ''}${(todayStats.total_pnl || 0).toFixed(2)}%`,
          (todayStats.total_pnl || 0) >= 0 ? '#4caf50' : '#f44336',
          'account-balance'
        )}
      </View>

      {/* Market Data */}
      {renderMarketData()}

      {/* Bot Control */}
      {renderBotControl()}

      {/* Recent Signals */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>🎯 Recent Signals</Text>
        {recentSignals.length > 0 ? (
          recentSignals.map((signal, index) => (
            <View key={index} style={styles.signalItem}>
              <View style={styles.signalHeader}>
                <Text style={styles.signalInstrument}>{signal.instrument}</Text>
                <View style={[
                  styles.signalTypeBadge,
                  { backgroundColor: signal.signal_type === 'BUY' ? '#4caf50' : '#f44336' }
                ]}>
                  <Text style={styles.signalTypeText}>{signal.signal_type}</Text>
                </View>
              </View>
              <View style={styles.signalDetails}>
                <Text style={styles.signalDetail}>Entry: ₹{signal.entry_price?.toFixed(2)}</Text>
                <Text style={styles.signalDetail}>Target: ₹{signal.target_price?.toFixed(2)}</Text>
                <Text style={styles.signalDetail}>Confidence: {signal.confidence?.toFixed(0)}%</Text>
              </View>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>No recent signals</Text>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 10,
    gap: 10,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    borderLeftWidth: 4,
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statCardContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statCardLeft: {
    flex: 1,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  statTitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  card: {
    backgroundColor: '#fff',
    margin: 10,
    borderRadius: 8,
    padding: 15,
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  marketRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  instrumentName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  priceContainer: {
    alignItems: 'flex-end',
  },
  price: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  change: {
    fontSize: 14,
    fontWeight: '500',
  },
  controlButtons: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 15,
  },
  controlButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 6,
    gap: 5,
  },
  startButton: {
    backgroundColor: '#4caf50',
  },
  stopButton: {
    backgroundColor: '#f44336',
  },
  testButton: {
    backgroundColor: '#2196f3',
  },
  controlButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  statusLabel: {
    fontSize: 16,
    color: '#666',
  },
  statusValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  signalItem: {
    padding: 10,
    borderRadius: 6,
    backgroundColor: '#f9f9f9',
    marginBottom: 10,
  },
  signalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  signalInstrument: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  signalTypeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  signalTypeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  signalDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  signalDetail: {
    fontSize: 12,
    color: '#666',
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    fontStyle: 'italic',
    padding: 20,
  },
});

export default DashboardScreen;