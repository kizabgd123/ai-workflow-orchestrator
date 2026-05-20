# OmG Hooks System

## Overview
The OmG hooks system provides a role-driven event orchestration layer for the AI Workflow Orchestrator. It ensures deterministic event handling across safety, quality, and optimization lanes.

## Plugin Contract
Runtime adapters must implement the following interface:

### `onHookEvent(event, sdk)`

#### `event` Envelope:
- `event`: The event name (e.g., `agent-start`, `task-complete`).
- `source`: Originating module or agent.
- `session_id`: Unique identifier for the current session.
- `task_id`: Identifier for the specific task being processed.
- `lane`: The execution lane (`P0-safety`, `P1-quality`, `P2-optimization`).
- `subagent`: Name of the subagent involved (if any).
- `termination_reason`: Reason for agent/task termination (if applicable).
- `metadata`: Key-value pairs of additional context.

#### `sdk` Capabilities:
- `log(message)`: Log an event-specific message.
- `state.get(key)`: Retrieve persisted hook state.
- `state.set(key, value)`: Update persisted hook state.
- `bridge`: Optional runtime bridge methods for native tool interaction.

## Guardrails
- **Worker Isolation**: Side-effect hooks are disabled for worker sessions to prevent runaway recursion.
- **Fail-Modes**:
  - `P0-safety`: Fail-closed. Any violation stops execution.
  - `P1-quality`: Fail-open. Logs issues but allows continuation.
  - `P2-optimization`: Fail-open. Optimization failures do not block the critical path.
- **Re-entry Logic**: Blocked continuations must re-validate through the safety lane before reaching quality or optimization lanes.
- **Churn Suppression**: Persisted hook state avoids volatile data (like timestamps) to maintain a clean git history and operator-visible state.
