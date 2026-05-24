export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const defaultWsHost = API_BASE.replace(/^http/, 'ws');
export const WS_BASE = import.meta.env.VITE_WS_URL || (defaultWsHost.endsWith('/ws') ? defaultWsHost : `${defaultWsHost}/ws`);
