import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from './App';

// Mock du WebSocket pour éviter les erreurs de connexion dans jsdom
global.WebSocket = vi.fn().mockImplementation(() => ({
  onopen: vi.fn(),
  onclose: vi.fn(),
  onerror: vi.fn(),
  onmessage: vi.fn(),
  send: vi.fn(),
  close: vi.fn(),
  readyState: 1, // OPEN
}));

describe('App Component', () => {
  it('renders without crashing and displays connection status', () => {
    render(<App />);
    // Le composant commence déconnecté, mais le useEffect va instancier le WS.
    // L'état initial est affiché au moins une fois
    expect(screen.getAllByText(/Déconnecté|Connecté/i).length).toBeGreaterThan(0);
  });
});
