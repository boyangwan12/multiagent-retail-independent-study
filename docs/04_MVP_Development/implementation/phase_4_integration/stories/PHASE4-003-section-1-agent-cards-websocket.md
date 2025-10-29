# Story: Integrate Section 1 - Agent Cards with Real WebSocket Connection

**Epic:** Phase 4 - Frontend/Backend Integration
**Story ID:** PHASE4-003
**Status:** Ready for Implementation
**Estimate:** 6 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE4-002 (Section 0 - Parameter Gathering)

---

## Story

As a user,
I want to see real-time progress updates from the backend agents as they process my forecast workflow,
So that I understand what the system is doing and can monitor the workflow execution.

**Business Value:** Real-time agent status updates provide transparency and build user trust. Without WebSocket integration, users have no visibility into workflow execution, making the system feel like a black box. This is critical for user experience and debugging.

**Epic Context:** This is Story 3 of 9 in Phase 4. It replaces the setTimeout-based mock WebSocket with a real WebSocket connection to the backend. This enables live updates from mock agents (Demand, Inventory, Pricing) as they execute. This is the first time frontend and backend communicate in real-time.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ POST /api/workflows/forecast endpoint tested with Postman (returns workflow_id)
2. ✅ WebSocket connection establishes to ws://localhost:8000/api/workflows/{id}/stream
3. ✅ Frontend listens for 6 message types: agent_started, agent_progress, agent_completed, human_input_required, workflow_complete, error
4. ✅ Agent cards update in real-time as messages arrive
5. ✅ Mock agents (Demand, Inventory, Pricing) return dynamic data based on parameters
6. ✅ Progress bars update based on agent_progress messages
7. ✅ Agent status badges update (idle → running → complete)
8. ✅ WebSocket reconnects automatically if connection drops
9. ✅ Workflow completes successfully and displays results
10. ✅ All 3 agent cards show correct final status

### Quality Requirements

11. ✅ WebSocket messages arrive in <1 second of backend sending
12. ✅ No console errors during WebSocket connection
13. ✅ Connection cleanup on component unmount (no memory leaks)
14. ✅ Test with backend restart (reconnection works)
15. ✅ Mock agents adapt output based on SeasonParameters

---

## Tasks

### Task 1: Test Backend Workflow Endpoint with Postman

**Goal:** Verify the workflow creation endpoint works BEFORE integrating with frontend.

**Subtasks:**
- [ ] Start backend server: `uv run uvicorn app.main:app --reload`
- [ ] Open Postman and create new request:
  - Method: POST
  - URL: `http://localhost:8000/api/workflows/forecast`
  - Headers: `Content-Type: application/json`
  - Body (raw JSON):
    ```json
    {
      "parameters": {
        "forecast_horizon_weeks": 12,
        "season_start_date": "2025-11-03",
        "season_end_date": "2026-01-25",
        "replenishment_strategy": "weekly",
        "dc_holdback_percentage": 0.45,
        "markdown_checkpoint_week": 6,
        "markdown_threshold": 0.60
      },
      "category_name": "Women's Dresses"
    }
    ```

- [ ] Send request and verify response (200 OK):
  ```json
  {
    "workflow_id": "wf_abc123def456",
    "status": "initiated",
    "message": "Workflow started successfully",
    "websocket_url": "ws://localhost:8000/api/workflows/wf_abc123def456/stream"
  }
  ```

- [ ] Copy `workflow_id` and `websocket_url` for WebSocket testing

**Validation:**
- Request returns 200 OK
- Response includes workflow_id
- Response includes websocket_url
- workflow_id is unique (test multiple times)

---

### Task 2: Test Backend WebSocket with wscat or Postman

**Goal:** Verify WebSocket server works BEFORE integrating with frontend.

**Subtasks:**
- [ ] Install wscat (WebSocket client): `npm install -g wscat`

- [ ] Connect to WebSocket (replace {workflow_id} with actual ID from Task 1):
  ```bash
  wscat -c ws://localhost:8000/api/workflows/wf_abc123def456/stream
  ```

