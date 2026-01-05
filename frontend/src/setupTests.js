require('@testing-library/jest-dom');

// Polyfill fetch for tests
global.fetch = require('jest-fetch-mock');

// Mock EventSource
global.EventSource = jest.fn().mockImplementation((url) => ({
  url,
  onopen: null,
  onmessage: null,
  onerror: null,
  readyState: 1, // OPEN
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
}));

// Mock styled-jsx
require('styled-jsx/css').default = {
  global: () => '',
  resolve: () => ({ styles: '', className: '' })
};