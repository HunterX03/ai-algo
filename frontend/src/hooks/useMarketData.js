import { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const useMarketData = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMarketRegime = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/market/regime`);
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return null;
    }
  };

  const fetchTopSignals = async (timeframe = 'swing') => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/signals/top10?timeframe=${timeframe}`);
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return null;
    }
  };

  const runScanner = async (timeframe = 'swing') => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/scanner/run?timeframe=${timeframe}`);
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return null;
    }
  };

  const fetchStockDetail = async (ticker) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/signals/${ticker}`);
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return null;
    }
  };

  const fetchSentiment = async (ticker) => {
    try {
      const response = await axios.get(`${API}/sentiment/${ticker}`);
      return response.data;
    } catch (err) {
      console.error('Sentiment fetch error:', err);
      return null;
    }
  };

  const fetchStrategies = async () => {
    try {
      const response = await axios.get(`${API}/strategies/list`);
      return response.data;
    } catch (err) {
      console.error('Strategies fetch error:', err);
      return null;
    }
  };

  const runBacktest = async (strategy, capital = 100000) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/backtest/run?strategy=${strategy}&capital=${capital}`);
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return null;
    }
  };

  const calculateRisk = async (params) => {
    try {
      const queryStr = new URLSearchParams(params).toString();
      const response = await axios.get(`${API}/portfolio/risk?${queryStr}`);
      return response.data;
    } catch (err) {
      console.error('Risk calculation error:', err);
      return null;
    }
  };

  return {
    loading,
    error,
    fetchMarketRegime,
    fetchTopSignals,
    runScanner,
    fetchStockDetail,
    fetchSentiment,
    fetchStrategies,
    runBacktest,
    calculateRisk
  };
};