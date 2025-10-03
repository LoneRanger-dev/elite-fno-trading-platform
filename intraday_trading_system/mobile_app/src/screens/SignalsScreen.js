/**
 * Signals Screen - List of all trading signals with filtering
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { apiService } from '../services/apiService';
import { socketService } from '../services/socketService';

const SignalsScreen = () => {
  const [signals, setSignals] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL'); // ALL, ACTIVE, CLOSED

  useEffect(() => {
    loadSignals();
    setupSocketListeners();

    return () => {
      socketService.off('new_signal');
      socketService.off('signals_update');
    };
  }, [filter]);

  const setupSocketListeners = () => {
    socketService.on('new_signal', (signal) => {
      setSignals(prev => [signal, ...prev]);
    });

    socketService.on('signals_update', (updatedSignals) => {
      setSignals(updatedSignals);
    });
  };

  const loadSignals = useCallback(async () => {
    try {
      setLoading(true);
      const status = filter === 'ALL' ? null : filter;
      const data = await apiService.getSignals(50, status);
      setSignals(data);
    } catch (error) {
      console.error('Failed to load signals:', error);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadSignals();
    setRefreshing(false);
  }, [loadSignals]);

  const renderFilterButton = (filterType, label) => (
    <TouchableOpacity
      style={[
        styles.filterButton,
        filter === filterType && styles.activeFilterButton
      ]}
      onPress={() => setFilter(filterType)}
    >
      <Text style={[
        styles.filterButtonText,
        filter === filterType && styles.activeFilterButtonText
      ]}>
        {label}
      </Text>
    </TouchableOpacity>
  );

  const renderSignalItem = ({ item: signal }) => {
    const isProfit = signal.signal_type === 'BUY' ? 
      (signal.current_price || signal.entry_price) > signal.entry_price :
      (signal.current_price || signal.entry_price) < signal.entry_price;

    return (
      <View style={styles.signalCard}>
        <View style={styles.signalHeader}>
          <View style={styles.signalTitleRow}>
            <Text style={styles.instrumentText}>{signal.instrument}</Text>
            <View style={[
              styles.signalTypeBadge,
              { backgroundColor: signal.signal_type === 'BUY' ? '#4caf50' : '#f44336' }
            ]}>
              <Text style={styles.signalTypeText}>{signal.signal_type}</Text>
            </View>
          </View>
          <Text style={styles.timestampText}>
            {new Date(signal.timestamp).toLocaleString()}
          </Text>
        </View>

        <View style={styles.signalBody}>
          <View style={styles.priceRow}>
            <View style={styles.priceItem}>
              <Text style={styles.priceLabel}>Entry</Text>
              <Text style={styles.priceValue}>₹{signal.entry_price?.toFixed(2)}</Text>
            </View>
            <View style={styles.priceItem}>
              <Text style={styles.priceLabel}>Target</Text>
              <Text style={styles.priceValue}>₹{signal.target_price?.toFixed(2)}</Text>
            </View>
            <View style={styles.priceItem}>
              <Text style={styles.priceLabel}>Stop Loss</Text>
              <Text style={styles.priceValue}>₹{signal.stop_loss?.toFixed(2)}</Text>
            </View>
          </View>

          <View style={styles.detailsRow}>
            <View style={styles.detailItem}>
              <Text style={styles.detailLabel}>Confidence</Text>
              <Text style={styles.detailValue}>{signal.confidence?.toFixed(0)}%</Text>
            </View>
            <View style={styles.detailItem}>
              <Text style={styles.detailLabel}>R:R Ratio</Text>
              <Text style={styles.detailValue}>1:{signal.risk_reward_ratio?.toFixed(1)}</Text>
            </View>
            <View style={styles.detailItem}>
              <Text style={styles.detailLabel}>Status</Text>
              <Text style={[
                styles.statusText,
                { color: getStatusColor(signal.status) }
              ]}>
                {signal.status}
              </Text>
            </View>
          </View>

          {signal.setup_description && (
            <View style={styles.setupRow}>
              <Text style={styles.setupLabel}>Setup:</Text>
              <Text style={styles.setupText}>{signal.setup_description}</Text>
            </View>
          )}
        </View>
      </View>
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return '#2196f3';
      case 'CLOSED': return '#4caf50';
      case 'CANCELLED': return '#f44336';
      default: return '#666';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading signals...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Filter Buttons */}
      <View style={styles.filterContainer}>
        {renderFilterButton('ALL', 'All')}
        {renderFilterButton('ACTIVE', 'Active')}
        {renderFilterButton('CLOSED', 'Closed')}
      </View>

      {/* Signals List */}
      <FlatList
        data={signals}
        renderItem={renderSignalItem}
        keyExtractor={(item, index) => `${item.id || index}`}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContainer}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="trending-up" size={48} color="#ccc" />
            <Text style={styles.emptyText}>No signals found</Text>
            <Text style={styles.emptySubtext}>
              {filter === 'ALL' ? 'No signals generated yet' : `No ${filter.toLowerCase()} signals`}
            </Text>
          </View>
        }
      />
    </View>
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
  filterContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#fff',
    gap: 10,
  },
  filterButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
  },
  activeFilterButton: {
    backgroundColor: '#1a237e',
  },
  filterButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  activeFilterButtonText: {
    color: '#fff',
  },
  listContainer: {
    padding: 10,
  },
  signalCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    marginBottom: 10,
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  signalHeader: {
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  signalTitleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  instrumentText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  signalTypeBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 4,
  },
  signalTypeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  timestampText: {
    fontSize: 12,
    color: '#666',
  },
  signalBody: {
    padding: 15,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  priceItem: {
    alignItems: 'center',
  },
  priceLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  priceValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  detailItem: {
    alignItems: 'center',
  },
  detailLabel: {
    fontSize: 11,
    color: '#666',
    marginBottom: 2,
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  statusText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  setupRow: {
    flexDirection: 'row',
    marginTop: 10,
  },
  setupLabel: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
    marginRight: 5,
  },
  setupText: {
    flex: 1,
    fontSize: 12,
    color: '#666',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#999',
    marginTop: 10,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#ccc',
    marginTop: 5,
  },
});

export default SignalsScreen;