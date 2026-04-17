import { useState, useCallback } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const useMarketData = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMarketRegime = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/market/regime`);
      return response.data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchTopSignals = useCallback(async (timeframe = 'swing') => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/signals/top10?timeframe=${timeframe}`);
      return response.data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const runScanner = useCallback(async (timeframe = 'swing') => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/scanner/run?timeframe=${timeframe}`);
      return response.data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStockDetail = useCallback(async (ticker) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/signals/${ticker}`);
      return response.data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSentiment = useCallback(async (ticker) => {
    try {
      const response = await axios.get(`${API}/sentiment/${ticker}`);
      return response.data;
    } catch {
      return null;
    }
  }, []);

  const fetchStrategies = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/strategies/list`);
      return response.data;
    } catch {
      return null;
    }
  }, []);

  const runBacktest = useCallback(async (strategy, capital = 100000) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/backtest/run?strategy=${strategy}&capital=${capital}`);
      return response.data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const calculateRisk = useCallback(async (params) => {
    try {
      const queryStr = new URLSearchParams(params).toString();
      const response = await axios.get(`${API}/portfolio/risk?${queryStr}`);
      return response.data;
    } catch {
      return null;
    }
  }, []);

  return { loading, error, fetchMarketRegime, fetchTopSignals, runScanner, fetchStockDetail, fetchSentiment, fetchStrategies, runBacktest, calculateRisk };
};
