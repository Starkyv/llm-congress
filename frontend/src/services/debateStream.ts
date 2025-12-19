import { SSEEvent } from '../types/debate';

/**
 * Stream debate events from the backend via Server-Sent Events
 */
export async function streamDebate(
  topic: string,
  duration: number,
  onEvent: (event: SSEEvent) => void,
  onComplete: () => void,
  onError?: (error: Error) => void
): Promise<() => void> {
  const controller = new AbortController();

  const run = async () => {
    try {
      const response = await fetch(
        `/api/debate/stream?topic=${encodeURIComponent(topic)}&duration=${duration}`,
        { signal: controller.signal }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      const processStream = async (): Promise<void> => {
        const { done, value } = await reader.read();

        if (done) {
          parseSSEBuffer(buffer, onEvent);
          onComplete();
          return;
        }

        buffer += decoder.decode(value, { stream: true });
        buffer = parseSSEBuffer(buffer, onEvent);

        await processStream();
      };

      await processStream();
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        return;
      }
      if (onError) {
        onError(error as Error);
      }
      onComplete();
    }
  };

  run();

  // Return cancel function
  return () => {
    controller.abort();
  };
}

function parseSSEBuffer(
  buffer: string,
  onEvent: (event: SSEEvent) => void
): string {
  const events = buffer.split('\n\n');
  const remaining = events.pop() || '';

  for (const eventBlock of events) {
    if (!eventBlock.trim()) continue;

    const parsed = parseSSEEvent(eventBlock);
    if (parsed) {
      onEvent(parsed);
    }
  }

  return remaining;
}

function parseSSEEvent(eventBlock: string): SSEEvent | null {
  const lines = eventBlock.split('\n');
  let eventType = 'message';
  let data = '';

  for (const line of lines) {
    if (line.startsWith('event:')) {
      eventType = line.slice(6).trim();
    } else if (line.startsWith('data:')) {
      data = line.slice(5).trim();
    } else if (line.startsWith(':')) {
      continue;
    }
  }

  if (!data) return null;

  try {
    return {
      event: eventType,
      data: JSON.parse(data),
    };
  } catch {
    return {
      event: eventType,
      data: data,
    };
  }
}

/**
 * Fetch available agents from the backend
 */
export async function fetchAgents(): Promise<{
  proposition_agents: Array<{ id: string; name: string; personality: string }>;
  opposition: { id: string; name: string; personality: string };
}> {
  const response = await fetch('/api/agents');
  if (!response.ok) {
    throw new Error(`Failed to fetch agents: ${response.status}`);
  }
  return response.json();
}

/**
 * Stop the current debate
 */
export async function stopDebate(): Promise<void> {
  const response = await fetch('/api/debate/stop', { method: 'POST' });
  if (!response.ok) {
    throw new Error(`Failed to stop debate: ${response.status}`);
  }
}

