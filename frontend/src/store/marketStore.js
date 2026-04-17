import { create } from 'zustand';

const useMarketStore = create((set) => ({
  marketRegime: null,
  signals: [],
  selectedStock: null,
  ws: null,
  
  setMarketRegime: (regime) => set({ marketRegime: regime }),
  setSignals: (signals) => set({ signals }),
  setSelectedStock: (stock) => set({ selectedStock: stock }),
  setWebSocket: (ws) => set({ ws }),
  
  connectWebSocket: () => {
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
    const wsUrl = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://');
    const ws = new WebSocket(`${wsUrl}/ws/live`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WS message:', data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    set({ ws });
    return ws;
  },
  
  disconnectWebSocket: () => {
    set((state) => {
      if (state.ws) {
        state.ws.close();
      }
      return { ws: null };
    });
  },
}));

export default useMarketStore;