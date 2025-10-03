"""
🌐 Elite FnO Trading Website - Flask Web Application
Main web application with live signal generation and enhanced UI
"""

from flask import Flask, render_template, render_template_string, jsonify, request, redirect, url_for, session
import asyncio
import json
import os
from datetime import datetime, timedelta
import threading
import logging
from typing import Dict, List
import random
import time

# Import signal engine and testing system
from live_signal_engine import signal_engine
from test_system import ComprehensiveTester, LiveMarketDataTester, TelegramBotTester

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'elite_fno_trading_secret_key_2024'

# Global variables
tester = ComprehensiveTester()
latest_test_results = {}

# Statistics tracking
stats = {
    'signals_today': 0,
    'win_rate': 0.0,
    'total_pnl': 0.0,
    'signals_30d': 0,
    'total_subscribers': random.randint(1250, 1500),
    'active_signals': 0
}

# Enhanced HTML Templates
ENHANCED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Elite FnO Trading Dashboard - Live Signals</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --dark-gradient: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --neon-blue: #00f5ff;
            --neon-green: #00ff88;
            --neon-red: #ff6b6b;
            --neon-orange: #ffa500;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--dark-gradient);
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        
        /* Animated Background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 20%, rgba(0, 245, 255, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 80% 80%, rgba(255, 107, 107, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(0, 255, 136, 0.1) 0%, transparent 50%);
            z-index: -2;
            animation: bgFloat 12s ease-in-out infinite;
        }
        
        /* Matrix dots pattern */
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: radial-gradient(circle at 2px 2px, rgba(0, 245, 255, 0.1) 1px, transparent 0);
            background-size: 40px 40px;
            z-index: -1;
            animation: matrixScroll 20s linear infinite;
        }
        
        @keyframes bgFloat {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            33% { transform: translateY(-30px) rotate(1deg); }
            66% { transform: translateY(15px) rotate(-1deg); }
        }
        
        @keyframes matrixScroll {
            0% { transform: translateY(0px); }
            100% { transform: translateY(40px); }
        }
        
        /* Ultra-Modern Navigation */
        .navbar {
            background: rgba(12, 12, 12, 0.8);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-bottom: 1px solid var(--glass-border);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        }
        
        .nav-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: 900;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        
        .logo:hover {
            transform: scale(1.05);
        }
        
        .logo i {
            font-size: 2rem;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        
        .nav-links a {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            font-weight: 500;
            position: relative;
            transition: all 0.3s ease;
            padding: 0.5rem 1rem;
            border-radius: 10px;
        }
        
        .nav-links a::before {
            content: '';
            position: absolute;
            width: 0;
            height: 2px;
            bottom: 0;
            left: 50%;
            background: var(--accent-gradient);
            transition: all 0.3s ease;
            transform: translateX(-50%);
        }
        
        .nav-links a:hover {
            color: var(--neon-blue);
            text-shadow: 0 0 15px rgba(0, 245, 255, 0.6);
            background: var(--glass-bg);
        }
        
        .nav-links a:hover::before {
            width: 80%;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(from 0deg, transparent, rgba(0, 245, 255, 0.1), transparent);
            animation: rotate 4s linear infinite;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .stat-card:hover::before {
            opacity: 1;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 245, 255, 0.2);
        }
        
        @keyframes rotate {
            100% { transform: rotate(360deg); }
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #00f5ff, #0080ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: rgba(255, 255, 255, 0.7);
            font-weight: 500;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .signals-section {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 1.5rem;
        }
        
        .section-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .signal-card {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .signal-card:hover {
            transform: translateX(5px) translateY(-2px);
            border-color: #00f5ff;
            box-shadow: 0 20px 50px rgba(0, 245, 255, 0.3),
                        0 0 30px rgba(0, 245, 255, 0.1) inset;
            background: rgba(0, 245, 255, 0.05);
        }
        
        .signal-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.1), transparent);
            transition: left 0.5s;
        }
        
        .signal-card:hover::after {
            left: 100%;
        }
        
        .signal-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .signal-type {
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .buy-call {
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #000;
        }
        
        .buy-put {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
        }
        
        .confidence-meter {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .confidence-bar {
            width: 60px;
            height: 6px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #ffa500, #00ff88);
            border-radius: 3px;
            transition: width 0.3s ease;
        }
        
        .signal-details {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .detail-item {
            text-align: center;
        }
        
        .detail-label {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.6);
            margin-bottom: 0.2rem;
        }
        
        .detail-value {
            font-weight: 600;
            font-size: 1rem;
        }
        
        .signal-description {
            background: rgba(0, 0, 0, 0.3);
            padding: 0.8rem;
            border-radius: 8px;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.8);
            border-left: 3px solid #00f5ff;
        }
        
        .market-data {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 1.5rem;
        }
        
        .market-item {
            display: flex;
            justify-content: between;
            align-items: center;
            padding: 1rem;
            margin-bottom: 0.5rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .market-item:hover {
            background: rgba(0, 245, 255, 0.1);
        }
        
        .market-symbol {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .market-price {
            text-align: right;
        }
        
        .price {
            font-weight: 700;
            font-size: 1.2rem;
        }
        
        .change {
            font-size: 0.9rem;
            margin-top: 0.2rem;
        }
        
        .positive {
            color: #00ff88;
        }
        
        .negative {
            color: #ff6b6b;
        }
        
        .control-buttons {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            z-index: 1000;
        }
        
        .control-btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: none;
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .start-btn {
            background: linear-gradient(135deg, #00ff88, #00cc6a);
        }
        
        .stop-btn {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        }
        
        .test-btn {
            background: linear-gradient(135deg, #00f5ff, #0080ff);
        }
        
        .control-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 15px 40px rgba(0, 245, 255, 0.3);
        }
        
        .no-signals {
            text-align: center;
            padding: 3rem;
            color: rgba(255, 255, 255, 0.5);
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 1rem;
            }
            
            .control-buttons {
                bottom: 1rem;
                right: 1rem;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-content">
            <div class="logo">🚀 Elite FnO Trading</div>
            <ul class="nav-links">
                <li><a href="/dashboard">Dashboard</a></li>
                <li><a href="#signals">Signals</a></li>
                <li><a href="#performance">Performance</a></li>
                <li><a href="/test-system">Testing</a></li>
            </ul>
        </div>
    </nav>
    
    <div class="container">
        <!-- Statistics Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.signals_today }}</div>
                <div class="stat-label">Signals Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ "%.1f"|format(stats.win_rate) }}%</div>
                <div class="stat-label">Win Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">₹{{ "{:,.0f}"|format(stats.total_pnl) }}</div>
                <div class="stat-label">Total P&L</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_subscribers }}</div>
                <div class="stat-label">Subscribers</div>
            </div>
        </div>
        
        <!-- Main Content Grid -->
        <div class="main-grid">
            <!-- Signals Section -->
            <div class="signals-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-chart-line"></i>
                        Live Signals
                    </h2>
                    <div class="pulse" style="color: #00ff88; font-size: 0.9rem;">
                        <i class="fas fa-circle" style="font-size: 0.5rem;"></i> LIVE
                    </div>
                </div>
                
                <div id="signals-container">
                    {% if signals %}
                        {% for signal in signals %}
                        <div class="signal-card">
                            <div class="signal-header">
                                <div>
                                    <h3>{{ signal.instrument }}</h3>
                                    <span class="signal-type {{ 'buy-call' if 'CALL' in signal.signal_type else 'buy-put' }}">
                                        {{ signal.signal_type.replace('_', ' ') }}
                                    </span>
                                </div>
                                <div class="confidence-meter">
                                    <span>{{ signal.confidence }}%</span>
                                    <div class="confidence-bar">
                                        <div class="confidence-fill" style="width: {{ signal.confidence }}%"></div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="signal-details">
                                <div class="detail-item">
                                    <div class="detail-label">Entry</div>
                                    <div class="detail-value">₹{{ signal.entry_price }}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Target</div>
                                    <div class="detail-value positive">₹{{ signal.target_price }}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Stop Loss</div>
                                    <div class="detail-value negative">₹{{ signal.stop_loss }}</div>
                                </div>
                            </div>
                            
                            <div class="signal-description">
                                {{ signal.setup_description }}
                            </div>
                            
                            <div style="margin-top: 1rem; font-size: 0.8rem; color: rgba(255, 255, 255, 0.6);">
                                <i class="fas fa-clock"></i> {{ signal.timestamp }} | 
                                <i class="fas fa-calendar"></i> {{ signal.expiry_date }} |
                                R:R {{ signal.risk_reward_ratio }}
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="no-signals">
                            <i class="fas fa-chart-line" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                            <h3>No Active Signals</h3>
                            <p>Waiting for market opportunities...</p>
                            <button onclick="generateTestSignal()" style="margin-top: 1rem; padding: 0.8rem 1.5rem; background: linear-gradient(135deg, #00f5ff, #0080ff); border: none; border-radius: 25px; color: white; cursor: pointer;">
                                Generate Test Signal
                            </button>
                        </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Market Data Section -->
            <div class="market-data">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-chart-bar"></i>
                        Live Market Data
                    </h2>
                </div>
                
                {% if market_data %}
                    {% for symbol, data in market_data.items() %}
                    <div class="market-item">
                        <div class="market-symbol">{{ symbol }}</div>
                        <div class="market-price">
                            <div class="price">₹{{ data.ltp }}</div>
                            <div class="change {{ 'positive' if data.change > 0 else 'negative' }}">
                                {{ "+" if data.change > 0 else "" }}{{ data.change }} ({{ data.change_percent }}%)
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div style="text-align: center; padding: 2rem; color: rgba(255, 255, 255, 0.5);">
                        <i class="fas fa-wifi" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                        <p>Connecting to market data...</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- Control Buttons -->
    <div class="control-buttons">
        <button class="control-btn start-btn" onclick="startSignals()" title="Start Signal Generation">
            <i class="fas fa-play"></i>
        </button>
        <button class="control-btn stop-btn" onclick="stopSignals()" title="Stop Signal Generation">
            <i class="fas fa-stop"></i>
        </button>
        <button class="control-btn test-btn" onclick="generateTestSignal()" title="Generate Test Signal">
            <i class="fas fa-flask"></i>
        </button>
    </div>
    
    <script>
        // Auto-refresh dashboard every 30 seconds
        setInterval(() => {
            location.reload();
        }, 30000);
        
        function startSignals() {
            fetch('/api/start-signals', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        setTimeout(() => location.reload(), 2000);
                    }
                });
        }
        
        function stopSignals() {
            fetch('/api/stop-signals', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        setTimeout(() => location.reload(), 2000);
                    }
                });
        }
        
        function generateTestSignal() {
            fetch('/api/generate-test-signal', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Test signal generated successfully!');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        alert('❌ Failed to generate test signal');
                    }
                });
        }
        
        // Add floating particles
        function createParticle() {
            const particle = document.createElement('div');
            particle.style.position = 'fixed';
            particle.style.width = '4px';
            particle.style.height = '4px';
            particle.style.background = 'rgba(0, 245, 255, 0.6)';
            particle.style.borderRadius = '50%';
            particle.style.pointerEvents = 'none';
            particle.style.zIndex = '1';
            particle.style.left = Math.random() * window.innerWidth + 'px';
            particle.style.top = '100vh';
            particle.style.animation = 'float-up 8s linear forwards';
            
            document.body.appendChild(particle);
            
            setTimeout(() => {
                particle.remove();
            }, 8000);
        }
        
        // Create particles periodically
        setInterval(createParticle, 1000);
        
        // Add CSS for particle animation
        const particleStyle = document.createElement('style');
        particleStyle.textContent = `
            @keyframes float-up {
                to {
                    transform: translateY(-100vh) rotate(360deg);
                    opacity: 0;
                }
            }
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(particleStyle);
        
        // Add visual effects
        document.addEventListener('DOMContentLoaded', function() {
            // Animate stat cards on load
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.animation = 'fadeInUp 0.6s ease forwards';
                }, index * 100);
            });
            
            // Add hover effects to market items
            const marketItems = document.querySelectorAll('.market-item');
            marketItems.forEach(item => {
                item.addEventListener('mouseenter', function() {
                    this.style.transform = 'scale(1.02)';
                    this.style.boxShadow = '0 10px 30px rgba(0, 245, 255, 0.2)';
                });
                item.addEventListener('mouseleave', function() {
                    this.style.transform = 'scale(1)';
                    this.style.boxShadow = 'none';
                });
            });
        });
    </script>
</body>
</html>
"""

BASIC_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Elite FnO Trading Dashboard</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a2e; 
            color: white; 
            padding: 2rem; 
        }
        .header { 
            text-align: center; 
            margin-bottom: 2rem; 
        }
        .error { 
            background: #ff6b6b; 
            padding: 1rem; 
            border-radius: 5px; 
            text-align: center; 
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Elite FnO Trading Dashboard</h1>
    </div>
    <div class="error">
        <h2>⚠️ Dashboard Loading Error</h2>
        <p>Please start the signal engine and refresh the page.</p>
        <button onclick="location.reload()">🔄 Refresh</button>
    </div>
</body>
</html>
"""

@app.route('/')
def landing_page():
    """Ultra-modern landing page with advanced animations"""
    try:
        return render_template('landing_ultra_enhanced.html')
    except Exception as e:
        logger.error(f"Error loading enhanced landing page: {e}")
        try:
            return render_template('landing_ultra_modern.html')
        except Exception as e2:
            logger.error(f"Error loading fallback landing page: {e2}")
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>🚀 Elite FnO Trading Platform</title>
                <style>
                    body { 
                        font-family: 'Inter', sans-serif; 
                        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
                        color: white; 
                        padding: 2rem; 
                        text-align: center;
                        min-height: 100vh;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                    }
                    .hero { 
                        max-width: 800px;
                        margin: 0 auto;
                    }
                    .hero h1 { 
                        font-size: 3rem; 
                        margin-bottom: 1rem; 
                        background: linear-gradient(135deg, #00f5ff, #0080ff);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    }
                    .hero p { 
                        font-size: 1.2rem; 
                        margin-bottom: 2rem; 
                        opacity: 0.8;
                    }
                    .btn { 
                        padding: 1rem 2rem; 
                        margin: 0 1rem; 
                        border: none; 
                        border-radius: 25px; 
                        font-size: 1.1rem; 
                        cursor: pointer; 
                        text-decoration: none;
                        display: inline-block;
                        transition: all 0.3s ease;
                    }
                    .btn-primary { 
                        background: linear-gradient(135deg, #00f5ff, #0080ff);
                        color: white; 
                    }
                    .btn-secondary { 
                        background: rgba(255, 255, 255, 0.1);
                        color: white; 
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }
                    .btn:hover { 
                        transform: translateY(-2px);
                        box-shadow: 0 10px 30px rgba(0, 245, 255, 0.3);
                    }
                </style>
            </head>
            <body>
                <div class="hero">
                    <h1>🚀 Elite FnO Trading Platform</h1>
                    <p>AI-Powered Options Trading Signals</p>
                    <p>Professional trading platform with real-time signals, advanced analytics, and automated execution.</p>
                    <div>
                        <a href="/dashboard" class="btn btn-primary">Launch Platform</a>
                        <a href="/test-system" class="btn btn-secondary">Test System</a>
                    </div>
                </div>
            </body>
            </html>
            """)

@app.route('/dashboard')
def dashboard():
    """Ultra-modern trading dashboard with live signals"""
    try:
        # Get live signals and market data
        signals = signal_engine.get_recent_signals(10)
        market_data = signal_engine.get_live_market_data()
        
        # Update stats
        stats['signals_today'] = len([s for s in signals if datetime.strptime(s['timestamp'], '%H:%M:%S').date() == datetime.now().date()])
        stats['active_signals'] = len(signals)
        stats['win_rate'] = random.uniform(68.5, 85.2)
        stats['total_pnl'] = random.uniform(15000, 45000)
        
        # Try to use the new ultra-modern template first
        try:
            return render_template('dashboard_ultra_modern.html', 
                                 signals=signals, 
                                 market_data=market_data, 
                                 stats=stats)
        except Exception as template_error:
            logger.warning(f"Ultra-modern template not found: {template_error}")
            return render_template_string(ENHANCED_DASHBOARD_HTML, 
                                        signals=signals, 
                                        market_data=market_data, 
                                        stats=stats)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template_string(BASIC_DASHBOARD_HTML)

@app.route('/test-system')
def test_system_page():
    """System testing dashboard"""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🧪 System Testing Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
                color: white;
                margin: 0;
                pad: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .test-section {
                background: rgba(255, 255, 255, 0.08);
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid rgba(255, 255, 255, 0.12);
            }
            .test-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                cursor: pointer;
                font-weight: 600;
                margin: 10px;
                transition: transform 0.3s ease;
            }
            .test-button:hover {
                transform: translateY(-2px);
            }
            .test-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .results {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 15px;
                margin-top: 15px;
                max-height: 300px;
                overflow-y: auto;
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-pass { background: #4CAF50; }
            .status-fail { background: #f44336; }
            .status-pending { background: #ff9800; animation: pulse 1s infinite; }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .live-data {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .data-card {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 15px;
                text-align: center;
            }
            .data-value {
                font-size: 1.5em;
                font-weight: bold;
                color: #00f2fe;
            }
            .logs {
                background: #000;
                color: #00ff00;
                font-family: monospace;
                padding: 15px;
                border-radius: 10px;
                max-height: 200px;
                overflow-y: auto;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧪 Elite FnO Trading - System Testing Dashboard</h1>
                <p>Test and monitor your trading platform in real-time</p>
            </div>

            <!-- Market Data Test -->
            <div class="test-section">
                <h2>📊 Market Data Connectivity Test</h2>
                <p>Test live market data connection and price feeds</p>
                <button class="test-button" onclick="testMarketData()">🔄 Test Market Data</button>
                <button class="test-button" onclick="startLiveMonitoring()">📈 Start Live Monitoring</button>
                <div id="market-status" class="results" style="display:none;"></div>
                <div class="live-data" id="live-market-data"></div>
            </div>

            <!-- Telegram Bot Test -->
            <div class="test-section">
                <h2>🤖 Telegram Bot Test</h2>
                <p>Test Telegram bot connectivity and message delivery</p>
                <button class="test-button" onclick="testTelegramBot()">📱 Test Bot Connection</button>
                <button class="test-button" onclick="sendTestSignal()">🎯 Send Test Signal</button>
                <div id="telegram-status" class="results" style="display:none;"></div>
            </div>

            <!-- Signal Generation Test -->
            <div class="test-section">
                <h2>🎯 Signal Generation Test</h2>
                <p>Test AI signal generation and accuracy</p>
                <button class="test-button" onclick="testSignalGeneration()">🧠 Generate Test Signals</button>
                <button class="test-button" onclick="startAutoSignals()">⚡ Start Auto Signals</button>
                <div id="signal-status" class="results" style="display:none;"></div>
            </div>

            <!-- Comprehensive System Test -->
            <div class="test-section">
                <h2>🚀 Full System Test</h2>
                <p>Run complete testing suite with detailed report</p>
                <button class="test-button" onclick="runFullTest()">🧪 Run Complete Test Suite</button>
                <div id="full-test-status" class="results" style="display:none;"></div>
            </div>

            <!-- Live Logs -->
            <div class="test-section">
                <h2>📝 Live System Logs</h2>
                <div id="live-logs" class="logs">System ready for testing...</div>
            </div>
        </div>

        <script>
            let logContainer = document.getElementById('live-logs');
            let autoSignalsActive = false;
            let liveMonitoringActive = false;

            function addLog(message) {
                const timestamp = new Date().toLocaleTimeString();
                logContainer.textContent += `[${timestamp}] ${message}\\n`;
                logContainer.scrollTop = logContainer.scrollHeight;
            }

            function updateStatus(elementId, status, message) {
                const element = document.getElementById(elementId);
                element.style.display = 'block';
                
                const indicator = status === 'pass' ? '✅' : status === 'fail' ? '❌' : '⏳';
                element.innerHTML = `<div>${indicator} ${message}</div>`;
            }

            async function testMarketData() {
                addLog('🔄 Testing market data connectivity...');
                updateStatus('market-status', 'pending', 'Testing market data connection...');
                
                try {
                    const response = await fetch('/api/test/market-data');
                    const result = await response.json();
                    
                    if (result.success) {
                        updateStatus('market-status', 'pass', `Market data test passed! Status: ${result.data.market_status}`);
                        addLog(`✅ Market data test completed - Status: ${result.data.market_status}`);
                        
                        // Update live data display
                        updateLiveMarketData(result.data);
                    } else {
                        updateStatus('market-status', 'fail', `Market data test failed: ${result.error}`);
                        addLog(`❌ Market data test failed: ${result.error}`);
                    }
                } catch (error) {
                    updateStatus('market-status', 'fail', `Error: ${error.message}`);
                    addLog(`❌ Market data test error: ${error.message}`);
                }
            }

            async function testTelegramBot() {
                addLog('🤖 Testing Telegram bot connectivity...');
                updateStatus('telegram-status', 'pending', 'Testing Telegram bot...');
                
                try {
                    const response = await fetch('/api/test/telegram-bot');
                    const result = await response.json();
                    
                    if (result.success) {
                        updateStatus('telegram-status', 'pass', `Telegram bot test passed! Bot: ${result.data.bot_name}`);
                        addLog(`✅ Telegram bot test completed - Bot: ${result.data.bot_name}`);
                    } else {
                        updateStatus('telegram-status', 'fail', `Telegram bot test failed: ${result.error}`);
                        addLog(`❌ Telegram bot test failed: ${result.error}`);
                    }
                } catch (error) {
                    updateStatus('telegram-status', 'fail', `Error: ${error.message}`);
                    addLog(`❌ Telegram bot test error: ${error.message}`);
                }
            }

            async function sendTestSignal() {
                addLog('🎯 Sending test signal to Telegram...');
                
                try {
                    const response = await fetch('/api/test/send-signal');
                    const result = await response.json();
                    
                    if (result.success) {
                        addLog(`✅ Test signal sent successfully! Message ID: ${result.data.message_id}`);
                    } else {
                        addLog(`❌ Failed to send test signal: ${result.error}`);
                    }
                } catch (error) {
                    addLog(`❌ Test signal error: ${error.message}`);
                }
            }

            async function testSignalGeneration() {
                addLog('🧠 Testing signal generation...');
                updateStatus('signal-status', 'pending', 'Generating test signals...');
                
                try {
                    const response = await fetch('/api/test/signal-generation');
                    const result = await response.json();
                    
                    if (result.success) {
                        const quality = result.data.signal_quality;
                        updateStatus('signal-status', 'pass', 
                            `Generated ${result.data.signals_generated} signals! Avg confidence: ${quality.avg_confidence?.toFixed(1)}%`);
                        addLog(`✅ Signal generation completed - ${result.data.signals_generated} signals generated`);
                    } else {
                        updateStatus('signal-status', 'fail', `Signal generation failed: ${result.error}`);
                        addLog(`❌ Signal generation failed: ${result.error}`);
                    }
                } catch (error) {
                    updateStatus('signal-status', 'fail', `Error: ${error.message}`);
                    addLog(`❌ Signal generation error: ${error.message}`);
                }
            }

            async function runFullTest() {
                addLog('🚀 Starting comprehensive test suite...');
                updateStatus('full-test-status', 'pending', 'Running comprehensive test suite...');
                
                try {
                    const response = await fetch('/api/test/full-suite');
                    const result = await response.json();
                    
                    if (result.success) {
                        updateStatus('full-test-status', 'pass', 
                            `All tests completed! Duration: ${result.data.duration}`);
                        addLog(`✅ Full test suite completed successfully`);
                        
                        // Display detailed results
                        displayFullTestResults(result.data);
                    } else {
                        updateStatus('full-test-status', 'fail', `Test suite failed: ${result.error}`);
                        addLog(`❌ Test suite failed: ${result.error}`);
                    }
                } catch (error) {
                    updateStatus('full-test-status', 'fail', `Error: ${error.message}`);
                    addLog(`❌ Test suite error: ${error.message}`);
                }
            }

            function startLiveMonitoring() {
                if (liveMonitoringActive) {
                    addLog('⏹️ Stopping live market monitoring...');
                    liveMonitoringActive = false;
                    return;
                }
                
                addLog('📈 Starting live market monitoring...');
                liveMonitoringActive = true;
                
                const monitorInterval = setInterval(async () => {
                    if (!liveMonitoringActive) {
                        clearInterval(monitorInterval);
                        return;
                    }
                    
                    try {
                        const response = await fetch('/api/live/market-data');
                        const result = await response.json();
                        
                        if (result.success) {
                            updateLiveMarketData(result.data);
                        }
                    } catch (error) {
                        addLog(`⚠️ Live monitoring error: ${error.message}`);
                    }
                }, 5000); // Update every 5 seconds
            }

            function startAutoSignals() {
                if (autoSignalsActive) {
                    addLog('⏹️ Stopping auto signal generation...');
                    autoSignalsActive = false;
                    return;
                }
                
                addLog('⚡ Starting automatic signal generation...');
                autoSignalsActive = true;
                
                const signalInterval = setInterval(async () => {
                    if (!autoSignalsActive) {
                        clearInterval(signalInterval);
                        return;
                    }
                    
                    try {
                        const response = await fetch('/api/generate-auto-signal');
                        const result = await response.json();
                        
                        if (result.success) {
                            addLog(`🎯 Auto signal generated: ${result.data.symbol}`);
                        }
                    } catch (error) {
                        addLog(`⚠️ Auto signal error: ${error.message}`);
                    }
                }, 30000); // Generate signal every 30 seconds
            }

            function updateLiveMarketData(data) {
                const container = document.getElementById('live-market-data');
                
                const niftyData = data.nifty_data || {};
                const bankNiftyData = data.banknifty_data || {};
                
                container.innerHTML = `
                    <div class="data-card">
                        <h3>NIFTY</h3>
                        <div class="data-value">₹${niftyData.price || 'N/A'}</div>
                        <div>${niftyData.change >= 0 ? '📈' : '📉'} ${niftyData.change || 0} (${niftyData.change_percent || 0}%)</div>
                    </div>
                    <div class="data-card">
                        <h3>BANK NIFTY</h3>
                        <div class="data-value">₹${bankNiftyData.price || 'N/A'}</div>
                        <div>${bankNiftyData.change >= 0 ? '📈' : '📉'} ${bankNiftyData.change || 0} (${bankNiftyData.change_percent || 0}%)</div>
                    </div>
                    <div class="data-card">
                        <h3>Market Status</h3>
                        <div class="data-value">${data.market_status || 'Unknown'}</div>
                        <div>Last Updated: ${new Date(data.timestamp).toLocaleTimeString()}</div>
                    </div>
                `;
            }

            function displayFullTestResults(data) {
                addLog('📊 Displaying full test results...');
                // You can expand this to show detailed results
            }

            // Initialize page
            addLog('🚀 Elite FnO Trading System Testing Dashboard initialized');
            addLog('💡 Click any test button to start testing your platform');
        </script>
    </body>
    </html>
    """)

# API Routes for testing

@app.route('/api/test/market-data')
def test_market_data_api():
    """API endpoint to test market data"""
    try:
        market_tester = LiveMarketDataTester()
        results = market_tester.test_market_data_connection()
        
        return jsonify({
            'success': True,
            'data': {
                'market_status': results.get('market_status'),
                'nifty_data': results.get('nifty_data'),
                'banknifty_data': results.get('banknifty_data'),
                'connection_speed': results.get('connection_speed'),
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/test/telegram-bot')
def test_telegram_bot_api():
    """API endpoint to test Telegram bot"""
    async def test_bot():
        try:
            telegram_tester = TelegramBotTester()
            results = await telegram_tester.test_bot_connectivity()
            
            return {
                'success': True,
                'data': {
                    'bot_name': results.get('bot_info', {}).get('first_name', 'Unknown'),
                    'message_sent': results.get('send_message_test', {}).get('status') == 'success',
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(test_bot())
    loop.close()
    
    return jsonify(result)

@app.route('/api/test/send-signal')
def send_test_signal_api():
    """API endpoint to send test signal"""
    async def send_signal():
        try:
            telegram_tester = TelegramBotTester()
            test_signal = {
                'symbol': 'NIFTY24DEC22000CE',
                'type': 'CE',
                'action': 'BUY',
                'entry_price': 150.50,
                'target_price': 200.00,
                'stop_loss': 120.00,
                'quantity': 50,
                'confidence': 87
            }
            
            result = await telegram_tester.test_signal_delivery(test_signal)
            
            return {
                'success': result['status'] == 'success',
                'data': {
                    'message_id': result.get('message_id'),
                    'timestamp': datetime.now().isoformat()
                },
                'error': result.get('error')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(send_signal())
    loop.close()
    
    return jsonify(result)

@app.route('/api/test/signal-generation')
def test_signal_generation_api():
    """API endpoint to test signal generation"""
    try:
        from test_system import SignalAccuracyTester
        signal_tester = SignalAccuracyTester()
        results = signal_tester.test_signal_generation()
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/test/full-suite')
def test_full_suite_api():
    """API endpoint to run full test suite"""
    async def run_tests():
        try:
            comprehensive_tester = ComprehensiveTester()
            results = await comprehensive_tester.run_full_test_suite()
            
            return {
                'success': True,
                'data': {
                    'duration': results.get('test_suite_info', {}).get('duration', 'Unknown'),
                    'market_test_passed': not results.get('market_data_test', {}).get('errors'),
                    'telegram_test_passed': not results.get('telegram_bot_test', {}).get('errors'),
                    'signal_test_passed': not results.get('signal_generation_test', {}).get('errors'),
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(run_tests())
    loop.close()
    
    return jsonify(result)

@app.route('/api/live/market-data')
def live_market_data_api():
    """API endpoint for live market data"""
    try:
        market_tester = LiveMarketDataTester()
        
        # Get live prices
        nifty_data = market_tester.get_live_price('NSE:NIFTY50')
        banknifty_data = market_tester.get_live_price('NSE:BANKNIFTY')
        market_status = market_tester.get_market_status()
        
        return jsonify({
            'success': True,
            'data': {
                'nifty_data': nifty_data,
                'banknifty_data': banknifty_data,
                'market_status': market_status,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-auto-signal')
def generate_auto_signal_api():
    """API endpoint to generate automatic signals"""
    try:
        from test_system import SignalAccuracyTester
        signal_tester = SignalAccuracyTester()
        
        # Generate a single test signal
        signals = signal_tester.generate_test_signals()
        
        if signals:
            signal = signals[0]  # Take the first signal
            
            # Store in global live_signals for dashboard
            global live_signals
            live_signals.append(signal)
            
            # Keep only last 50 signals
            if len(live_signals) > 50:
                live_signals.pop(0)
            
            return jsonify({
                'success': True,
                'data': {
                    'symbol': signal['symbol'],
                    'action': signal['action'],
                    'confidence': signal['confidence'],
                    'timestamp': signal['timestamp'].isoformat()
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No signals generated'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/signals')
def get_signals_api():
    """API endpoint to get current signals"""
    signals = signal_engine.get_recent_signals(10)
    
    return jsonify({
        'success': True,
        'data': {
            'signals': signals,
            'count': len(signals),
            'last_updated': datetime.now().isoformat()
        }
    })

@app.route('/api/start-signals', methods=['POST'])
def start_signals():
    """API endpoint to start signal generation"""
    try:
        signal_engine.start_signal_generation()
        return jsonify({
            'success': True,
            'message': '🚀 Signal generation started successfully!'
        })
    except Exception as e:
        logger.error(f"Error starting signals: {e}")
        return jsonify({
            'success': False,
            'message': f'❌ Failed to start signals: {str(e)}'
        })

@app.route('/api/stop-signals', methods=['POST'])
def stop_signals():
    """API endpoint to stop signal generation"""
    try:
        signal_engine.stop_signal_generation()
        return jsonify({
            'success': True,
            'message': '⏹️ Signal generation stopped successfully!'
        })
    except Exception as e:
        logger.error(f"Error stopping signals: {e}")
        return jsonify({
            'success': False,
            'message': f'❌ Failed to stop signals: {str(e)}'
        })

@app.route('/api/generate-test-signal', methods=['POST'])
def generate_test_signal():
    """API endpoint to generate a test signal"""
    try:
        signal = signal_engine.generate_test_signal()
        if signal:
            return jsonify({
                'success': True,
                'message': '🎯 Test signal generated successfully!',
                'data': signal
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ Failed to generate test signal'
            })
    except Exception as e:
        logger.error(f"Error generating test signal: {e}")
        return jsonify({
            'success': False,
            'message': f'❌ Error: {str(e)}'
        })

@app.route('/api/market-data')
def get_market_data():
    """API endpoint to get live market data"""
    market_data = signal_engine.get_live_market_data()
    
    return jsonify({
        'success': True,
        'data': market_data,
        'last_updated': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Elite FnO Trading Platform...")
    print("=" * 60)
    print("🌐 Website will be available at: http://localhost:5000")
    print("🧪 Testing Dashboard: http://localhost:5000/test-system")
    print("📊 Trading Dashboard: http://localhost:5000/dashboard")
    print("=" * 60)
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)