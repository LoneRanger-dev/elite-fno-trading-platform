/**
 * Performance Screen - Trading performance analytics and charts
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { LineChart, PieChart } from 'react-native-chart-kit';

import { apiService } from '../services/apiService';

const { width: screenWidth } = Dimensions.get('window');

const PerformanceScreen = () => {
  const [performance, setPerformance] = useState({});
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPerformanceData();
  }, []);

  const loadPerformanceData = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPerformance(30);
      setPerformance(data);
    } catch (error) {
      console.error('Failed to load performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadPerformanceData();
    setRefreshing(false);
  };

  const renderMetricCard = (title, value, color, subtitle = '') => (
    <View style={[styles.metricCard, { borderLeftColor: color }]}>
      <Text style={styles.metricTitle}>{title}</Text>
      <Text style={[styles.metricValue, { color }]}>{value}</Text>
      {subtitle ? <Text style={styles.metricSubtitle}>{subtitle}</Text> : null}
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading performance data...</Text>
      </View>
    );
  }

  // Sample chart data (replace with actual data)
  const chartData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        data: [2.5, -1.2, 3.8, 1.6],
        strokeWidth: 2,
      },
    ],
  };

  const pieData = [
    {
      name: 'Wins',
      population: performance.winning_trades || 0,
      color: '#4caf50',
      legendFontColor: '#333',
      legendFontSize: 15,
    },
    {
      name: 'Losses',
      population: performance.losing_trades || 0,
      color: '#f44336',
      legendFontColor: '#333',
      legendFontSize: 15,
    },
  ];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Key Metrics */}
      <View style={styles.metricsContainer}>
        {renderMetricCard(
          'Total P&L',
          `${(performance.total_pnl || 0) >= 0 ? '+' : ''}${(performance.total_pnl || 0).toFixed(2)}%`,
          (performance.total_pnl || 0) >= 0 ? '#4caf50' : '#f44336'
        )}
        {renderMetricCard(
          'Win Rate',
          `${(performance.win_rate || 0).toFixed(1)}%`,
          '#2196f3',
          `${performance.winning_trades || 0}/${(performance.winning_trades || 0) + (performance.losing_trades || 0)} trades`
        )}
        {renderMetricCard(
          'Best Trade',
          `+${(performance.best_trade || 0).toFixed(2)}%`,
          '#4caf50'
        )}
        {renderMetricCard(
          'Worst Trade',
          `${(performance.worst_trade || 0).toFixed(2)}%`,
          '#f44336'
        )}
      </View>

      {/* P&L Chart */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>📈 Weekly P&L Trend</Text>
        <LineChart
          data={chartData}
          width={screenWidth - 40}
          height={220}
          chartConfig={{
            backgroundColor: '#fff',
            backgroundGradientFrom: '#fff',
            backgroundGradientTo: '#fff',
            decimalPlaces: 1,
            color: (opacity = 1) => `rgba(26, 35, 126, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
            style: {
              borderRadius: 16,
            },
            propsForDots: {
              r: '6',
              strokeWidth: '2',
              stroke: '#1a237e',
            },
          }}
          bezier
          style={styles.chart}
        />
      </View>

      {/* Win/Loss Distribution */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>🎯 Win/Loss Distribution</Text>
        <PieChart
          data={pieData}
          width={screenWidth - 40}
          height={200}
          chartConfig={{
            color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
          }}
          accessor="population"
          backgroundColor="transparent"
          paddingLeft="15"
        />
      </View>

      {/* Detailed Stats */}
      <View style={styles.statsContainer}>
        <Text style={styles.sectionTitle}>📊 Detailed Statistics</Text>
        
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Total Signals:</Text>
          <Text style={styles.statValue}>{performance.total_signals || 0}</Text>
        </View>
        
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Average Win:</Text>
          <Text style={[styles.statValue, { color: '#4caf50' }]}>
            +{(performance.avg_win || 0).toFixed(2)}%
          </Text>
        </View>
        
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Average Loss:</Text>
          <Text style={[styles.statValue, { color: '#f44336' }]}>
            {(performance.avg_loss || 0).toFixed(2)}%
          </Text>
        </View>
        
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Profit Factor:</Text>
          <Text style={styles.statValue}>{(performance.profit_factor || 0).toFixed(2)}</Text>
        </View>
        
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Period:</Text>
          <Text style={styles.statValue}>{performance.period_days || 30} days</Text>
        </View>
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
  metricsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
    gap: 10,
  },
  metricCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    width: (screenWidth - 40) / 2,
    borderLeftWidth: 4,
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  metricTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  metricSubtitle: {
    fontSize: 10,
    color: '#999',
  },
  chartContainer: {
    backgroundColor: '#fff',
    margin: 10,
    borderRadius: 8,
    padding: 15,
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  statsContainer: {
    backgroundColor: '#fff',
    margin: 10,
    borderRadius: 8,
    padding: 15,
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
  },
  statValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
});

export default PerformanceScreen;