- [ ] Verify you receive messages in this order:

  **Message 1: agent_started (Demand Agent)**
  ```json
  {
    "type": "agent_started",
    "agent": "Demand Agent",
    "timestamp": "2025-10-29T10:30:00Z"
  }
  ```

  **Message 2: agent_progress (Demand Agent)**
  ```json
  {
    "type": "agent_progress",
    "agent": "Demand Agent",
    "message": "Running Prophet forecasting model...",
    "progress_pct": 33,
    "timestamp": "2025-10-29T10:30:05Z"
  }
  ```

  **Message 3: agent_progress (Demand Agent)**
  ```json
  {
    "type": "agent_progress",
    "agent": "Demand Agent",
    "message": "Running ARIMA forecasting model...",
    "progress_pct": 66,
    "timestamp": "2025-10-29T10:30:10Z"
  }
  ```

  **Message 4: agent_completed (Demand Agent)**
  ```json
  {
    "type": "agent_completed",
    "agent": "Demand Agent",
    "duration_seconds": 18,
    "result": {
      "total_season_demand": 8000,
      "safety_stock_pct": 0.25,
      "adaptation_reasoning": "No replenishment strategy → increased safety stock from 20% to 25%"
    },
    "timestamp": "2025-10-29T10:30:18Z"
  }
  ```

  **Message 5: agent_started (Inventory Agent)**
  ```json
  {
    "type": "agent_started",
    "agent": "Inventory Agent",
    "timestamp": "2025-10-29T10:30:19Z"
  }
  ```

  **... (similar for Inventory Agent)**

  **Message 6: agent_started (Pricing Agent)**
  ```json
  {
    "type": "agent_started",
    "agent": "Pricing Agent",
    "timestamp": "2025-10-29T10:30:35Z"
  }
  ```

  **... (similar for Pricing Agent)**

  **Message 7: workflow_complete**
  ```json
  {
    "type": "workflow_complete",
    "workflow_id": "wf_abc123def456",
    "duration_seconds": 45,
    "result": {
      "forecast_id": "fc_xyz789",
      "allocation_id": "al_xyz789",
      "markdown_id": "md_xyz789"
    },
    "timestamp": "2025-10-29T10:30:45Z"
  }
  ```

- [ ] Verify messages arrive in correct order
- [ ] Verify timestamps are sequential
- [ ] Verify all 3 agents execute (Demand → Inventory → Pricing)

**Validation:**
- WebSocket connection establishes successfully
- All 6 message types received
- Messages arrive in real-time (not all at once)
- Connection stays open until workflow_complete
- Connection closes gracefully after workflow_complete

---

### Task 3: Create TypeScript Types for WebSocket Messages

**Subtasks:**
- [ ] Create `frontend/src/types/websocket.ts`:
  ```typescript
  // Base WebSocket message
  export interface WebSocketMessage {
    type:
      | "agent_started"
      | "agent_progress"
      | "agent_completed"
      | "human_input_required"
      | "workflow_complete"
      | "error";
    timestamp: string;
  }

  // Agent Started
  export interface AgentStartedMessage extends WebSocketMessage {
    type: "agent_started";
    agent: "Demand Agent" | "Inventory Agent" | "Pricing Agent";
  }

  // Agent Progress
  export interface AgentProgressMessage extends WebSocketMessage {
    type: "agent_progress";
    agent: string;
    message: string;
    progress_pct: number; // 0-100
  }

  // Agent Completed
  export interface AgentCompletedMessage extends WebSocketMessage {
    type: "agent_completed";
    agent: string;
    duration_seconds: number;
    result: any; // Agent-specific result object
  }

  // Human Input Required (for approvals)
  export interface HumanInputRequiredMessage extends WebSocketMessage {
    type: "human_input_required";
    agent: string;
    action: "approve_manufacturing_order" | "approve_markdown";
    data: any;
    options: string[]; // ["modify", "accept"]
  }

  // Workflow Complete
  export interface WorkflowCompleteMessage extends WebSocketMessage {
    type: "workflow_complete";
    workflow_id: string;
    duration_seconds: number;
    result: {
      forecast_id: string;
      allocation_id: string;
      markdown_id: string | null;
    };
  }

  // Error
  export interface ErrorMessage extends WebSocketMessage {
    type: "error";
    agent: string;
    error_message: string;
  }

  // Union type for all messages
  export type WebSocketMessageType =
    | AgentStartedMessage
    | AgentProgressMessage
    | AgentCompletedMessage
    | HumanInputRequiredMessage
    | WorkflowCompleteMessage
    | ErrorMessage;

  // Agent Status
  export type AgentStatus = "idle" | "running" | "complete" | "error";

  // Agent State
  export interface AgentState {
    name: "Demand Agent" | "Inventory Agent" | "Pricing Agent";
    status: AgentStatus;
    progress: number; // 0-100
    messages: string[];
    duration: number | null;
    result: any | null;
  }
  ```

