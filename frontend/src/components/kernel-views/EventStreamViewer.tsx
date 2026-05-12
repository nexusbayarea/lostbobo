import React from 'react';

export default function EventStreamViewer() {
  return (
    <div className="h-full p-4 border rounded-xl bg-card">
      <h2 className="text-xl font-bold mb-4">Kernel Event Stream</h2>
      <div className="h-[600px] overflow-y-auto border p-2 font-mono text-xs bg-black text-green-500 rounded">
        {/* Integration: Connect to WS /api/v1/observability/events */}
        <div className="py-1">System ready...</div>
      </div>
    </div>
  );
}
