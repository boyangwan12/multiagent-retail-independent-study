// WebSocket message types for agent workflow real-time updates

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