- [ ] Export types for use in components

**Validation:**
- TypeScript compiles without errors
- Types cover all 6 message types

---

### Task 4: Create WebSocket Client Service

**Subtasks:**
- [ ] Create `frontend/src/services/websocket-service.ts`:
  ```typescript
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
      const wsUrl = buildWsUrl(`/api/workflows/${workflowId}/stream`);
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
  ```

- [ ] Test service in isolation:
  ```typescript
  // Test in browser console
  const ws = new WebSocketService();
  ws.onMessage((message) => {
    console.log('Received:', message);
  });
  ws.connect('wf_abc123def456');

  // After workflow completes:
  ws.disconnect();
  ```

**Validation:**
- Service connects to WebSocket successfully
- Messages logged to console
- Reconnection works (test by restarting backend)
- Disconnect cleans up properly

---

### Task 5: Create useWebSocket Hook

**Subtasks:**
- [ ] Create `frontend/src/hooks/useWebSocket.ts`:
  ```typescript
  import { useEffect, useRef, useState } from 'react';
  import { WebSocketService } from '@/services/websocket-service';
  import type { WebSocketMessageType, AgentState } from '@/types/websocket';

  export function useWebSocket(workflowId: string | null) {
    const wsRef = useRef<WebSocketService | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [agents, setAgents] = useState<AgentState[]>([
      { name: 'Demand Agent', status: 'idle', progress: 0, messages: [], duration: null, result: null },
      { name: 'Inventory Agent', status: 'idle', progress: 0, messages: [], duration: null, result: null },
      { name: 'Pricing Agent', status: 'idle', progress: 0, messages: [], duration: null, result: null },
    ]);
    const [workflowComplete, setWorkflowComplete] = useState(false);
    const [workflowResult, setWorkflowResult] = useState<any>(null);

    useEffect(() => {
      if (!workflowId) return;

      // Create WebSocket service
      const ws = new WebSocketService();
      wsRef.current = ws;

      // Handle incoming messages
      ws.onMessage((message: WebSocketMessageType) => {
        handleMessage(message);
      });

      // Connect to WebSocket
      ws.connect(workflowId);
      setIsConnected(true);

      // Cleanup on unmount
      return () => {
        ws.disconnect();
        setIsConnected(false);
      };
    }, [workflowId]);

    const handleMessage = (message: WebSocketMessageType) => {
      switch (message.type) {
        case 'agent_started':
          setAgents(prev =>
            prev.map(agent =>
              agent.name === message.agent
                ? { ...agent, status: 'running', progress: 0, messages: ['Started'] }
                : agent
            )
          );
          break;

        case 'agent_progress':
          setAgents(prev =>
            prev.map(agent =>
              agent.name === message.agent
                ? {
                    ...agent,
                    status: 'running',
                    progress: message.progress_pct,
                    messages: [...agent.messages, message.message],
                  }
                : agent
            )
          );
          break;

        case 'agent_completed':
          setAgents(prev =>
            prev.map(agent =>
              agent.name === message.agent
                ? {
                    ...agent,
                    status: 'complete',
                    progress: 100,
                    duration: message.duration_seconds,
                    result: message.result,
                    messages: [...agent.messages, 'Completed'],
                  }
                : agent
            )
          );
          break;

        case 'workflow_complete':
          setWorkflowComplete(true);
          setWorkflowResult(message.result);
          break;

        case 'error':
          setAgents(prev =>
            prev.map(agent =>
              agent.name === message.agent
                ? {
                    ...agent,
                    status: 'error',
                    messages: [...agent.messages, `Error: ${message.error_message}`],
                  }
                : agent
            )
          );
          break;

        case 'human_input_required':
          // Handle approval requests (future story)
          console.log('Human input required:', message);
          break;
      }
    };

    return {
      isConnected,
      agents,
      workflowComplete,
      workflowResult,
    };
  }
  ```

