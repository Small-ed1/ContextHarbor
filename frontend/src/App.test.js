import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import App from './App';

beforeEach(() => {
  // Mock all fetches to return empty arrays or objects
  fetch.mockResponse((req) => {
    if (req.url.includes('/api/settings')) {
      return Promise.resolve(JSON.stringify({
        theme: 'dark',
        homeModelPreference: 'default'
      }));
    }
    return Promise.resolve(JSON.stringify([]));
  });
});

test('renders Router Phase 1 title', async () => {
  render(<App />);
  const titleElement = await screen.findByText(/Welcome to Router Phase 1/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders start chat button', async () => {
  render(<App />);
  const buttonElement = await screen.findByText(/Start Chat/i);
  expect(buttonElement).toBeInTheDocument();
});

test('renders deep research button', async () => {
  render(<App />);
  const buttons = await screen.findAllByText(/Deep Research/i);
  expect(buttons.length).toBeGreaterThan(0);
});

test('renders sidebar with settings', async () => {
  render(<App />);
  const settingsElement = await screen.findByText(/Settings/i);
  expect(settingsElement).toBeInTheDocument();
});

test('renders sidebar with chat sessions', async () => {
  render(<App />);
  const sessionsElement = await screen.findByText(/Chat Sessions/i);
  expect(sessionsElement).toBeInTheDocument();
});

test('renders sidebar with documents mode', async () => {
  render(<App />);
  const documentsElement = await screen.findByText(/Documents/i);
  expect(documentsElement).toBeInTheDocument();
});