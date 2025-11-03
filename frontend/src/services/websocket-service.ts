import { buildWsUrl } from '@/config/api';
import type { WebSocketMessageType } from '@/types/websocket';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000; // 2 seconds
  private messageHandlers: ((message: WebSocketMessageType) => void)[] = [];

  /**
   * Connect to WebSocket stream for a workflow
   */
  connect(workflowId: string): void {
    const wsUrl = buildWsUrl(`/api/v1/workflows/${workflowId}/stream`);
    console.log('Connecting to WebSocket:', wsUrl);

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessageType = JSON.parse(event.data);
          console.log('WebSocket message:', message);

          // Notify all handlers
          this.messageHandlers.forEach(handler => handler(message));
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);

        // Auto-reconnect if not a normal closure
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);

          setTimeout(() => {
            this.connect(workflowId);
          }, this.reconnectDelay);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }

  /**
   * Add a message handler
   */
  onMessage(handler: (message: WebSocketMessageType) => void): void {
    this.messageHandlers.push(handler);
  }

  /**
   * Remove a message handler
   */
  offMessage(handler: (message: WebSocketMessageType) => void): void {
    this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
  }

  /**
   * Close the WebSocket connection
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
      this.messageHandlers = [];
    }
  }

  /**
   * Get connection state
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
