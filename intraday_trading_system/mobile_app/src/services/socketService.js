/**
 * Socket Service for real-time communication with trading bot
 */

import { io } from 'socket.io-client';

const SERVER_URL = 'http://localhost:5000'; // Change this to your server URL

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.listeners = new Map();
  }

  connect() {
    if (this.socket && this.isConnected) {
      return;
    }

    this.socket = io(SERVER_URL, {
      transports: ['websocket'],
      timeout: 5000,
    });

    this.socket.on('connect', () => {
      this.isConnected = true;
      console.log('Socket connected');
      this.emit('connect');
    });

    this.socket.on('disconnect', () => {
      this.isConnected = false;
      console.log('Socket disconnected');
      this.emit('disconnect');
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      this.isConnected = false;
    });

    // Listen for trading bot events
    this.socket.on('bot_status', (data) => {
      this.emit('bot_status', data);
    });

    this.socket.on('market_update', (data) => {
      this.emit('market_update', data);
    });

    this.socket.on('new_signal', (data) => {
      this.emit('new_signal', data);
    });

    this.socket.on('signals_update', (data) => {
      this.emit('signals_update', data);
    });

    this.socket.on('error', (data) => {
      console.error('Socket error:', data);
      this.emit('error', data);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback = null) {
    if (!this.listeners.has(event)) {
      return;
    }

    if (callback) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    } else {
      this.listeners.delete(event);
    }
  }

  emit(event, data = null) {
    // Emit to registered listeners
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${event} listener:`, error);
        }
      });
    }
  }

  // Send request for updates
  requestUpdate() {
    if (this.socket && this.isConnected) {
      this.socket.emit('request_update');
    }
  }

  // Check connection status
  getConnectionStatus() {
    return this.isConnected;
  }

  // Reconnect manually
  reconnect() {
    this.disconnect();
    setTimeout(() => {
      this.connect();
    }, 1000);
  }
}

export const socketService = new SocketService();