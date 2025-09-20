import {
  createWebSocketConnection,
  sendAnalysisRequest,
  sendHeartbeat,
  calculateReconnectDelay,
  parseWebSocketMessage,
  isWebSocketReady
} from '@utils/websocket-utils.js'

describe('WebSocket Utils', () => {
  let mockWebSocket

  beforeEach(() => {
    // Ensure WebSocket constants are properly defined
    global.WebSocket.CONNECTING = 0
    global.WebSocket.OPEN = 1
    global.WebSocket.CLOSING = 2
    global.WebSocket.CLOSED = 3

    mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      readyState: WebSocket.OPEN,
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null
    }

    global.WebSocket = vi.fn(() => mockWebSocket)
    // Re-add constants to constructor function
    global.WebSocket.CONNECTING = 0
    global.WebSocket.OPEN = 1
    global.WebSocket.CLOSING = 2
    global.WebSocket.CLOSED = 3
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('createWebSocketConnection', () => {
    it('creates WebSocket with correct URL', () => {
      const url = 'ws://localhost:8000/ws'
      createWebSocketConnection(url)

      expect(global.WebSocket).toHaveBeenCalledWith(url)
    })

    it('sets up callbacks when provided', () => {
      const callbacks = {
        onOpen: vi.fn(),
        onMessage: vi.fn(),
        onError: vi.fn(),
        onClose: vi.fn()
      }

      createWebSocketConnection('ws://test', callbacks)

      expect(mockWebSocket.onopen).toBe(callbacks.onOpen)
      expect(mockWebSocket.onmessage).toBe(callbacks.onMessage)
      expect(mockWebSocket.onerror).toBe(callbacks.onError)
      expect(mockWebSocket.onclose).toBe(callbacks.onClose)
    })

    it('uses default callbacks when none provided', () => {
      createWebSocketConnection('ws://test')

      expect(typeof mockWebSocket.onopen).toBe('function')
      expect(typeof mockWebSocket.onmessage).toBe('function')
      expect(typeof mockWebSocket.onerror).toBe('function')
      expect(typeof mockWebSocket.onclose).toBe('function')
    })
  })

  describe('sendAnalysisRequest', () => {
    it('sends analysis request when WebSocket is ready', () => {
      const result = sendAnalysisRequest(mockWebSocket, 'base64data', 'environment')

      expect(result).toBe(true)
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: 'image_analysis',
          image_data: 'base64data',
          environment_description: 'environment'
        })
      )
    })

    it('returns false when WebSocket is not ready', () => {
      mockWebSocket.readyState = WebSocket.CONNECTING
      const result = sendAnalysisRequest(mockWebSocket, 'data', 'env')

      expect(result).toBe(false)
      expect(mockWebSocket.send).not.toHaveBeenCalled()
    })

    it('returns false when WebSocket is null', () => {
      const result = sendAnalysisRequest(null, 'data', 'env')

      expect(result).toBe(false)
    })
  })

  describe('sendHeartbeat', () => {
    it('sends heartbeat when WebSocket is ready', () => {
      const result = sendHeartbeat(mockWebSocket)

      expect(result).toBe(true)
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        JSON.stringify({ type: 'ping' })
      )
    })

    it('returns false when WebSocket is not ready', () => {
      mockWebSocket.readyState = WebSocket.CLOSED
      const result = sendHeartbeat(mockWebSocket)

      expect(result).toBe(false)
      expect(mockWebSocket.send).not.toHaveBeenCalled()
    })

    it('returns false when WebSocket is null', () => {
      const result = sendHeartbeat(null)

      expect(result).toBe(false)
    })
  })

  describe('calculateReconnectDelay', () => {
    it('calculates exponential backoff correctly', () => {
      expect(calculateReconnectDelay(0)).toBe(1000)
      expect(calculateReconnectDelay(1)).toBe(2000)
      expect(calculateReconnectDelay(2)).toBe(4000)
      expect(calculateReconnectDelay(3)).toBe(8000)
    })

    it('respects maximum delay', () => {
      expect(calculateReconnectDelay(10)).toBe(30000) // Default max
      expect(calculateReconnectDelay(10, 5000)).toBe(5000) // Custom max
    })

    it('handles zero attempt', () => {
      expect(calculateReconnectDelay(0)).toBe(1000)
    })
  })

  describe('parseWebSocketMessage', () => {
    it('parses valid JSON message', () => {
      const data = '{"type": "test", "data": "value"}'
      const result = parseWebSocketMessage(data)

      expect(result).toEqual({ type: 'test', data: 'value' })
    })

    it('returns null for invalid JSON', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const result = parseWebSocketMessage('invalid json {')

      expect(result).toBe(null)
      expect(consoleSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
    })

    it('handles empty string', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const result = parseWebSocketMessage('')

      expect(result).toBe(null)

      consoleSpy.mockRestore()
    })
  })

  describe('isWebSocketReady', () => {
    it('returns true when WebSocket is open', () => {
      expect(isWebSocketReady(mockWebSocket)).toBe(true)
    })

    it('returns false when WebSocket is connecting', () => {
      mockWebSocket.readyState = WebSocket.CONNECTING
      expect(isWebSocketReady(mockWebSocket)).toBe(false)
    })

    it('returns false when WebSocket is closing', () => {
      mockWebSocket.readyState = WebSocket.CLOSING
      expect(isWebSocketReady(mockWebSocket)).toBe(false)
    })

    it('returns false when WebSocket is closed', () => {
      mockWebSocket.readyState = WebSocket.CLOSED
      expect(isWebSocketReady(mockWebSocket)).toBe(false)
    })

    it('returns false when WebSocket is null', () => {
      expect(isWebSocketReady(null)).toBe(false)
    })

    it('returns false when WebSocket is undefined', () => {
      expect(isWebSocketReady(undefined)).toBe(false)
    })
  })
})
