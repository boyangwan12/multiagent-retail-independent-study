import type { AgentState } from '@/types';

type MessageHandler = (data: AgentState) => void;

export class MockWebSocket {
  private handlers: Set<MessageHandler> = new Set();
  private intervalId: ReturnType<typeof setInterval> | null = null;

  connect() {
    // Simulate agent progression: Demand → Inventory → Pricing
    let step = 0;
    const steps: Array<Omit<AgentState, 'timestamp'>> = [
      {
        agent_name: 'Demand Agent',
        status: 'thinking',
        progress_pct: 33,
        message: 'Running Prophet forecasting...',
      },
      {
        agent_name: 'Demand Agent',
        status: 'complete',
        progress_pct: 100,
        message: 'Forecast complete',
      },
      {
        agent_name: 'Inventory Agent',
        status: 'thinking',
        progress_pct: 66,
        message: 'Calculating allocations...',
      },
      {
        agent_name: 'Inventory Agent',
        status: 'complete',
        progress_pct: 100,
        message: 'Allocations complete',
      },
      {
        agent_name: 'Pricing Agent',
        status: 'thinking',
        progress_pct: 90,
        message: 'Analyzing markdown strategy...',
      },
      {
        agent_name: 'Pricing Agent',
        status: 'complete',
        progress_pct: 100,
        message: 'Workflow complete',
      },
    ];

    this.intervalId = setInterval(() => {
      if (step < steps.length) {
        const data: AgentState = {
          ...steps[step],
          timestamp: new Date().toISOString(),
        };
        this.broadcast(data);
        step++;
      } else {
        this.disconnect();
      }
    }, 2000); // 2 seconds between updates
  }

  onMessage(handler: MessageHandler) {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  private broadcast(data: AgentState) {
    this.handlers.forEach((handler) => handler(data));
  }

  disconnect() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }
}