- [ ] Test hook in a component:
  ```typescript
  function TestWebSocket() {
    const { isConnected, agents, workflowComplete, workflowResult } = useWebSocket('wf_abc123');

    return (
      <div>
        <p>Connected: {isConnected ? 'Yes' : 'No'}</p>
        {agents.map(agent => (
          <div key={agent.name}>
            <h3>{agent.name}</h3>
            <p>Status: {agent.status}</p>
            <p>Progress: {agent.progress}%</p>
            <ul>
              {agent.messages.map((msg, i) => <li key={i}>{msg}</li>)}
            </ul>
          </div>
        ))}
        {workflowComplete && <p>Workflow complete! Result: {JSON.stringify(workflowResult)}</p>}
      </div>
    );
  }
  ```

**Validation:**
- Hook connects to WebSocket when workflowId provided
- Agent states update as messages arrive
- Component re-renders on each message
- Cleanup works on unmount

---

### Task 6: Update AgentWorkflow Component with Real WebSocket

**Subtasks:**
- [ ] Locate `frontend/src/components/AgentWorkflow/AgentWorkflow.tsx`

- [ ] Replace mock WebSocket with real hook:

  **Before (Mock):**
  ```typescript
  useEffect(() => {
    // Mock WebSocket with setTimeout
    const interval = setInterval(() => {
      setAgents(prev => {
        // ... update agents with mock data
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);
  ```

  **After (Real WebSocket):**
  ```typescript
  import { useWebSocket } from '@/hooks/useWebSocket';

  function AgentWorkflow({ workflowId }: { workflowId: string | null }) {
    const { isConnected, agents, workflowComplete, workflowResult } = useWebSocket(workflowId);

    return (
      <div>
        {/* Connection status indicator */}
        {workflowId && (
          <div className="flex items-center gap-2 mb-4">
            <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-gray-600">
              {isConnected ? 'Connected to workflow' : 'Disconnected'}
            </span>
          </div>
        )}

        {/* Agent Cards */}
        <div className="grid grid-cols-3 gap-4">
          {agents.map(agent => (
            <AgentCard key={agent.name} agent={agent} />
          ))}
        </div>

        {/* Workflow Complete Message */}
        {workflowComplete && (
          <Alert className="mt-4">
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle>Workflow Complete!</AlertTitle>
            <AlertDescription>
              Forecast ID: {workflowResult?.forecast_id}
            </AlertDescription>
          </Alert>
        )}
      </div>
    );
  }
  ```

- [ ] Update AgentCard component to display agent state:
  ```typescript
  function AgentCard({ agent }: { agent: AgentState }) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{agent.name}</span>
            <Badge variant={
              agent.status === 'idle' ? 'secondary' :
              agent.status === 'running' ? 'default' :
              agent.status === 'complete' ? 'success' : 'destructive'
            }>
              {agent.status}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Progress Bar */}
          {agent.status === 'running' && (
            <Progress value={agent.progress} className="mb-2" />
          )}

          {/* Messages */}
          <div className="space-y-1">
            {agent.messages.slice(-3).map((msg, i) => (
              <p key={i} className="text-xs text-gray-600">
                {msg}
              </p>
            ))}
          </div>

          {/* Duration */}
          {agent.duration && (
            <p className="text-xs text-gray-500 mt-2">
              Completed in {agent.duration}s
            </p>
          )}
        </CardContent>
      </Card>
    );
  }
  ```

**Validation:**
- Agent cards update in real-time as WebSocket messages arrive
- Progress bars animate smoothly
- Status badges change color (idle → running → complete)
- Connection indicator shows correct state

---

### Task 7: Integrate Workflow Initiation from Section 0

