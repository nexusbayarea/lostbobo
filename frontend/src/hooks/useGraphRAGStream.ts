import { useState, useEffect, useCallback } from 'react';

export interface StreamChunk {
  id: string;
  text_preview: string;
  score: number;
  hop: number;
}

export interface StreamUpdate {
  type: 'start' | 'seed' | 'chunk' | 'complete' | 'error';
  question_id?: string;
  query?: string;
  chunks?: unknown[];
  chunk?: StreamChunk;
  progress?: number;
  context?: {
    chunk_ids: string[];
    prompt_context: string;
    retrieval_ms: number;
    total_chunks: number;
  };
  message?: string;
}

export function useGraphRAGStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [updates, setUpdates] = useState<StreamUpdate[]>([]);
  const [finalContext, setFinalContext] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  const streamQuery = useCallback(async (questionId: string, query: string, category?: string) => {
    setIsStreaming(true);
    setUpdates([]);
    setFinalContext(null);
    setError(null);

    const url = new URL('/api/graphrag/stream', window.location.origin);
    url.searchParams.set('question_id', questionId);
    url.searchParams.set('query', query);
    if (category) url.searchParams.set('category', category);

    const eventSource = new EventSource(url.toString());

    eventSource.onmessage = (event) => {
      try {
        const update: StreamUpdate = JSON.parse(event.data);
        setUpdates((prev) => [...prev, update]);

        if (update.type === 'complete') {
          setFinalContext(update.context);
          setIsStreaming(false);
          eventSource.close();
        } else if (update.type === 'error') {
          setError(update.message || 'Streaming failed');
          setIsStreaming(false);
          eventSource.close();
        }
      } catch (e) {
        console.error('Failed to parse stream event', e);
      }
    };

    eventSource.onerror = () => {
      setError('Connection lost');
      setIsStreaming(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const reset = useCallback(() => {
    setUpdates([]);
    setFinalContext(null);
    setError(null);
  }, []);

  return { streamQuery, isStreaming, updates, finalContext, error, reset };
}