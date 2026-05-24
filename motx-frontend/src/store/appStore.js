import { create } from 'zustand';

const storageAvailable = typeof window !== 'undefined' && typeof window.localStorage !== 'undefined' &&
  typeof window.localStorage.getItem === 'function' && typeof window.localStorage.setItem === 'function';
const initialUserId = storageAvailable ? window.localStorage.getItem('userId') : null;

const useStore = create((set, get) => ({
  userId: initialUserId || `user_${Date.now()}`,
  setUserId: (id) => {
    if (storageAvailable && typeof window.localStorage.setItem === 'function') {
      window.localStorage.setItem('userId', id);
    }
    set({ userId: id });
  },
  webSocket: null,
  ambientWebSocket: null,
  eyeWebSocket: null,
  setWebSocket: (ws) => set({ webSocket: ws }),
  setAmbientWebSocket: (ws) => set({ ambientWebSocket: ws }),
  setEyeWebSocket: (ws) => set({ eyeWebSocket: ws }),
  ambientData: null,
  setAmbientData: (data) => set({ ambientData: data }),
  eyePosition: null,
  setEyePosition: (position) => set({ eyePosition: position }),
  executionHistory: [],
  addExecution: (execution) => set((state) => ({
    executionHistory: [execution, ...state.executionHistory].slice(0, 50)
  })),
  clearHistory: () => set({ executionHistory: [] }),
  playerProfile: null,
  setPlayerProfile: (profile) => set({ playerProfile: profile }),
  analyticsData: null,
  setAnalyticsData: (data) => set({ analyticsData: data }),
  agentStatus: [],
  setAgentStatus: (status) => set({ agentStatus: status }),
  activeTab: 'dashboard',
  setActiveTab: (tab) => set({ activeTab: tab }),
  notifications: [],
  addNotification: (notification) => set((state) => ({
    notifications: [
      ...state.notifications,
      { id: Date.now(), ...notification }
    ]
  })),
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter((n) => n.id !== id)
  })),
  sendWebSocketMessage: (message) => {
    const ws = get().webSocket;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  }
}));

export default useStore;
