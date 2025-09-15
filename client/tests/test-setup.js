import '@testing-library/jest-dom'

// Mock CSS imports to avoid Tailwind parsing issues in tests
vi.mock('~/styles.css', () => ({}))
vi.mock('@/styles.css', () => ({}))

// Mock WebSocket for tests
global.WebSocket = class MockWebSocket {
  constructor(url) {
    this.url = url
    this.readyState = WebSocket.CONNECTING
    setTimeout(() => {
      this.readyState = WebSocket.OPEN
      if (this.onopen) this.onopen()
    }, 0)
  }

  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  send(data) {
    // Mock send method
  }

  close() {
    this.readyState = WebSocket.CLOSED
    if (this.onclose) this.onclose({ code: 1000, reason: 'Normal closure' })
  }
}

// Mock File and FileReader for image upload tests
global.File = class MockFile {
  constructor(parts, filename, properties = {}) {
    this.name = filename
    this.size = parts.reduce((acc, part) => acc + part.length, 0)
    this.type = properties.type || ''
    this.lastModified = properties.lastModified || Date.now()
  }
}

global.FileReader = class MockFileReader {
  constructor() {
    this.readyState = 0
    this.result = null
    this.error = null
  }

  static EMPTY = 0
  static LOADING = 1
  static DONE = 2

  readAsDataURL(file) {
    setTimeout(() => {
      this.readyState = MockFileReader.DONE
      this.result = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
      if (this.onload) this.onload({ target: this })
    }, 0)
  }
}

// Mock ResizeObserver for chart.js
global.ResizeObserver = class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Mock Canvas for chart.js
global.HTMLCanvasElement.prototype.getContext = () => ({
  fillRect: () => {},
  clearRect: () => {},
  getImageData: () => ({ data: new Array(4) }),
  putImageData: () => {},
  createImageData: () => new ImageData(1, 1),
  setTransform: () => {},
  drawImage: () => {},
  save: () => {},
  fillText: () => {},
  restore: () => {},
  beginPath: () => {},
  moveTo: () => {},
  lineTo: () => {},
  closePath: () => {},
  stroke: () => {},
  translate: () => {},
  scale: () => {},
  rotate: () => {},
  arc: () => {},
  fill: () => {},
  measureText: () => ({ width: 0 }),
  transform: () => {},
  rect: () => {},
  clip: () => {},
})

// Mock CSS parsing to avoid jsdom issues with complex CSS
Object.defineProperty(window, 'CSS', {
  value: {
    supports: () => false,
  }
})

// Mock getComputedStyle for CSS testing
Object.defineProperty(window, 'getComputedStyle', {
  value: () => ({
    getPropertyValue: () => '',
  }),
})

// Silence console errors during tests unless explicitly testing error handling
const originalError = console.error
const originalWarn = console.warn
beforeAll(() => {
  console.error = (...args) => {
    // Ignore CSS parsing errors and React warnings in tests
    if (
      args[0]?.includes?.('Warning:') ||
      args[0]?.includes?.('Error:') ||
      args[0]?.includes?.('Could not parse CSS') ||
      args[0]?.includes?.('stylesheet')
    ) {
      return
    }
    originalError.call(console, ...args)
  }

  console.warn = (...args) => {
    // Ignore Tailwind warnings in tests
    if (args[0]?.includes?.('content') && args[0]?.includes?.('pattern')) {
      return
    }
    originalWarn.call(console, ...args)
  }
})

afterAll(() => {
  console.error = originalError
  console.warn = originalWarn
})