**Subtasks:**
- [ ] Update ParameterGathering component to start workflow after confirmation:

  ```typescript
  import { WorkflowService } from '@/services/workflow-service';

  const [workflowId, setWorkflowId] = useState<string | null>(null);

  const handleConfirmParameters = async () => {
    setState(prev => ({ ...prev, isConfirmed: true }));
    setShowConfirmationModal(false);

    try {
      // Start workflow
      const response = await WorkflowService.createForecastWorkflow({
        parameters: state.extractedParameters!,
        category_name: 'Women\'s Dresses', // TODO: Let user select category
      });

      setWorkflowId(response.workflow_id);
      console.log('Workflow started:', response.workflow_id);
      console.log('WebSocket URL:', response.websocket_url);

      // Scroll to Section 1 (Agent Cards)
      document.getElementById('section-1-agent-cards')?.scrollIntoView({
        behavior: 'smooth',
      });
    } catch (error) {
      console.error('Failed to start workflow:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to start workflow. Please try again.',
      }));
    }
  };
  ```

- [ ] Create WorkflowService:
  ```typescript
  // frontend/src/services/workflow-service.ts
  import { ApiClient } from '@/utils/api-client';
  import { API_ENDPOINTS } from '@/config/api';
  import type { SeasonParameters } from '@/types/parameters';

  interface CreateForecastWorkflowRequest {
    parameters: SeasonParameters;
    category_name: string;
  }

  interface CreateForecastWorkflowResponse {
    workflow_id: string;
    status: string;
    message: string;
    websocket_url: string;
  }

  export class WorkflowService {
    static async createForecastWorkflow(
      request: CreateForecastWorkflowRequest
    ): Promise<CreateForecastWorkflowResponse> {
      return ApiClient.post<CreateForecastWorkflowResponse>(
        API_ENDPOINTS.WORKFLOWS_FORECAST,
        request
      );
    }
  }
  ```

- [ ] Pass workflowId to AgentWorkflow component:
  ```typescript
  // In main App.tsx or Dashboard component
  const [workflowId, setWorkflowId] = useState<string | null>(null);

  return (
    <>
      <Section0ParameterGathering onWorkflowStart={setWorkflowId} />
      <Section1AgentWorkflow workflowId={workflowId} />
      {/* ... other sections */}
    </>
  );
  ```

**Validation:**
- Confirming parameters calls POST /api/workflows/forecast
- Workflow ID returned and stored in state
- WebSocket connection automatically established
- Agent cards start updating with real-time messages

---

## Testing Requirements

### Unit Tests
```typescript
describe('WebSocketService', () => {
  it('should connect to WebSocket successfully', () => {
    const ws = new WebSocketService();
    ws.connect('wf_test123');
    expect(ws.isConnected()).toBe(true);
  });

  it('should handle incoming messages', (done) => {
    const ws = new WebSocketService();
    ws.onMessage((message) => {
      expect(message.type).toBe('agent_started');
      done();
    });
    ws.connect('wf_test123');
  });
});

describe('useWebSocket hook', () => {
  it('should update agent state on message', () => {
    const { result } = renderHook(() => useWebSocket('wf_test123'));

    // Simulate WebSocket message
    act(() => {
      // ... trigger message
    });

    expect(result.current.agents[0].status).toBe('running');
  });
});
```

### Integration Tests
```typescript
describe('AgentWorkflow Component', () => {
  it('should display agent cards with real-time updates', async () => {
    render(<AgentWorkflow workflowId="wf_test123" />);

    await waitFor(() => {
      expect(screen.getByText('Demand Agent')).toBeInTheDocument();
      expect(screen.getByText('running')).toBeInTheDocument();
    });
  });

  it('should show workflow complete message', async () => {
    render(<AgentWorkflow workflowId="wf_test123" />);

    await waitFor(() => {
      expect(screen.getByText(/workflow complete/i)).toBeInTheDocument();
    });
  });
});
```

