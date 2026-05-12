import React, { useState } from 'react';
import { Button } from '@/components/ui/button';

export default function ReplayConsole() {
  const [executionId, setExecutionId] = useState('');
  const [status, setStatus] = useState('');

  const handleReplay = async () => {
    setStatus('Starting replay...');
    // Integration: POST /api/observability/replay { executionId }
  };

  return (
    <div className="h-full p-4 border rounded-xl bg-card">
      <h2 className="text-xl font-bold mb-4">Deterministic Replay Console</h2>
      <div className="flex gap-2 mb-4">
        <input
          className="border px-2 py-1 rounded bg-background"
          placeholder="Execution ID"
          value={executionId}
          onChange={(e) => setExecutionId(e.target.value)}
        />
        <Button onClick={handleReplay}>Execute Replay</Button>
      </div>
      <div className="text-sm text-muted-foreground">{status}</div>
    </div>
  );
}
