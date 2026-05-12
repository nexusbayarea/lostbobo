import React from 'react';

export default function DAGExecutionViewer() {
  return (
    <div className="h-full p-4 border rounded-xl bg-card">
      <h2 className="text-xl font-bold mb-4">Live DAG Execution</h2>
      <p className="text-muted-foreground">Interactive graph of currently executing DAG (ReactFlow Integration).</p>
      {/* Integration: Connect to /api/v1/observability/dag/{dag_id} */}
    </div>
  );
}