### Manual Testing Checklist
- [ ] Start backend server
- [ ] Start frontend server
- [ ] Enter natural language parameters in Section 0
- [ ] Click "Extract Parameters"
- [ ] Confirm parameters in modal
- [ ] Verify workflow starts (POST /api/workflows/forecast called)
- [ ] Verify WebSocket connects (check console)
- [ ] Verify Demand Agent card shows "running"
- [ ] Verify progress bar updates
- [ ] Verify messages appear in agent card
- [ ] Verify Demand Agent completes (status → "complete")
- [ ] Verify Inventory Agent starts
- [ ] Verify Pricing Agent starts
- [ ] Verify all 3 agents complete
- [ ] Verify "Workflow Complete" message appears
- [ ] Verify connection indicator shows "Connected"
- [ ] Test reconnection (restart backend during workflow)

---

## Implementation Notes

### WebSocket Connection Lifecycle

1. **Connection:**
   - User confirms parameters
   - Frontend calls POST /api/workflows/forecast
   - Backend returns workflow_id
   - Frontend connects to ws://localhost:8000/api/workflows/{id}/stream

2. **Message Flow:**
   - Backend sends agent_started (Demand)
   - Backend sends agent_progress (multiple times)
   - Backend sends agent_completed (Demand)
   - Backend sends agent_started (Inventory)
   - ... repeat for all agents
   - Backend sends workflow_complete

3. **Cleanup:**
   - Workflow completes → WebSocket closes (code 1000)
   - Component unmounts → WebSocket closes
   - Connection error → Auto-reconnect (max 5 attempts)

### Mock Agent Behavior (Backend)

**Critical:** Mock agents MUST adapt to parameters!

**Example: Demand Agent Mock**
```python
# backend/app/agents/demand_agent.py (mock implementation)
def run_demand_forecast_mock(parameters: SeasonParameters):
    # Adapt safety stock based on replenishment strategy
    if parameters.replenishment_strategy == "none":
        safety_stock = 0.25
        reasoning = "No replenishment → increased safety stock 20% → 25%"
    else:
        safety_stock = 0.20
        reasoning = f"{parameters.replenishment_strategy} replenishment → standard 20% safety stock"

    return {
        "total_season_demand": 8000,
        "safety_stock_pct": safety_stock,
        "adaptation_reasoning": reasoning,
        "forecast_horizon_weeks": parameters.forecast_horizon_weeks,
    }
```

---

## Dependencies

**Requires:**
- PHASE4-002 complete (parameter extraction working)
- Backend POST /api/workflows/forecast endpoint functional
- Backend WebSocket server functional
- Mock agents return dynamic data

**Enables:**
- PHASE4-004 (Sections 2-3 can display forecast/allocation data)
- All subsequent sections (need workflow_id)

---

## Definition of Done

- [ ] POST /api/workflows/forecast tested with Postman
- [ ] WebSocket tested with wscat
- [ ] TypeScript types created for all 6 message types
- [ ] WebSocketService created and tested
- [ ] useWebSocket hook created and tested
- [ ] AgentWorkflow component updated with real WebSocket
- [ ] Workflow initiation integrated from Section 0
- [ ] Real-time updates working (agent cards update live)
- [ ] Progress bars animate correctly
- [ ] Status badges update correctly
- [ ] Workflow completion message displays
- [ ] Reconnection works (test with backend restart)
- [ ] All manual tests passing
- [ ] No console errors
- [ ] No memory leaks (WebSocket cleanup on unmount)

---

## Time Tracking

- **Estimated:** 6 hours
- **Actual:** ___ hours
- **Variance:** ___ hours

**Breakdown:**
- Task 1 (Postman workflow endpoint): ___ min
- Task 2 (wscat WebSocket test): ___ min
- Task 3 (TypeScript types): ___ min
- Task 4 (WebSocketService): ___ min
- Task 5 (useWebSocket hook): ___ min
- Task 6 (AgentWorkflow component): ___ min
- Task 7 (Workflow initiation): ___ min
- Testing: ___ min
- Documentation: ___ min

---

## Related Stories

- **Depends On:** PHASE4-002 (Section 0 - Parameter Gathering)
- **Blocks:** PHASE4-004, PHASE4-005, PHASE4-006 (all need workflow_id)
- **Related:** PHASE4-008 (Integration Tests)

---

**Status:** ⏳ Ready for Implementation
**Assigned To:** Dev Team
**Priority:** P0 (Critical - Enables all subsequent sections)
**Created:** 2025-10-29
**Updated:** 2025-10-29
